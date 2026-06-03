import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(name, url, params=None):
    print(f"\n--- Testing: {name} ({url}) ---")
    try:
        res = requests.get(f"{BASE_URL}{url}", params=params, timeout=10)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            if "status" in data:
                print(f"Status in response: {data['status']}")
            if "total" in data:
                print(f"Total results: {data['total']}")
            elif "total_items" in data:
                print(f"Total items: {data['total_items']}")
            
            # Print sample result
            if "items" in data and data["items"]:
                print("First item sample:")
                print(json.dumps(data["items"][0], indent=2)[:300] + "...")
            elif "data" in data and isinstance(data["data"], list) and data["data"]:
                print("First data item sample:")
                print(json.dumps(data["data"][0], indent=2)[:300] + "...")
            elif "data" in data and isinstance(data["data"], dict):
                print("Data sample:")
                print(json.dumps(data["data"], indent=2)[:300] + "...")
            else:
                print(f"Response snippet: {json.dumps(data)[:300]}...")
        else:
            print(f"Error Response: {res.text[:300]}")
        return res.json() if res.status_code == 200 else None
    except Exception as e:
        print(f"Connection/Request error: {e}")
        return None

def main():
    # 1. Public list
    res_list = test_endpoint("Public list", "/stok/public/list")
    
    # 2. Public list with query 'cisco'
    test_endpoint("Public list search 'cisco'", "/stok/public/list", {"q": "cisco"})
    
    # 2b. Smart synonym test: 'kamera' (should map to camera, cctv)
    test_endpoint("Smart search for 'kamera' (synonym test)", "/stok/public/list", {"q": "kamera"})
    
    # 2c. Smart specs search test: '5MP' or 'wireless' (should match specs_text)
    test_endpoint("Smart specs search for '5MP'", "/stok/public/list", {"q": "5MP"})
    test_endpoint("Smart specs search for 'wireless'", "/stok/public/list", {"q": "wireless"})
    
    # 2d. Fallback test: 'cisco lan' (no single product matches both, should fall back to OR)
    test_endpoint("Fallback search for 'cisco lan' (strict AND yields 0, loose OR matches both)", "/stok/public/list", {"q": "cisco lan"})
    
    # 3. Autocomplete suggestion
    test_endpoint("Autocomplete for 'cis'", "/stok/public/autocomplete", {"q": "cis"})
    
    # 4. Popular products
    test_endpoint("Popular products", "/stok/public/popular")
    
    # 5. Admin stocks list (with facets)
    test_endpoint("Admin stocks", "/stok/admin/stocks")
    
    # 6. Public brands
    test_endpoint("Public brands", "/stok/public/brands")
    
    # 7. Megamenu collections
    test_endpoint("Megamenu collections", "/stok/public/megamenu-collections")
    
    # 8. Brand showcase
    test_endpoint("Brand showcase", "/stok/public/brand-showcase")
    
    # 9. Similar products/recommendations
    if res_list and "items" in res_list and res_list["items"]:
        sample_uuid = res_list["items"][0]["uuid"]
        test_endpoint(f"Recommendations for uuid {sample_uuid}", f"/stok/public/recommendations/{sample_uuid}")

if __name__ == "__main__":
    main()
