import chromadb  # type: ignore[import]
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_collection("docker_docs")

question = input("Ask a question: ")

query_embedding = model.encode(question).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=10,
    include=["documents", "metadatas", "distances"]
)
for i in range(10):
    print("\n----")
    print(results["documents"][0][i][:300])
print(results.keys())

print("\nTop Results:\n")
print("Total documents:", collection.count())
for i in range(len(results["documents"][0])):

    print(f"\nResult {i+1}")
    print("-" * 50)

    print(
        "Source:",
        results["metadatas"][0][i]["source"]
    )
    print("Distance:", results["distances"][0][i])
    print()

    print(results["documents"][0][i][:700])
    