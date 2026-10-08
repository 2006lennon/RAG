import os
import requests

BASE_URL = "http://140.113.241.112:8080"
MODEL = "Gemma4-31B-CK:64k"

api_key = os.environ.get("OPENWEBUI_API_KEY")

if not api_key:
    print("[!] OPENWEBUI_API_KEY is not set.")
    raise SystemExit(1)

url = f"{BASE_URL}/api/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Reply with exactly: TEST_OK"
        }
    ],
    "stream": False,
}

print("[*] Sending request...")
print(f"[*] Model: {MODEL}")

try:
    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=180,
    )

    print(f"[*] HTTP status: {response.status_code}")

    response.raise_for_status()

    data = response.json()

    print("\n--- Raw response ---")
    print(data)

    if "choices" in data:
        answer = data["choices"][0]["message"]["content"]

        print("\n--- Model answer ---")
        print(answer)

except requests.exceptions.Timeout:
    print("\n[!] TIMEOUT: no response within 180 seconds.")

except requests.exceptions.RequestException as exc:
    print(f"\n[!] HTTP/network error: {exc}")

except Exception as exc:
    print(f"\n[!] Unexpected error: {exc}")