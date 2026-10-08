from pathlib import Path
import os
import re
import requests


# ============================================================
# Configuration
# ============================================================

DOCS_DIR = Path("docs")
GENERATED_DIR = Path("generated")
LOGS_DIR = Path("logs")

CHUNK_SIZE = 700
TOP_K = 3

OPENWEBUI_BASE_URL = "http://140.113.241.112:8080"
MODEL = "Gemma4-31B-CK:64k"


# ============================================================
# Safety policy
# ============================================================

BLOCKED_TERMS = (
    "passwordset",
    "trustpasswordset",
    "secretsdump",
    "ntds.dit",
    "credential dump",
    "remote command",
    "execute exploit",
    "scan network",
)


def unsafe(text):
    lowered = text.lower()

    for blocked in BLOCKED_TERMS:
        if blocked in lowered:
            return blocked

    return None


# ============================================================
# Document loading
# ============================================================

def load_documents():
    documents = []

    if not DOCS_DIR.exists():
        print("[!] docs directory does not exist.")
        return documents

    for path in DOCS_DIR.glob("*.txt"):
        try:
            text = path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            documents.append(
                {
                    "source": path.name,
                    "text": text,
                }
            )

        except Exception as exc:
            print(f"[!] Failed to read {path}: {exc}")

    return documents


# ============================================================
# Line-aware chunking
# ============================================================

def chunks(text, chunk_size=CHUNK_SIZE):
    lines = text.splitlines()

    result = []
    buffer = []
    current_size = 0

    for line in lines:
        line_size = len(line) + 1

        if buffer and current_size + line_size > chunk_size:
            result.append("\n".join(buffer))

            buffer = []
            current_size = 0

        buffer.append(line)
        current_size += line_size

    if buffer:
        result.append("\n".join(buffer))

    return result


# ============================================================
# Tokenization
# ============================================================

def terms(text):
    return set(
        re.findall(
            r"[A-Za-z_][A-Za-z0-9_]*|[\u4e00-\u9fff]+|\d+",
            text.lower(),
        )
    )


# ============================================================
# Build local chunk database
# ============================================================

def build_chunks(documents):
    database = []

    for doc in documents:
        for index, chunk in enumerate(chunks(doc["text"])):
            database.append(
                {
                    "source": doc["source"],
                    "index": index,
                    "text": chunk,
                    "terms": terms(chunk),
                }
            )

    return database


# ============================================================
# Retrieval
# ============================================================

def retrieve(query, database, top_k=TOP_K):
    query_terms = terms(query)

    scored = []

    for item in database:
        overlap = query_terms & item["terms"]

        score = len(overlap)

        if score > 0:
            scored.append(
                (
                    score,
                    item,
                )
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True,
    )

    return [
        item
        for _, item in scored[:top_k]
    ]


# ============================================================
# Context rendering
# ============================================================

def build_context(results):
    if not results:
        return "NEED_MORE_CONTEXT"

    output = []

    for number, item in enumerate(results, start=1):
        output.append(
            f"[Context {number}]"
        )

        output.append(
            f"Source: {item['source']}"
        )

        output.append(
            f"Chunk: {item['index']}"
        )

        output.append("")

        output.append(
            item["text"]
        )

        output.append("")

    return "\n".join(output)


# ============================================================
# Open WebUI request
# ============================================================

def ask_llm(question, context):
    api_key = os.environ.get(
        "OPENWEBUI_API_KEY"
    )

    if not api_key:
        raise RuntimeError(
            "OPENWEBUI_API_KEY is not set."
        )

    url = (
        f"{OPENWEBUI_BASE_URL}"
        "/api/chat/completions"
    )

    headers = {
        "Authorization": (
            f"Bearer {api_key}"
        ),
        "Content-Type": "application/json",
    }

    system_prompt = """
You are assisting with an academic defensive-security research project
about CVE-2020-1472 (Zerologon).

You must use only the provided retrieved context.

Allowed tasks:
- explain vulnerability concepts
- explain protocol structures
- explain API names and parameters
- summarize documentation
- compare retrieved information
- identify missing context

Do not:
- provide executable exploitation code
- provide credential dumping instructions
- provide password-changing procedures
- provide remote command execution instructions
- provide attack automation
- invent undocumented APIs

If the retrieved context is insufficient, answer exactly:
NEED_MORE_CONTEXT

Keep the answer concise and technical.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved Context:
{context}
""".strip()

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "stream": False,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["choices"][0]
        ["message"]["content"]
    )


# ============================================================
# Save result
# ============================================================

def save_result(question, context, answer):
    GENERATED_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        GENERATED_DIR
        / "zerologon_rag_answer.md"
    )

    content = f"""# Zerologon RAG Result

## Question

{question}

## Retrieved Context

{context}

## LLM Answer

{answer}
"""

    output_path.write_text(
        content,
        encoding="utf-8",
    )

    return output_path


# ============================================================
# Main
# ============================================================

def main():
    print(
        "[*] Zerologon safe RAG + LLM"
    )

    print(
        "[*] Loading local documents..."
    )

    documents = load_documents()

    if not documents:
        print(
            "[!] No .txt files found in ./docs"
        )
        return

    database = build_chunks(
        documents
    )

    print(
        f"[*] Loaded {len(documents)} documents"
    )

    print(
        f"[*] Created {len(database)} chunks"
    )

    question = input(
        "\nQuestion: "
    ).strip()

    if not question:
        print(
            "[!] Empty question."
        )
        return

    blocked = unsafe(question)

    if blocked:
        print(
            f"\nPOLICY_BLOCKED: {blocked}"
        )
        return

    results = retrieve(
        question,
        database,
    )

    context = build_context(
        results
    )

    blocked = unsafe(context)

    if blocked:
        print(
            f"\nPOLICY_BLOCKED: {blocked}"
        )
        return

    print(
        "\n[*] Retrieval complete."
    )

    print(
        "[*] Sending retrieved context "
        "to Open WebUI..."
    )

    try:
        answer = ask_llm(
            question,
            context,
        )

    except requests.exceptions.Timeout:
        print(
            "\n[!] TIMEOUT: model did not "
            "respond within 180 seconds."
        )
        return

    except requests.exceptions.RequestException as exc:
        print(
            f"\n[!] HTTP/network error: {exc}"
        )
        return

    except Exception as exc:
        print(
            f"\n[!] Error: {exc}"
        )
        return

    blocked = unsafe(answer)

    if blocked:
        print(
            "\n[!] Generated answer was blocked "
            "by the local safety filter."
        )
        return

    output_path = save_result(
        question,
        context,
        answer,
    )

    print(
        "\n--- LLM Answer ---\n"
    )

    print(answer)

    print(
        f"\n[*] Saved to: {output_path}"
    )

    print(
        "\n[*] Safety mode: no Impacket, "
        "no DC connection, no code execution."
    )


if __name__ == "__main__":
    main()