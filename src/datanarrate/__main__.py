"""CLI entry-point: python -m datanarrate / datanarrate."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from datanarrate.config import NarrativeConfig, Tone
from datanarrate.core import DataStoryteller

app = typer.Typer(help="DataNarrate — turn datasets into narratives.")
console = Console()


@app.command()
def analyze(
    data: Path = typer.Argument(..., help="Path to a CSV or JSON file"),
    tone: Tone = typer.Option(Tone.FORMAL, "--tone", "-t", help="Narrative tone"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Write Markdown report to file"),
    period_col: Optional[str] = typer.Option(None, "--period", "-p", help="Column for time periods"),
    group_col: Optional[str] = typer.Option(None, "--group", "-g", help="Column for group comparison"),
    title: str = typer.Option("Data Narrative Report", "--title", help="Report title"),
) -> None:
    """Analyze a dataset and generate a narrative report."""
    if not data.exists():
        console.print(f"[red]Error:[/red] File not found: {data}")
        raise typer.Exit(code=1)

    config = NarrativeConfig(tone=tone)
    storyteller = DataStoryteller(config)
    df = storyteller.load(data)

    report = storyteller.generate_report(df, title=title, period_col=period_col, group_col=group_col)

    if output:
        output.write_text(report, encoding="utf-8")
        console.print(f"[green]Report written to {output}[/green]")
    else:
        console.print(Markdown(report))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
