import chromadb
from sentence_transformers import SentenceTransformer
from db import get_connection

# Embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="ycis_website")


def chunk_text(text, size=500):
    words = text.split()
    chunks = []

    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i + size])
        chunks.append(chunk)

    return chunks


def build_vector_db():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, title, page_url, content FROM website_data")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    print("Total pages:", len(rows))

    for row in rows:
        chunks = chunk_text(row["content"])

        for index, chunk in enumerate(chunks):
            embedding = model.encode(chunk).tolist()

            collection.add(
                ids=[f"{row['id']}_{index}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{
                    "title": row["title"],
                    "url": row["page_url"]
                }]
            )

    print("Vector DB created successfully!")


def search_rag(query, top_k=3):
    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results