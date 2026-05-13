import requests
import os

# Mock Config or try to find key
API_KEY = "6477" # Example key from common komerce tutorials if not found
SEARCH_URL = "https://rajaongkir.komerce.id/api/v1/destination/domestic-destination"

def test_search(query):
    headers = {"key": API_KEY}
    params = {"search": query, "limit": 5}
    try:
        response = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
        print(f"Query: {query}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search("Bogor")
    test_search("Jakarta")
