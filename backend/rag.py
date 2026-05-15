import chromadb
from embeddings import get_embedding

# ✅ Correct persistent DB
client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(name="ycis")


def load_data():
    web_data = ""
    pdf_data = ""

    try:
        with open("../data/website.txt", "r", encoding="utf-8") as f:
            web_data = f.read()
    except:
        print("website.txt not found")

    try:
        with open("../data/pdf.txt", "r", encoding="utf-8") as f:
            pdf_data = f.read()
    except:
        print("pdf.txt not found")

    return web_data + "\n" + pdf_data


def split_text(text, chunk_size=300, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)
        start += (chunk_size - overlap)

    return chunks

def store_embeddings():
    print("Storing embeddings...")

    text = load_data()
    print("Text length:", len(text))

    chunks = split_text(text)
    print("Total chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print("Processing chunk", i)

        emb = get_embedding(chunk)

        collection.add(
            embeddings=[emb],
            documents=[chunk],
            ids=[str(i)],
            metadatas=[{"source": "college_data"}]
        )


    print("Data stored in vector DB!")


def query_rag(query):
    emb = get_embedding(query)

    results = collection.query(
        query_embeddings=[emb],
        n_results=1   # ✅ less noise, better accuracy
    )

    print("Retrieved docs:", results["documents"])

    return results