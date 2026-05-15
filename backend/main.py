from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

from db import search_database
from vector_store import search_rag

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "mistral"
cache = {}


@app.get("/chat")
def chat(query: str):
    try:
        key = query.lower().strip()

        if key in cache:
            return cache[key]

        context = ""
        sources = []

        # 1. Search structured MySQL data first
        rows = search_database(query)

        if rows:
            for row in rows:
                context += f"{row['title']}:\n{row['content']}\n\n"
                sources.append({
                    "title": row["title"],
                    "content": row["content"]
                })

        # 2. If MySQL structured data not found, use RAG
        else:
            rag_results = search_rag(query)

            docs = rag_results.get("documents", [[]])[0]
            metas = rag_results.get("metadatas", [[]])[0]

            for doc in docs:
                context += doc + "\n\n"

            for meta in metas:
                sources.append({
                    "title": meta.get("title", "Website Page"),
                    "content": meta.get("url", "")
                })

        if not context.strip():
            return {
                "answer": "No data found",
                "source": []
            }

        prompt = f"""
You are YCIS College AI Assistant.

Answer ONLY from the context below.

Strict Rules:
- Do NOT guess
- Do NOT assume related departments
- Do NOT say "could be related"
- If exact information is not present in context, reply only: No data found
- Keep answer short and clear

Context:
{context}

Question:
{query}

Answer:
"""

        response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,

        "options": {
            "temperature": 0.0,
            "num_predict": 120
        }
    },
    timeout=40
)

        data = response.json()
        answer = data.get("response", "").strip()

        if not answer:
            answer = "No data found"

        result = {
            "answer": answer,
            "source": sources
        }

        cache[key] = result
        return result

    except Exception as e:
        return {"error": str(e)}