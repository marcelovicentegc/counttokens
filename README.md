# VTEX AI CLI

A CLI to help developers with AI-related tasks

This tool provides functionalities to count tokens in text, files, or directories.

It also includes an option to ingest curated data from VTEX repositories.

## Installation

```bash
# Install from source
git clone https://github.com/vtex/ai-cli.git
cd ai-cli
source venv/bin/activate
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
vtexai counttokens text "Your text string here" --model gpt-3.5-turbo
```

### Count tokens in a file

```bash
vtexai counttokens file path/to/your/file.txt --model gpt-3.5-turbo
```

### Count tokens in a directory

```bash
vtexai counttokens directory path/to/your/directory --recursive --model gpt-3.5-turbo --extensions txt json
```

### Save results to a file

```bash
vtexai counttokens directory path/to/your/directory --output results.json
```

### Use interactive mode

```bash
vtexai counttokens interactive
```

This will start an interactive session that guides you through:
- Selecting the model to use for token counting
- Choosing between counting tokens in text, a file, or a directory
- Providing inputs through a series of guided prompts
- Viewing results and saving them to a file if desired

### Ingest data from repositories

```bash
vtexai ingest
```

This will start the interactive ingest tool which allows you to:
1. Select from available repositories (currently supporting Shoreline and FastStore)
2. Clone or use an existing repository
3. Select specific data types to ingest based on the repository
4. Save ingested data to your local machine

The ingest tool is designed to be easily extensible - new repositories can be added to the system with minimal code changes.

## Options

- `--model`, `-m`: The model to use for token counting (default: gpt-3.5-turbo)
- `--output`, `-o`: Path to save output as JSON or CSV
- `--extensions`, `-e`: File extensions to process (can be specified multiple times, e.g., `-e txt -e json`)
- `--recursive/--no-recursive`: Whether to search subdirectories recursively (default: recursive)

## Python API

You can also use CountTokens programmatically in your Python code:

```python
from vtex_ai_tools import TokenCounter

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

# Use the Ingest functionality in your code
from vtex_ai_tools import Ingest

# Initialize the ingest tool
ingest_tool = Ingest()

# Access Shoreline Best Practices programmatically
repo_path = "/path/to/shoreline/repo"  # Provide existing repo path
ingest_tool.ingest_shoreline_best_practices(repo_path)

# Access Shoreline Examples programmatically
ingest_tool.ingest_shoreline_examples(repo_path)
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