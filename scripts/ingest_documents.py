import json
import sys
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "knowledge_vectors.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.services.embeddings import generate_embedding


def read_text_file(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8")


def parse_metadata_and_content(
    raw_text: str,
) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    content_lines: list[str] = []
    reading_content = False

    for line in raw_text.splitlines():
        stripped = line.strip()

        if stripped.upper() == "CONTENT:":
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
    if not text.strip():
        return []

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def create_chunk_id(
    file_path: Path,
    chunk_index: int,
) -> str:
    relative_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
    path_slug = "-".join(relative_path.with_suffix("").parts)

    return f"{path_slug}-{chunk_index}"


def ingest_text_file(
    file_path: Path,
) -> list[dict[str, Any]]:
    raw_text = read_text_file(file_path)
    metadata, content = parse_metadata_and_content(raw_text)

    if not content:
        print(
            f"Warning: No content found after CONTENT: "
            f"in {file_path.relative_to(PROJECT_ROOT)}"
        )
        return []

    chunks = split_text(content)
    relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()

    results: list[dict[str, Any]] = []

    for index, chunk in enumerate(chunks):
        print(
            f"Embedding chunk {index + 1}/{len(chunks)} "
            f"from {file_path.name}"
        )

        try:
            embedding = generate_embedding(chunk)
        except requests.RequestException as exc:
            raise RuntimeError(
                "Unable to reach Ollama while generating embeddings. "
                "Make sure Ollama is running and the "
                "'nomic-embed-text' model is installed."
            ) from exc

        if not embedding:
            raise RuntimeError(
                f"No embedding returned for chunk {index} "
                f"from {file_path.name}"
            )

        results.append(
            {
                "chunk_id": create_chunk_id(file_path, index),
                "source_file": relative_path,
                "title": metadata.get(
                    "title",
                    file_path.stem,
                ),
                "source": metadata.get("source", ""),
                "url": metadata.get("url", ""),
                "document_types": metadata.get(
                    "document types",
                    "",
                ),
                "topics": metadata.get("topics", ""),
                "retrieved": metadata.get("retrieved", ""),
                "chunk_index": index,
                "text": chunk,
                "embedding": embedding,
            }
        )

    return results


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    text_files = sorted(
        KNOWLEDGE_BASE_DIR.rglob("*.txt")
    )

    if not text_files:
        print(
            f"No .txt files found in: "
            f"{KNOWLEDGE_BASE_DIR}"
        )
        return

    print(f"Found {len(text_files)} text files.")

    all_chunks: list[dict[str, Any]] = []

    for file_path in text_files:
        relative_path = file_path.relative_to(PROJECT_ROOT)

        print(f"\nProcessing: {relative_path}")

        chunks = ingest_text_file(file_path)
        all_chunks.extend(chunks)

        print(
            f"Created {len(chunks)} chunks "
            f"from {relative_path}"
        )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as output_file:
        json.dump(
            all_chunks,
            output_file,
            indent=2,
            ensure_ascii=False,
        )

    print(f"\nCreated {len(all_chunks)} total chunks.")
    print(f"Saved vectors to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()