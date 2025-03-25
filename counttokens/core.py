import os
import json
import csv
import tiktoken
from typing import Dict, List, Optional, Union, Tuple
import pandas as pd
from tqdm import tqdm


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