import os

os.makedirs("data/chunks", exist_ok=True)

chunk_size = 500

total_chunks = 0

for filename in os.listdir("data/raw"):

    if not filename.endswith(".txt"):
        continue

    filepath = os.path.join("data/raw", filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    source_name = filename.replace(".txt", "")

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size]

        chunk_file = (
            f"data/chunks/{source_name}_chunk_{i//chunk_size + 1}.txt"
        )

        with open(chunk_file, "w", encoding="utf-8") as f:
            f.write(chunk)

        total_chunks += 1

print(f"Total chunks created: {total_chunks}")