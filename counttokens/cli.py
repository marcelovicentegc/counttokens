import os
import sys
import json
import click
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import box
import pandas as pd
from .core import TokenCounter

console = Console()

@click.group()
@click.version_option('0.1.0')
def main():
    """
    CountTokens - A CLI tool for counting tokens in text datasets using tiktoken.
    
    This tool helps you analyze the number of tokens in text, files, or entire directories.
    """
    pass


@main.command()
@click.argument('text', type=str)
@click.option('--model', '-m', type=str, default='gpt-3.5-turbo',
              help='The model to use for token counting (e.g., gpt-3.5-turbo, gpt-4).')
def text(text: str, model: str):
    """Count tokens in a provided text string."""
    counter = TokenCounter(model=model)
    token_count = counter.count_tokens(text)
    
    table = Table(title=f"Token Count ({model})", box=box.ROUNDED)
    table.add_column("Text Preview", style="cyan")
    table.add_column("Characters", style="magenta")
    table.add_column("Tokens", style="green")
    
    # Create a preview of the text
    preview = text[:50] + "..." if len(text) > 50 else text
    
    table.add_row(preview, str(len(text)), str(token_count))
    console.print(table)


@main.command()
@click.argument('file_path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--model', '-m', type=str, default='gpt-3.5-turbo',
              help='The model to use for token counting (e.g., gpt-3.5-turbo, gpt-4).')
@click.option('--output', '-o', type=click.Path(), help='Path to save output as JSON or CSV.')
def file(file_path: str, model: str, output: Optional[str]):
    """Count tokens in a file."""
    counter = TokenCounter(model=model)
    
    with console.status(f"[bold green]Counting tokens in {file_path}...", spinner="dots"):
        result = counter.count_file_tokens(file_path)
    
    _display_result(result, output)


@main.command()
@click.argument('directory_path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--model', '-m', type=str, default='gpt-3.5-turbo',
              help='The model to use for token counting (e.g., gpt-3.5-turbo, gpt-4).')
@click.option('--extensions', '-e', multiple=True, help='File extensions to process (e.g., -e txt -e json).')
@click.option('--recursive/--no-recursive', default=True, help='Whether to search subdirectories recursively.')
@click.option('--output', '-o', type=click.Path(), help='Path to save output as JSON or CSV.')
def directory(directory_path: str, model: str, extensions: List[str], recursive: bool, output: Optional[str]):
    """Count tokens in all files within a directory."""
    counter = TokenCounter(model=model)
    
    console.print(f"[bold]Counting tokens in directory: [cyan]{directory_path}[/cyan][/bold]")
    console.print(f"Model: [magenta]{model}[/magenta]")
    console.print(f"Extensions: [yellow]{', '.join(extensions) if extensions else 'all supported'}[/yellow]")
    console.print(f"Recursive: [green]{recursive}[/green]")
    
    results = counter.count_directory_tokens(
        directory_path=directory_path,
        extensions=extensions or None,
        recursive=recursive
    )
    
    # Calculate summary
    total_tokens = sum(r.get('tokens', 0) for r in results if 'tokens' in r)
    total_files = len(results)
    error_files = sum(1 for r in results if 'error' in r)
    
    # Display summary
    table = Table(title=f"Token Count Summary ({model})", box=box.ROUNDED)
    table.add_column("Total Files", style="cyan")
    table.add_column("Processed Successfully", style="green")
    table.add_column("Total Tokens", style="magenta")
    
    table.add_row(
        str(total_files),
        str(total_files - error_files),
        f"{total_tokens:,}"
    )
    
    console.print(table)
    
    # Display detailed results
    if total_files <= 20 or output:  # Only show details for manageable number of files
        detail_table = Table(title="Detailed File Results", box=box.SIMPLE)
        detail_table.add_column("File", style="cyan")
        detail_table.add_column("Tokens", style="green")
        detail_table.add_column("Characters", style="yellow")
        
        for result in results:
            if 'error' in result:
                detail_table.add_row(
                    result['file'],
                    "ERROR",
                    result['error']
                )
            else:
                detail_table.add_row(
                    result['file'],
                    str(result['tokens']),
                    str(result['characters'])
                )
        
        if total_files <= 20:  # Only print to console if manageable
            console.print(detail_table)
    
    if output:
        _save_results(results, output)
        console.print(f"[bold green]Results saved to: {output}[/bold green]")


def _display_result(result: dict, output: Optional[str] = None):
    """Display the result in a table and optionally save to a file."""
    table = Table(title=f"Token Count ({result['model']})", box=box.ROUNDED)
    table.add_column("File", style="cyan")
    table.add_column("Tokens", style="green")
    table.add_column("Characters", style="yellow")
    
    table.add_row(
        result['file'],
        str(result['tokens']),
        str(result['characters'])
    )
    
    console.print(table)
    
    # Add additional info based on file type
    if 'rows' in result and 'columns' in result:
        console.print(f"[bold]Rows:[/bold] {result['rows']}")
        console.print(f"[bold]Columns:[/bold] {result['columns']}")
    elif 'entries' in result:
        console.print(f"[bold]Entries:[/bold] {result['entries']}")
    
    if output:
        _save_results([result], output)
        console.print(f"[bold green]Result saved to: {output}[/bold green]")


def _save_results(results: List[dict], output_path: str):
    """Save results to a file in JSON or CSV format."""
    _, ext = os.path.splitext(output_path)
    
    if ext.lower() == '.json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    
    elif ext.lower() == '.csv':
        # Convert to DataFrame for CSV output
        df = pd.DataFrame(results)
        df.to_csv(output_path, index=False)
    
    else:
        # Default to JSON if extension not specified
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)


if __name__ == "__main__":
    main()