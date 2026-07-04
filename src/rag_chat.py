import os
import chromadb
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="chroma_db"
)

collection = client.get_collection(
    "docker_docs"
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

question = input("Ask a question: ")

query_embedding = embedding_model.encode(
    question
).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

context = "\n\n".join(
    results["documents"][0]
)

prompt = f"""
You are a Docker documentation assistant.

Answer using the provided context.

If the answer is partially available across multiple chunks,
combine the information and provide a complete explanation.

If the answer is not present, say so clearly.

Context:
{context}

Question:
{question}

Answer:
"""
print("\nRETRIEVED CONTEXT:\n")
print(context[:5000])
print("\nSources Used:")

for meta in results["metadatas"][0]:
    print("-", meta["source"])

response = model.generate_content(
    prompt
)

print("\nAnswer:\n")
print(response.text)
print("Total documents:", collection.count())