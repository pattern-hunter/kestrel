# Kestrel

An exploration of MCP code mode execution, focused on reducing token usage and increasing accuracy.

## Installation

### Option 1: Install directly from GitHub

Install the latest version directly from the repository:

```bash
pip install git+https://github.com/pattern-hunter/kestrel.git
```

Or install a specific branch:

```bash
pip install git+https://github.com/pattern-hunter/kestrel.git@main
```

With development dependencies:

```bash
pip install "git+https://github.com/pattern-hunter/kestrel.git[dev]"
```

### Option 2: Clone locally and install in development mode

Clone the repository:

```bash
git clone https://github.com/pattern-hunter/kestrel.git
cd kestrel
```

Install as an editable package:

```bash
pip install -e .
```

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

```python
from kestrel import code_mode

# Extract function signatures from client.py files
functions = code_mode.get_all_client_functions("./services")

# Create execution plan
plan, functions_list = code_mode.create_execution_plan(
    prompt="Your prompt here",
    services_directory="./services",
    model="gemini-pro"
)

# Write execution code
code = code_mode.write_execution_code(plan, functions_list, "gemini-pro")
```

## Project Structure

```
kestrel/
├── kestrel/                 # Main package
│   ├── __init__.py
│   ├── code_mode.py        # Core functionality
│   └── prompts/            # Prompt templates
├── pyproject.toml          # Package configuration
└── README.md
```
