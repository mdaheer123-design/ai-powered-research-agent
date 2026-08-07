import json
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS
import requests
from bs4 import BeautifulSoup

def search_web(query: str) -> str:
    """
    Searches the web for a given query and returns a list of snippets with their URLs.
    
    Args:
        query: The search query string.
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            if not results:
                return json.dumps({"error": "No results found."})
            
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                })
            return json.dumps(formatted_results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

def read_webpage(url: str) -> str:
    """
    Reads the content of a web page and returns the extracted text.
    Use this after finding a relevant URL via search_web.
    
    Args:
        url: The URL of the web page to read.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove non-content elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.extract()
            
        text = soup.get_text(separator="\n", strip=True)
        
        # Truncate to avoid token limits
        if len(text) > 15000:
            text = text[:15000] + "\n... [Content Truncated]"
            
        return text
    except Exception as e:
        return json.dumps({"error": str(e)})

def calculator(expression: str) -> str:
    """
    Evaluates a basic arithmetic expression.
    
    Args:
        expression: The mathematical expression to evaluate (e.g., '2 + 2', '100 * (45 / 5)').
    """
    try:
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names, {})
        return str(result)
    except Exception as e:
        return json.dumps({"error": f"Invalid expression: {str(e)}"})

# List of tools to pass to the GenAI SDK
TOOLS = [search_web, read_webpage, calculator]
