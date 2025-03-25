# CountTokens

A CLI tool for counting tokens in text datasets using tiktoken.

## Installation

```bash
# Install from source
git clone https://github.com/marcelovicentegc/counttokens.git
cd counttokens
pip install -e .
```

## Features

- Count tokens in text strings, files, or entire directories
- Support for multiple file formats (TXT, JSON, CSV, MD, PY, JS, HTML, CSS)
- Compatible with various OpenAI tokenizers (GPT-3.5-Turbo, GPT-4, etc.)
- Export results to JSON or CSV formats
- Beautifully formatted CLI output

## Usage

### Count tokens in a text string

```bash
counttokens text "Your text string here" --model gpt-3.5-turbo
```

### Count tokens in a file

```bash
counttokens file path/to/your/file.txt --model gpt-3.5-turbo
```

### Count tokens in a directory

```bash
counttokens directory path/to/your/directory --recursive --model gpt-3.5-turbo --extensions txt json
```

### Save results to a file

```bash
counttokens directory path/to/your/directory --output results.json
```

## Options

- `--model`, `-m`: The model to use for token counting (default: gpt-3.5-turbo)
- `--output`, `-o`: Path to save output as JSON or CSV
- `--extensions`, `-e`: File extensions to process (can be specified multiple times, e.g., `-e txt -e json`)
- `--recursive/--no-recursive`: Whether to search subdirectories recursively (default: recursive)

## Python API

You can also use CountTokens programmatically in your Python code:

```python
from counttokens import TokenCounter

# Initialize the token counter
counter = TokenCounter(model="gpt-3.5-turbo")

# Count tokens in a string
token_count = counter.count_tokens("Your text string here")
print(f"Token count: {token_count}")

# Count tokens in a file
file_result = counter.count_file_tokens("path/to/your/file.txt")
print(f"File token count: {file_result['tokens']}")

# Count tokens in a directory
dir_results = counter.count_directory_tokens("path/to/your/directory", 
                                            extensions=[".txt", ".json"], 
                                            recursive=True)
total_tokens = sum(r.get('tokens', 0) for r in dir_results if 'tokens' in r)
print(f"Directory total tokens: {total_tokens}")
```

## Supported Models

- gpt-3.5-turbo
- gpt-4
- text-davinci-003
- text-davinci-002
- text-embedding-ada-002
- ... and others supported by tiktoken

## License

MIT