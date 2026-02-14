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

## Usage

```python
from kestrel import code_mode

# Extract function signatures from client.py files
functions = code_mode.get_all_client_functions(
    services_dir="./services", client_file_name="client.py"
)

# Create execution plan
code, total_tokens = code_mode.create_execution_plan(
    prompt="Your prompt here",
    services_directory="./services",
    model="gemini-pro"
)
```

## Project Structure

```
kestrel/
├── benchmarking/            # Example scripts and benchmarks and service clients
│   ├── kestrel_client.py
│   ├── mcp_client.py
│   └── services/            # Example MCP service clients (e.g. nasa_iss_locator)
├── build/                   # Build artifacts (wheels, dist)
├── kestrel/                 # Main package
│   ├── __init__.py
│   ├── code_mode.py         # Core functionality (execution plan, codegen, runner)
│   └── prompts/             # Prompt templates
├── pyproject.toml           # Package configuration
├── MANIFEST.in
└── README.md
```

## Run benchmark
To run a benchmark test, do the following:
- Add a *.env* file in the *benchmarking* folder. In the *.env* file, set *GEMINI_API_KEY* to your Gemini key
- Run the command
```
make run_benchmark
```