import os
from dotenv import load_dotenv
load_dotenv()

from agent import WebResearchAgent

agent = WebResearchAgent()
for event in agent.run("What is the capital of France?"):
    try:
        print(event)
    except UnicodeEncodeError:
        print(str(event).encode("utf-8"))
