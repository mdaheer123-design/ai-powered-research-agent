import os
import json
import urllib.request
import urllib.error

def test_groq_models(api_key):
    print("Testing Groq API...")
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            models = [m["id"] for m in data.get("data", [])]
            print("\nSUCCESS! Here are the models you actually have access to:")
            for m in sorted(models):
                print(f"  - {m}")
            return models
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode())
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    key = input("Please paste your GROQ_API_KEY to test available models: ").strip()
    if key:
        test_groq_models(key)
    else:
        print("No API key provided.")

