import os
import json
import csv
import tiktoken
from typing import Dict, List, Optional, Union, Tuple
import pandas as pd
from tqdm import tqdm
from rich.console import Console

console = Console()

class TokenCounter:
    """
    A class for counting tokens in various text datasets using tiktoken.
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        """
        Initialize the TokenCounter with a specified model.
        
        Args:
            model (str): The model to use for token counting.
                         Options include: "gpt-3.5-turbo", "gpt-4", "text-davinci-003", etc.
        """
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base encoding if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """
        Count the number of tokens in a given text.
        
        Args:
            text (str): The text to count tokens for.
            
        Returns:
            int: Number of tokens in the text.
        """
        if not text:
            return 0
        
        # Count tokens
        tokens = self.encoding.encode(text)
        return len(tokens)
    
    def count_file_tokens(self, file_path: str) -> Dict:
        """
        Count tokens in a file.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            Dict: A dictionary containing token count information.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Read file contents based on extension
        if ext == '.json':
            return self._count_json_file_tokens(file_path)
        elif ext == '.csv':
            return self._count_csv_file_tokens(file_path)
        elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
            return self._count_text_file_tokens(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _count_text_file_tokens(self, file_path: str) -> Dict:
        """Count tokens in a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        token_count = self.count_tokens(content)
        return {
            'file': file_path,
            'tokens': token_count,
            'characters': len(content),
            'model': self.model
        }
    
    def _count_json_file_tokens(self, file_path: str) -> Dict:
        """Count tokens in a JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert to string to count tokens
        content = json.dumps(data)
        token_count = self.count_tokens(content)
        
        return {
            'file': file_path,
            'tokens': token_count,
            'characters': len(content),
            'entries': len(data) if isinstance(data, list) else 1,
            'model': self.model
        }
    
    def _count_csv_file_tokens(self, file_path: str) -> Dict:
        """Count tokens in a CSV file."""
        df = pd.read_csv(file_path)
        
        # Count tokens in each cell
        total_tokens = 0
        for column in df.columns:
            for value in df[column].astype(str):
                total_tokens += self.count_tokens(value)
        
        # Also count tokens if the entire CSV was a single string
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'file': file_path,
            'tokens': total_tokens,
            'characters': len(content),
            'rows': len(df),
            'columns': len(df.columns),
            'model': self.model
        }
    
    def count_directory_tokens(self, directory_path: str, 
                              extensions: Optional[List[str]] = None,
                              recursive: bool = True) -> List[Dict]:
        """
        Count tokens in all files within a directory.
        
        Args:
            directory_path (str): Path to the directory.
            extensions (List[str], optional): List of file extensions to process.
            recursive (bool): Whether to search subdirectories recursively.
            
        Returns:
            List[Dict]: A list of dictionaries containing token count information for each file.
        """
        if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Directory not found: {directory_path}")
        
        results = []
        
        # Define supported extensions if not provided
        if extensions is None:
            extensions = ['.txt', '.json', '.csv', '.md', '.py', '.js', '.html', '.css']
        
        # Normalize extensions to include the dot if not already
        extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        
        # Walk through directory
        for root, dirs, files in os.walk(directory_path):
            if not recursive and root != directory_path:
                continue
                
            for file in tqdm(files, desc=f"Processing files in {root}"):
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path)
                
                if ext.lower() in extensions:
                    try:
                        result = self.count_file_tokens(file_path)
                        results.append(result)
                    except Exception as e:
                        results.append({
                            'file': file_path,
                            'error': str(e),
                            'model': self.model
                        })
        
        return results

class InteractiveTokenCounter:
    """
    An interactive class for counting tokens through a guided menu-based interface.
    """
    
    def __init__(self):
        self.counter = None
        self.options = {
            1: self._count_text_tokens,
            2: self._count_file_tokens,
            3: self._count_directory_tokens
        }
        self.models = [
            "gpt-3.5-turbo",
            "gpt-4",
            "text-davinci-003",
            "text-davinci-002",
            "text-embedding-ada-002"
        ]
        self.supported_extensions = ['.txt', '.json', '.csv', '.md', '.py', '.js', '.html', '.css']
    
    def run(self):
        """Run the interactive token counter with guided prompts."""
        console.print("[bold]Interactive Token Counter[/bold]")
        console.print("This tool will help you count tokens in text, files, or directories.")
        
        # First, let the user select a model
        model = self._select_model()
        self.counter = TokenCounter(model=model)
        
        # Display options
        console.print("\n[bold]Select what you want to count:[/bold]")
        console.print("1. Count tokens in a text string")
        console.print("2. Count tokens in a file")
        console.print("3. Count tokens in a directory")
        
        # Get user choice
        while True:
            try:
                choice = int(input("\nEnter your choice (1-3): "))
                if choice in self.options:
                    self.options[choice]()
                    break
                else:
                    console.print("[red]Invalid option selected. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
    
    def _select_model(self) -> str:
        """Let the user select a model for token counting."""
        console.print("\n[bold]Available models:[/bold]")
        for i, model in enumerate(self.models, 1):
            console.print(f"{i}. {model}")
        
        default_model = "gpt-3.5-turbo"
        console.print(f"\nDefault model: [cyan]{default_model}[/cyan]")
        
        choice = input("Select a model (enter number) or press Enter for default: ").strip()
        
        if not choice:
            return default_model
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.models):
                return self.models[index]
            else:
                console.print(f"[yellow]Invalid choice. Using default model: {default_model}[/yellow]")
                return default_model
        except ValueError:
            console.print(f"[yellow]Invalid input. Using default model: {default_model}[/yellow]")
            return default_model
    
    def _count_text_tokens(self):
        """Interactive function to count tokens in a text string."""
        console.print("\n[bold]Count tokens in a text string[/bold]")
        
        while True:
            text = input("\nEnter the text (or type 'exit' to quit): ")
            
            if text.lower() == 'exit':
                break
                
            if not text:
                console.print("[yellow]No text entered. Please try again.[/yellow]")
                continue
            
            token_count = self.counter.count_tokens(text)
            
            console.print(f"\n[bold]Results:[/bold]")
            console.print(f"Text length: [cyan]{len(text)}[/cyan] characters")
            console.print(f"Token count: [green]{token_count}[/green] tokens")
            
            again = input("\nDo you want to count another text? (y/n): ").lower()
            if again != 'y':
                break
    
    def _count_file_tokens(self):
        """Interactive function to count tokens in a file."""
        console.print("\n[bold]Count tokens in a file[/bold]")
        
        while True:
            file_path = input("\nEnter the path to the file (or type 'exit' to quit): ")
            
            if file_path.lower() == 'exit':
                break
                
            if not file_path:
                console.print("[yellow]No file path entered. Please try again.[/yellow]")
                continue
            
            # Check if file exists
            if not os.path.exists(file_path):
                console.print("[red]File not found. Please check the path and try again.[/red]")
                continue
            
            # Check if it's a file
            if not os.path.isfile(file_path):
                console.print("[red]The path does not point to a file. Please try again.[/red]")
                continue
            
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_extensions:
                console.print(f"[yellow]Warning: File extension {ext} might not be supported.[/yellow]")
                proceed = input("Do you want to proceed anyway? (y/n): ").lower()
                if proceed != 'y':
                    continue
            
            try:
                with console.status(f"[bold green]Counting tokens in {file_path}...", spinner="dots"):
                    result = self.counter.count_file_tokens(file_path)
                
                console.print(f"\n[bold]Results:[/bold]")
                console.print(f"File: [cyan]{result['file']}[/cyan]")
                console.print(f"Characters: [magenta]{result['characters']:,}[/magenta]")
                console.print(f"Tokens: [green]{result['tokens']:,}[/green]")
                
                # Additional info based on file type
                if 'rows' in result and 'columns' in result:
                    console.print(f"Rows: [yellow]{result['rows']}[/yellow]")
                    console.print(f"Columns: [yellow]{result['columns']}[/yellow]")
                elif 'entries' in result:
                    console.print(f"Entries: [yellow]{result['entries']}[/yellow]")
                
                # Ask about saving results
                save = input("\nDo you want to save the results to a file? (y/n): ").lower()
                if save == 'y':
                    output_path = input("Enter the output file path (e.g., results.json): ")
                    if output_path:
                        _, ext = os.path.splitext(output_path)
                        if not ext:
                            output_path += ".json"  # Default to JSON
                        
                        self._save_results([result], output_path)
                        console.print(f"[green]Results saved to: {output_path}[/green]")
            
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
            
            again = input("\nDo you want to count another file? (y/n): ").lower()
            if again != 'y':
                break
    
    def _count_directory_tokens(self):
        """Interactive function to count tokens in a directory."""
        console.print("\n[bold]Count tokens in a directory[/bold]")
        
        while True:
            directory_path = input("\nEnter the path to the directory (or type 'exit' to quit): ")
            
            if directory_path.lower() == 'exit':
                break
                
            if not directory_path:
                console.print("[yellow]No directory path entered. Please try again.[/yellow]")
                continue
            
            # Check if directory exists
            if not os.path.exists(directory_path):
                console.print("[red]Directory not found. Please check the path and try again.[/red]")
                continue
            
            # Check if it's a directory
            if not os.path.isdir(directory_path):
                console.print("[red]The path does not point to a directory. Please try again.[/red]")
                continue
            
            # Get extensions to process
            extensions_input = input("\nEnter file extensions to process (comma separated, e.g., txt,json) or press Enter for all supported: ")
            if extensions_input:
                extensions = [ext.strip().lower() for ext in extensions_input.split(',')]
                # Add dots to extensions if needed
                extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
            else:
                extensions = None
                
            # Get recursive option
            recursive_input = input("Process subdirectories recursively? (y/n, default: y): ").lower()
            recursive = recursive_input != 'n'  # Default to True
            
            try:
                console.print(f"\n[bold]Counting tokens in directory: {directory_path}[/bold]")
                console.print(f"Extensions: [cyan]{', '.join(extensions) if extensions else 'all supported'}[/cyan]")
                console.print(f"Recursive: [cyan]{'Yes' if recursive else 'No'}[/cyan]")
                
                results = self.counter.count_directory_tokens(
                    directory_path=directory_path,
                    extensions=extensions,
                    recursive=recursive
                )
                
                # Calculate summary
                total_tokens = sum(r.get('tokens', 0) for r in results if 'tokens' in r)
                total_files = len(results)
                error_files = sum(1 for r in results if 'error' in r)
                
                # Display summary
                console.print(f"\n[bold]Results:[/bold]")
                console.print(f"Total files processed: [cyan]{total_files}[/cyan]")
                console.print(f"Files processed successfully: [green]{total_files - error_files}[/green]")
                console.print(f"Total tokens: [magenta]{total_tokens:,}[/magenta]")
                
                # Ask about detailed results
                if total_files > 20:
                    show_details = input("\nShow detailed results for all files? (y/n): ").lower()
                    show_details = show_details == 'y'
                else:
                    show_details = True
                
                if show_details:
                    console.print("\n[bold]Detailed results:[/bold]")
                    for result in results:
                        if 'error' in result:
                            console.print(f"[red]Error processing {result['file']}: {result['error']}[/red]")
                        else:
                            console.print(f"File: [cyan]{result['file']}[/cyan]")
                            console.print(f"  Tokens: [green]{result['tokens']:,}[/green]")
                            console.print(f"  Characters: [magenta]{result['characters']:,}[/magenta]")
                
                # Ask about saving results
                save = input("\nDo you want to save the results to a file? (y/n): ").lower()
                if save == 'y':
                    output_path = input("Enter the output file path (e.g., results.json): ")
                    if output_path:
                        _, ext = os.path.splitext(output_path)
                        if not ext:
                            output_path += ".json"  # Default to JSON
                        
                        self._save_results(results, output_path)
                        console.print(f"[green]Results saved to: {output_path}[/green]")
            
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
            
            again = input("\nDo you want to count another directory? (y/n): ").lower()
            if again != 'y':
                break
    
    def _save_results(self, results: List[dict], output_path: str):
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