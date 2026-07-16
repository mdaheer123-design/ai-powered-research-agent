import argparse
from agent import WebResearchAgent
from rich.console import Console
import sys

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Autonomous Web Research Agent")
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
        agent.run(topic)
    except Exception as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")

if __name__ == "__main__":
    main()
