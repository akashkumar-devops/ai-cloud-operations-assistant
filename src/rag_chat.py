"""
Filename: rag_chat.py

Purpose
-------
Terminal interface for the AI Cloud Operations Assistant.
"""

from src.rag_engine import answer_question


def main():

    print("=" * 60)
    print("AI Cloud Operations Assistant")
    print("=" * 60)

    while True:

        question = input("\nAsk a question (type 'exit' to quit): ").strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        if not question:
            continue

        print("\nGenerating answer...\n")

        result = answer_question(question)

        print("=" * 60)
        print("Assistant")
        print("=" * 60)
        print(result["answer"])

        print("\nSources")
        print("-" * 60)

        for source in result["sources"]:
            print(
                f"{source['technology']} | "
                f"{source['document']} | "
                f"Chunk {source['chunk_id']}"
            )

        print("\nRetrieved Chunks :", result["retrieved_chunks"])


if __name__ == "__main__":
    main()
