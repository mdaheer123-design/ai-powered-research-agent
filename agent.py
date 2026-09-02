import os
import re
import json
import traceback
from groq import Groq
from google import genai
from google.genai import types
from tools import search_web, read_webpage, calculator

VALID_TOOLS = {"search_web", "read_webpage", "calculator"}

TOOL_FUNCTIONS = {
    "search_web": search_web,
    "read_webpage": read_webpage,
    "calculator": calculator,
}


def _parse_tool_call(content: str):
    """
    Parse a tool call from LLM output.  Handles three known formats:

    1. Plain JSON:    {"tool": "search_web", "args": {"query": "..."}}
    2. Fenced JSON:   ```json\n{"tool": ...}\n```
    3. Groq XML:      <function=search_web{"query": "..."}></function>
                   or <function=search_web>{"query": "..."}</function>

    Returns (tool_name, args_dict) on success, or None on failure.
    """
    if not content or not content.strip():
        return None

    text = content.strip()

    # ── Format 3: Groq XML  <function=name{...}</function>  ──────────────
    # Variant A:  <function=search_web{"query":"capital of France"}></function>
    # Variant B:  <function=search_web>{"query":"capital of France"}</function>
    xml_match = (
        re.search(r'<function=(\w+)\s*(\{[^}]*\})\s*>?\s*</function>', text, re.DOTALL)
        or re.search(r'<function=(\w+)>\s*(\{[^}]*\})\s*</function>', text, re.DOTALL)
    )
    if xml_match:
        name = xml_match.group(1)
        try:
            args = json.loads(xml_match.group(2))
            if name in VALID_TOOLS:
                return (name, args)
        except json.JSONDecodeError:
            pass

    # ── Format 2: Fenced JSON  ```json ... ```  ──────────────────────────
    fence_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if fence_match:
        try:
            data = json.loads(fence_match.group(1))
            name = data.get("tool")
            args = data.get("args", {})
            if name in VALID_TOOLS:
                return (name, args)
        except (json.JSONDecodeError, AttributeError):
            pass

    # ── Format 1: Plain JSON object  ─────────────────────────────────────
    # Find the first top-level { ... } in the text
    brace_match = re.search(r'\{.*\}', text, re.DOTALL)
    if brace_match:
        try:
            data = json.loads(brace_match.group(0))
            name = data.get("tool")
            args = data.get("args", {})
            if name in VALID_TOOLS:
                return (name, args)
        except (json.JSONDecodeError, AttributeError):
            pass

    return None


def _execute_tool(name: str, args: dict) -> str:
    """Execute a tool by name and return the result string."""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        return fn(**args)
    except Exception as e:
        return json.dumps({"error": str(e)})


def _safe_encode(text: str) -> str:
    """Encode text safely for Windows console output."""
    return text.encode("utf-8", errors="replace").decode("utf-8")


class WebResearchAgent:
    def __init__(self):
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")

        from datetime import datetime, timezone
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        self.system_instruction = (
            f"You are ResearchAgent, an autonomous research assistant.\n"
            f"Today's date is {current_date} (UTC).\n\n"
            f"Your job is to answer the user's research question comprehensively.\n"
            f"You have access to these tools: search_web, read_webpage, calculator.\n\n"
            f"RULES:\n"
            f"1. Use tools to gather facts. Only assert facts you have verified.\n"
            f"2. Do not explain your reasoning before calling a tool — just call it.\n"
            f"3. Once you have enough information, write a detailed Markdown report "
            f"with inline citations [Source](URL).\n"
            f"4. If sources conflict, note the discrepancy explicitly.\n"
            f"5. If the user just says a simple greeting (like 'hi' or 'hello') or asks a conversational question that doesn't require research, just reply politely and ask what they would like to research today. Do NOT use tools for simple greetings.\n"
        )

        # Groq-specific instruction for manual JSON tool calling
        self.groq_tool_instruction = (
            "\n\nIMPORTANT — TOOL CALLING FORMAT:\n"
            "When you need to use a tool, output ONLY a single JSON object "
            "on its own line, nothing else:\n"
            '{"tool": "tool_name", "args": {"param": "value"}}\n\n'
            "Available tools:\n"
            '- {"tool": "search_web", "args": {"query": "your search query"}}\n'
            '- {"tool": "read_webpage", "args": {"url": "https://example.com"}}\n'
            '- {"tool": "calculator", "args": {"expression": "2 + 2"}}\n\n'
            "When you are done researching and ready to present findings, "
            "write the full Markdown report directly (no JSON wrapper).\n"
        )

        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Searches the web for a given query and returns a list of snippets with their URLs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query string"}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_webpage",
                    "description": "Reads the content of a web page and returns the extracted text.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL of the web page to read."}
                        },
                        "required": ["url"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "calculator",
                    "description": "Evaluates a basic arithmetic expression.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string", "description": "The mathematical expression to evaluate."}
                        },
                        "required": ["expression"],
                    },
                },
            },
        ]

    # ── Public entry point ───────────────────────────────────────────────
    def run(self, query: str):
        """Run the research agent.  Yields SSE-style event dicts."""
        if self.groq_api_key:
            try:
                yield from self._run_groq(query)
                return  # success — done
            except Exception as e:
                err_msg = _safe_encode(str(e))
                yield {"type": "error", "message": f"Groq engine error: {err_msg}"}
                yield {"type": "status", "message": "Switching to backup engine (Gemini)..."}

        # Fallback to Gemini
        if self.gemini_api_key:
            try:
                yield from self._run_gemini(query)
                return
            except Exception as e:
                err_msg = _safe_encode(str(e))
                yield {"type": "error", "message": f"Gemini engine error: {err_msg}"}
        else:
            yield {"type": "error", "message": "No API keys configured. Please set GROQ_API_KEY or GEMINI_API_KEY."}

    # ── Groq engine (manual JSON tool calling) ───────────────────────────
    def _run_groq(self, query: str):
        yield {"type": "status", "message": f"Researching: {query}"}
        yield {"type": "status", "message": "Connected to Groq (GPT-OSS 120B)"}

        client = Groq(api_key=self.groq_api_key)

        messages = [
            {"role": "system", "content": self.system_instruction + self.groq_tool_instruction},
            {"role": "user", "content": query},
        ]

        for iteration in range(15):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.3,
            )

            content = response.choices[0].message.content or ""
            messages.append({"role": "assistant", "content": content})

            # Try to parse a tool call from the response
            parsed = _parse_tool_call(content)

            if parsed is not None:
                name, args = parsed

                # Descriptive status for the UI
                if name == "search_web":
                    yield {"type": "tool_call", "name": name, "args": args,
                           "display": f"Searching: \"{args.get('query', '')}\""}
                elif name == "read_webpage":
                    url = args.get("url", "")
                    short_url = url[:60] + "..." if len(url) > 60 else url
                    yield {"type": "tool_call", "name": name, "args": args,
                           "display": f"Reading: {short_url}"}
                elif name == "calculator":
                    yield {"type": "tool_call", "name": name, "args": args,
                           "display": f"Calculating: {args.get('expression', '')}"}

                result_str = _execute_tool(name, args)
                messages.append({
                    "role": "user",
                    "content": f"Tool result for {name}:\n{result_str}",
                })
                yield {"type": "status", "message": "Analyzing results..."}
            else:
                # No tool call found — this is the final report text
                if content.strip():
                    yield {"type": "final_report", "report": content}
                else:
                    yield {"type": "final_report", "report": "The agent returned an empty response. Please try again."}
                return

        yield {"type": "final_report", "report": "Research reached the iteration limit. Please try a more specific query."}

    # ── Gemini engine (native function calling) ──────────────────────────
    def _run_gemini(self, query: str):
        yield {"type": "status", "message": f"Researching: {query}"}
        yield {"type": "status", "message": "Connected to Gemini (3.6 Flash)"}

        if not self.gemini_api_key:
            yield {"type": "error", "message": "No Gemini API key available."}
            return

        client = genai.Client(api_key=self.gemini_api_key)
        config = types.GenerateContentConfig(
            system_instruction=self.system_instruction,
            tools=[search_web, read_webpage, calculator],
            temperature=0.3,
        )
        chat = client.chats.create(model="gemini-3.6-flash", config=config)

        try:
            response = chat.send_message(query)

            for _ in range(15):
                # Extract function calls from the response
                function_calls = getattr(response, "function_calls", []) or []
                if not function_calls and response.candidates and response.candidates[0].content:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            function_calls.append(part.function_call)

                if function_calls:
                    parts_to_send = []
                    for fc in function_calls:
                        name = fc.name
                        args = dict(fc.args) if fc.args else {}

                        if name == "search_web":
                            yield {"type": "tool_call", "name": name, "args": args,
                                   "display": f"Searching: \"{args.get('query', '')}\""}
                        elif name == "read_webpage":
                            url = args.get("url", "")
                            short_url = url[:60] + "..." if len(url) > 60 else url
                            yield {"type": "tool_call", "name": name, "args": args,
                                   "display": f"Reading: {short_url}"}
                        elif name == "calculator":
                            yield {"type": "tool_call", "name": name, "args": args,
                                   "display": f"Calculating: {args.get('expression', '')}"}

                        result_str = _execute_tool(name, args)
                        parts_to_send.append(
                            types.Part.from_function_response(name=name, response={"result": result_str})
                        )

                    yield {"type": "status", "message": "Analyzing results..."}
                    response = chat.send_message(parts_to_send)
                else:
                    yield {"type": "final_report", "report": response.text}
                    return

            yield {"type": "final_report", "report": "Research reached the iteration limit. Please try a more specific query."}

        except Exception as e:
            raise  # Re-raise so the caller in run() can handle fallback
