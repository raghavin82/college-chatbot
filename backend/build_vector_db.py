import json
from pyexpat import model
import chromadb
from sentence_transformers import SentenceTransformer

JSON_PATH = "data/processed/chunks.json"
DB_PATH = "data/vector_db"

def local_chunks():
    with open(JSON_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def build_database():
    print("Loading chunks...")

    chunks = local_chunks()

    print(f"Number of chunks: {len(chunks)}")

    print("\nLoading embedding model...")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path = DB_PATH
        )

    # Remove the old collection if it exists
    try:
        client.delete_collection(
            name="college_syllabus"
        )
        print("Old collection deleted.")
    except Exception:
        print("No old collection found.")

    # Create a fresh collection
    collection = client.create_collection(
        name="college_syllabus"
    )

    #Remove previous test data
    try:
        collection.delete(ids=["test_1"])
    except:
        pass

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        ids.append(str(chunk["id"]))

        # Add context to the text being embedded
        document = (
            f"Subject Code: {chunk['course_code']}. "
            f"Subject: {chunk['course_name']}. "
            f"Module: {chunk['module']}. "
            f"Topic: {chunk['topic']}"
        )

        documents.append(document)

        metadatas.append({
            "course_code": chunk["course_code"],
            "course_name": chunk["course_name"],
            "module": chunk["module"],
            "topic": chunk["topic"]
        })
    print("\nGenerating Embedding...")

    embedding = model.encode(
        documents, 
        show_progress_bar=True
    )

    print("\nAdding chunks to ChromaDB...")

    collection.add(
        ids = ids,
        documents = documents,
        embeddings = embedding.tolist(), 
        metadatas = metadatas,
    )

    print("\nDatabase built successfully!")
    print("Documents in database:", collection.count())


if __name__ == "__main__":
    build_database()