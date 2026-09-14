import re
import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "data/vector_db"


def extract_module_number(query):

    match = re.search(
        r"\bmodule\s+([1-5])\b",
        query.lower()
    )

    if match:
        return int(match.group(1))

    return None


def extract_course_code(query):

    query = query.lower()

    # Check whether the user is asking about a lab
    is_lab = bool(re.search(r"\blab\b", query))

    # Data Structure & Algorithm
    if "data structure" in query or re.search(r"\bdsa\b", query):
        if is_lab:
            return "CL02(P)"
        return "CL02"

    # Artificial Intelligence
    if "artificial intelligence" in query or re.search(r"\bai\b", query):
        if is_lab:
            return "CL04(P)"
        return "CL04"

    # Object Oriented Programming
    if "object oriented" in query or re.search(r"\boop\b", query):
        if is_lab:
            return "CL03(P)"
        return "CL03"

    # Computer Organization & Architecture
    if (
        "computer organization" in query
        or "computer system organization" in query
        or re.search(r"\bcoa\b", query)
    ):
        if is_lab:
            return "CL01(P)"
        return "CL01"

    # Python
    if "python" in query:
        return "CL05(P)"

    return None


def extract_query_intent(query):

    query = query.lower()

    #Module-specific question
    if re.search(r"\bmodule\s+[1-5]\b", query):
        return "module_topics"

    #course overview question
    if(
        "what topics are covered" in query
        or "topics covered" in query
        or "topics in" in query
        or "syllabus of" in query
        or "syllabus for" in query
    ):
        return "course_overview"

    #Topic/location search
    if(
        "where is" in query
        or "where are" in query 
        or "which module" in query 
        or "covered in the syllabus" in query 
        or "does" in query and "have" in query 
    ):
        return "topic_search"

    #General question
    return "general_question"


def filter_by_relevance(results, threshold=1.2):

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    filtered_documents = []
    filtered_metadatas = []
    filtered_distances = []

    for i in range(len(documents)):

        distance = distances[i]

        #Course overview results use None as distance
        if distance is None or distance <= threshold:

            filtered_documents.append(
                documents[i]
            )

            filtered_metadatas.append(
                metadatas[i]
            )

            filtered_distances.append(
                distance
            )

    return {
        "documents": [filtered_documents],
        "metadatas": [filtered_metadatas],
        "distances": [filtered_distances]
    }


def get_result_count(intent):

    if intent == "course_overview":
        return 100

    if intent == "module_topics":
        return 20

    if intent == "topic_search":
        return 20

    if intent == "general_question":
        return 10

    return 10


def search(query):

    # Detect course, module, and intent
    course_code = extract_course_code(query)
    module_number = extract_module_number(query)
    intent = extract_query_intent(query)

    #Determine retrieval size based on intent
    number_of_results = get_result_count(intent)

    print("Detected course:", course_code)
    print("Detected module:", module_number)
    print("Detected intent:", intent)
    print("Number of results:", number_of_results)

    # Load embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Connect to ChromaDB
    client = chromadb.PersistentClient(
        path=DB_PATH
    )

    collection = client.get_collection(
        name="college_syllabus"
    )

    # Convert question into embedding
    query_embedding = model.encode(query).tolist()

    # --------------------------------------------------
    # 1. MODULE TOPICS
    # --------------------------------------------------

    if intent == "module_topics" and course_code and module_number:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=number_of_results,
            where={
                "$and": [
                    {"course_code": course_code},
                    {"module": module_number}
                ]
            }
        )

    # --------------------------------------------------
    # 2. COURSE OVERVIEW
    # --------------------------------------------------

    elif intent == "course_overview" and course_code:

        results = collection.get(
            where={
                "course_code": course_code
            }
        )

        return {
            "documents": [results["documents"]],
            "metadatas": [results["metadatas"]],
            "distances": [[None] * len(results["documents"])]
        }

    # --------------------------------------------------
    # 3. TOPIC SEARCH
    # --------------------------------------------------

    elif intent == "topic_search":

        if course_code:

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=number_of_results,
                where={
                    "course_code": course_code
                }
            )

        else:

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=number_of_results
            )

    # --------------------------------------------------
    # 4. GENERAL QUESTION
    # --------------------------------------------------

    else:

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=number_of_results
        )

    #Apply relevance filtering only to 
    #semantic/topic-based searches.
    if intent in ["topic_search", "general_question"]:

        results = filter_by_relevance(
            results,
            threshold = 1.0
        )

    return results


if __name__ == "__main__":

    query = input("Ask a syllabus question: ")

    results = search(query)

    if not results["documents"][0]:
        print("\nNo relevant syllabus information found.")

    else:
        print("\nRelevant Syllabus Topics:\n")

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(documents)):
        
            print(f"Result {i+1}")
            print("Subject Code:", metadatas[i]["course_code"])
            print("Subject:", metadatas[i]["course_name"])
            print("Module:", metadatas[i]["module"])
            print("Topic:", metadatas[i]["topic"])
            print("Distance:", distances[i])
            print()
