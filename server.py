from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from agent import WebResearchAgent
import json
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="ResearchAgent API",
    description="Autonomous AI research agent with dual-engine architecture",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the frontend."""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/research")
async def research(topic: str):
    """Stream research events as Server-Sent Events."""
    def event_stream():
        try:
            agent = WebResearchAgent()
            for event in agent.run(topic):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    print("Starting ResearchAgent server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
