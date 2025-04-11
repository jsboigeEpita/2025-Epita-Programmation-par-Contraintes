import typer
from rich.console import Console
from llm_utils import detect_intent_with_llm, parse_user_request, describe_schedule_with_llm

app = typer.Typer()
console = Console()

@app.command()
def schedule(prompt: str):
    console.print(f"[bold green]Prompt reçu :[/bold green] {prompt}")
    
    intent = detect_intent_with_llm(prompt)
    console.print(f"[cyan]Intent détectée :[/cyan] {intent}")

    if intent != "match_schedule_request":
        console.print("[red]Ce prompt ne correspond pas à une demande de calendrier de match.[/red]")
        raise typer.Exit(code=1)

    infos = parse_user_request(prompt)
    console.print(f"[green]Infos extraites :[/green]\n{infos}")

    # Ici tu devrais appeler ton générateur de calendrier (CP-SAT OR-Tools par ex)
    # Pour le test, on met un faux calendrier
    fake_schedule = [
        {"home": "Équipe A", "away": "Équipe B", "date": "2025-05-01", "stadium": "Stade 1"},
        {"home": "Équipe C", "away": "Équipe D", "date": "2025-05-02", "stadium": "Stade 2"},
    ]
    
    summary = describe_schedule_with_llm(fake_schedule)
    console.print(f"\n[bold magenta]Résumé du calendrier :[/bold magenta]\n{summary}")

if __name__ == "__main__":
    app()
