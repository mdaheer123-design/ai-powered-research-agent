import os
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"] = "invalid_key_to_force_fallback"

from agent import WebResearchAgent

agent = WebResearchAgent()
for event in agent.run("Calculate 5 * 10"):
    try:
        print(event)
    except UnicodeEncodeError:
        print(str(event).encode("utf-8"))
