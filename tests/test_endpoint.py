"""
Endpoint / model discovery — find which model names work with your API endpoint.
Run: python -m tests.test_endpoint
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import anthropic
import config

MODEL_CANDIDATES = [
    "claude-3-5-sonnet",
    "claude-3-sonnet",
    "claude-sonnet-3-5",
    "claude-3-opus",
    "claude-opus-3",
    "claude-3-haiku",
    "claude-sonnet",
    "claude-3.5-sonnet",
]


def _make_client():
    kwargs = {"api_key": config.ANTHROPIC_API_KEY}
    if config.ANTHROPIC_BASE_URL:
        kwargs["base_url"] = config.ANTHROPIC_BASE_URL
    return anthropic.Anthropic(**kwargs)


def test_without_model():
    """Try calling the endpoint with an empty model string and without a model param."""
    print("\n--- Test: call without model parameter ---")
    client = _make_client()

    # 1) Empty string via SDK
    try:
        resp = client.messages.create(
            model="",
            max_tokens=20,
            messages=[{"role": "user", "content": "Hello, respond with just 'Hi'"}],
        )
        print(f"[OK] Empty model string works! Response: {resp.content[0].text}")
        return True
    except Exception as e:
        print(f"[X] Empty model string failed: {str(e)[:100]}")

    # 2) Raw request without model key
    try:
        import requests

        headers = {
            "x-api-key": config.ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        data = {"max_tokens": 20, "messages": [{"role": "user", "content": "Hi"}]}
        resp = requests.post(
            f"{config.ANTHROPIC_BASE_URL}v1/messages", headers=headers, json=data
        )
        print(f"  Status {resp.status_code}: {resp.text[:200]}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[X] No-model request failed: {str(e)[:100]}")
        return False


def test_model_candidates():
    """Try each candidate model name and report which ones work."""
    print("\n--- Test: model name candidates ---")
    print(f"Endpoint: {config.ANTHROPIC_BASE_URL or '(default)'}")
    print(f"Testing {len(MODEL_CANDIDATES)} names...\n")

    client = _make_client()
    working = []

    for name in MODEL_CANDIDATES:
        print(f"  {name}...", end=" ")
        try:
            resp = client.messages.create(
                model=name,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}],
            )
            print("[OK]")
            working.append(name)
        except anthropic.BadRequestError as e:
            msg = str(e).lower()
            if "model" in msg or "deployment" in msg:
                print("[X] not available")
            else:
                print(f"[?] {str(e)[:50]}")
        except Exception as e:
            print(f"[!] {str(e)[:50]}")

    if working:
        print(f"\nWorking models: {', '.join(working)}")
        print(f"Recommended: set ANTHROPIC_MODEL={working[0]}")
    else:
        print("\nNo working model found. Check with your admin for the correct model identifier.")

    return bool(working)


def main():
    print("=" * 60)
    print("Stock Recommendation Agent — Endpoint Discovery")
    print("=" * 60)

    test_without_model()
    test_model_candidates()


if __name__ == "__main__":
    main()
