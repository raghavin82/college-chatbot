import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "data/vector_db"


def search(query, number_of_results=5):

    #Local embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    #Connecting to ChromaDB
    client = chromadb.PersistentClient(
        path = DB_PATH
    )

    collection = client.get_collection(
        name = "college_syllabus"
    )

    #Convert the question into embedding
    query_embedding = model.encode(query).tolist()

    #Search the vector database
    results = collection.query(
        query_embeddings = [query_embedding],
        n_results = number_of_results
    )

    return results


if __name__ == "__main__":
    query = input("Ask a syllabus question: ")

    results = search(query)

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