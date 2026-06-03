import asyncio
import httpx

async def test():
    api_key = "***REMOVED***"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [
            {"role": "user", "content": "Please briefly explain the importance of fast AI inference."}
        ]
    }
    url = "https://api.groq.com/openai/v1/chat/completions"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status Code: {resp.status_code}")
            print(resp.text)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
