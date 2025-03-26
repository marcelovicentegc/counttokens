import os
import subprocess
from rich.console import Console
from gitingest import ingest
from typing import Dict, List, Optional, Tuple

console = Console()

class Repository:
    """
    A class representing a repository that can be ingested.
    """
    def __init__(self, 
                 name: str, 
                 url: str, 
                 description: str,
                 ingest_options: Dict[int, Tuple[str, str, str]]):
        """
        Initialize a repository configuration.
        
        Args:
            name: Repository name (used for folder names)
            url: Git URL for cloning
            description: Description of the repository
            ingest_options: Dictionary of ingest options where:
                - key is option number
                - value is tuple of (option name, file pattern, output subfolder)
        """
        self.name = name
        self.url = url
        self.description = description
        self.ingest_options = ingest_options

class Ingest:
    """
    A class for ingesting data from repositories using the gitingest package.
    """
    
    def __init__(self):
        # Define available repositories
        self.repositories = {
            1: Repository(
                name="shoreline",
                url="git@github.com:vtex/shoreline.git",
                description="VTEX Shoreline Design System",
                ingest_options={
                    1: ("Documentation > Best Practices", "**/*/best-practices.mdx", "shoreline-best-practices"),
                    2: ("Documentation > Examples", "/**/docs/examples/*.tsx", "shoreline-examples")
                }
            ),
            2: Repository(
                name="faststore",
                url="git@github.com:vtex/faststore.git",
                description="VTEX FastStore framework",
                ingest_options={
                    1: ("Documentation", "**/docs/**/*.mdx", "faststore-docs"),
                    2: ("Components", "**/src/components/**/*.{tsx,ts}", "faststore-components")
                }
            )
        }
        
        # Default directories
        self.clone_dir = os.path.expanduser("~/Documents")
        self.data_dir = os.path.expanduser("~/Data")
        
        # Will be set after repository selection
        self.selected_repo = None
    
    def run(self):
        """Run the ingest process with interactive prompts."""
        console.print("[bold]Data Ingest Tool[/bold]")
        console.print("This tool helps you ingest data from VTEX repositories.")
        
        # First, select a repository
        if not self._select_repository():
            console.print("[yellow]Ingest process canceled.[/yellow]")
            return
        
        # Now check if the repository exists locally
        repo_path = self._check_repository()
        
        # Display ingest options for the selected repository
        self._display_ingest_options()
        
        # Get user choice
        while True:
            try:
                choice = int(input(f"\nEnter your choice (1-{len(self.selected_repo.ingest_options)}): "))
                if choice in self.selected_repo.ingest_options:
                    # Make sure output directories exist
                    self._ensure_output_dirs()
                    # Run the selected ingest option
                    self._ingest_data(repo_path, choice)
                    break
                else:
                    console.print("[red]Invalid option selected. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
    
    def _select_repository(self) -> bool:
        """
        Let user select which repository to work with.
        Returns True if a repository was selected, False otherwise.
        """
        console.print("\n[bold]Available Repositories:[/bold]")
        
        for repo_id, repo in self.repositories.items():
            console.print(f"{repo_id}. {repo.name} - {repo.description}")
        
        console.print(f"{len(self.repositories) + 1}. Exit")
        
        while True:
            try:
                choice = int(input("\nSelect a repository: "))
                if choice in self.repositories:
                    self.selected_repo = self.repositories[choice]
                    console.print(f"[green]Selected: {self.selected_repo.name}[/green]")
                    return True
                elif choice == len(self.repositories) + 1:
                    return False
                else:
                    console.print("[red]Invalid option selected. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number.[/red]")
    
    def _display_ingest_options(self):
        """Display ingest options for the selected repository."""
        console.print(f"\n[bold]What would you like to ingest from {self.selected_repo.name}?[/bold]")
        
        for option_id, (option_name, _, _) in self.selected_repo.ingest_options.items():
            console.print(f"{option_id}. {option_name}")
    
    def _check_repository(self):
        """
        Check if the selected repository exists locally.
        If not, prompt the user to clone it.
        """
        # Construct the full path to where the repository should be
        repo_path = os.path.join(self.clone_dir, self.selected_repo.name)
        
        if os.path.exists(repo_path) and os.path.isdir(repo_path):
            console.print(f"[green]Found {self.selected_repo.name} repository at: {repo_path}[/green]")
            return repo_path
        else:
            console.print(f"[yellow]{self.selected_repo.name} repository not found at: {repo_path}[/yellow]")
            while True:
                choice = input("Would you like to clone the repository now? (y/n): ").lower()
                if choice in ['y', 'yes']:
                    return self._clone_repository()
                elif choice in ['n', 'no']:
                    custom_path = input(f"Enter the path to an existing {self.selected_repo.name} repository: ")
                    if os.path.exists(custom_path) and os.path.isdir(custom_path):
                        console.print(f"[green]Using repository at: {custom_path}[/green]")
                        return custom_path
                    else:
                        console.print("[red]Invalid path. Repository not found.[/red]")
                else:
                    console.print("[red]Invalid choice. Please enter 'y' or 'n'.[/red]")
    
    def _clone_repository(self):
        """Clone the selected repository and return its path."""
        # Make sure the clone directory exists
        os.makedirs(self.clone_dir, exist_ok=True)
        
        repo_path = os.path.join(self.clone_dir, self.selected_repo.name)
        console.print(f"[bold]Cloning {self.selected_repo.name} to {repo_path}...[/bold]")
        
        try:
            # Clone the repository
            subprocess.run(
                ["git", "clone", self.selected_repo.url, repo_path], 
                check=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            console.print(f"[green]Successfully cloned repository![/green]")
            return repo_path
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error cloning repository: {e}[/red]")
            console.print(f"[red]Error message: {e.stderr.decode()}[/red]")
            exit(1)
    
    def _ensure_output_dirs(self):
        """Ensure that the output directories exist."""
        # Create base data directory
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create output directories for each ingest option in the selected repository
        for _, (_, _, output_subfolder) in self.selected_repo.ingest_options.items():
            os.makedirs(os.path.join(self.data_dir, output_subfolder), exist_ok=True)
    
    def _ingest_data(self, repo_path: str, option_id: int):
        """
        Ingest data based on the selected repository and option.
        
        Args:
            repo_path: Path to the repository
            option_id: ID of the selected ingest option
        """
        option_name, pattern, output_subfolder = self.selected_repo.ingest_options[option_id]
        output_path = os.path.join(self.data_dir, output_subfolder, f"{output_subfolder}.txt")
        
        console.print(f"[bold]Ingesting {self.selected_repo.name} {option_name}...[/bold]")
        console.print(f"Repository path: {repo_path}")
        console.print(f"Output path: {output_path}")
        
        try:
            summary, tree, content = ingest(
                repo_path, 
                include_patterns=pattern, 
                output=output_path
            )
            
            console.print(f"[green]Successfully ingested {option_name}![/green]")
            console.print(f"Summary: {summary}")
            console.print(f"File tree: {tree}")
            console.print(f"Content length: {len(content) if content else 0} characters")
        except Exception as e:
            console.print(f"[red]Error ingesting {option_name}: {e}[/red]")
    
    # Maintain backward compatibility with existing code that might use these methods directly
    def ingest_shoreline_best_practices(self, repo_path):
        """Legacy method: Ingest Shoreline best practices documentation."""
        self.selected_repo = self.repositories[1]  # Shoreline
        self._ingest_data(repo_path, 1)  # Best Practices option
    
    def ingest_shoreline_examples(self, repo_path):
        """Legacy method: Ingest Shoreline examples."""
        self.selected_repo = self.repositories[1]  # Shoreline
        self._ingest_data(repo_path, 2)  # Examples option