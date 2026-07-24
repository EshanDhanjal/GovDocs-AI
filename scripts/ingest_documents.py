import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "knowledge_chunks.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def parse_metadata_and_content(raw_text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    content_lines: list[str] = []
    reading_content = False

    for line in raw_text.splitlines():
        stripped = line.strip()

        if stripped == "CONTENT:":
            reading_content = True
            continue

        if not reading_content and ":" in stripped:
            key, value = stripped.split(":", 1)
            metadata[key.strip().lower()] = value.strip()
        elif reading_content:
            content_lines.append(line)

    content = "\n".join(content_lines).strip()
    return metadata, content


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    if not text:
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def ingest_text_file(file_path: Path) -> list[dict[str, Any]]:
    raw_text = read_text_file(file_path)
    metadata, content = parse_metadata_and_content(raw_text)
    chunks = split_text(content)

    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    results: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        results.append(
            {
                "chunk_id": f"{file_path.stem}-{index}",
                "source_file": relative_path,
                "title": metadata.get("title", file_path.stem),
                "source": metadata.get("source", ""),
                "url": metadata.get("url", ""),
                "document_types": metadata.get("document types", ""),
                "topics": metadata.get("topics", ""),
                "retrieved": metadata.get("retrieved", ""),
                "chunk_index": index,
                "text": chunk,
            }
        )

    return results


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_chunks: list[dict[str, Any]] = []

    text_files = sorted(KNOWLEDGE_BASE_DIR.rglob("*.txt"))

    if not text_files:
        print("No .txt files found in knowledge_base/")
        return

    print(f"Found {len(text_files)} text files.")

    for file_path in text_files:
        chunks = ingest_text_file(file_path)
        all_chunks.extend(chunks)

        print(
            f"Ingested {file_path.relative_to(PROJECT_ROOT)} "
            f"into {len(chunks)} chunks."
        )

    with OUTPUT_FILE.open("w", encoding="utf-8") as output_file:
        json.dump(all_chunks, output_file, indent=2, ensure_ascii=False)

    print(f"\nCreated {len(all_chunks)} total chunks.")
    print(f"Saved output to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()