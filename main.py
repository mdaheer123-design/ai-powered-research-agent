import argparse
import sys
from dotenv import load_dotenv
from agent import WebResearchAgent
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

load_dotenv()

console = Console()


def main():
    parser = argparse.ArgumentParser(description="ResearchAgent — Autonomous AI Research Assistant")
    parser.add_argument("topic", type=str, nargs="?", help="The topic you want to research")
    args = parser.parse_args()

    if not args.topic:
        console.print("[bold yellow]Please enter a topic to research:[/bold yellow]")
        try:
            topic = input("> ")
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)
    else:
        topic = args.topic

    if not topic.strip():
        console.print("[bold red]Topic cannot be empty.[/bold red]")
        sys.exit(1)

    try:
        agent = WebResearchAgent()
        for event in agent.run(topic):
            event_type = event.get("type", "")

            if event_type == "status":
                console.print(f"  [dim]{event['message']}[/dim]")
            elif event_type == "tool_call":
                display = event.get("display", f"Using {event['name']}")
                console.print(f"  [cyan]{display}[/cyan]")
            elif event_type == "error":
                console.print(f"  [red]Error: {event['message']}[/red]")
            elif event_type == "final_report":
                console.print()
                md = Markdown(event["report"])
                console.print(Panel(md, title="Research Report", border_style="green"))

    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")


if __name__ == "__main__":
    main()
