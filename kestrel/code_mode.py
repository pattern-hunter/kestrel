import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
import subprocess
import tempfile

def get_function_signatures(file_path: str) -> List[str]:
    """
    Extract function signatures from a Python file including return types.
    
    Args:
        file_path: Path to the Python file
    
    Returns:
        List of function signatures with return types
    """
    functions = []
    
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            is_async = isinstance(node, ast.AsyncFunctionDef)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private/magic functions
                if node.name.startswith('_'):
                    continue

                # Get function arguments
                args = node.args
                arg_names = [arg.arg for arg in args.args]
                
                # Get default values
                defaults = args.defaults
                num_defaults = len(defaults)
                num_args = len(arg_names)
                
                # Build argument string
                arg_strs = []
                for i, arg_name in enumerate(arg_names):
                    if i >= num_args - num_defaults:
                        # This argument has a default
                        arg_strs.append(f"{arg_name}=...")
                    else:
                        arg_strs.append(arg_name)
                
                # Get return type annotation
                return_type = "None"
                if node.returns:
                    if isinstance(node.returns, ast.Name):
                        return_type = node.returns.id
                    elif isinstance(node.returns, ast.Constant):
                        return_type = str(node.returns.value)
                    else:
                        return_type = ast.unparse(node.returns)
                prefix = "async " if is_async else ""
                signature = f"{prefix}{node.name}({', '.join(arg_strs)}) -> {return_type}"
                functions.append(signature)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return functions

def get_all_client_functions(services_dir: str, client_file_name: str) -> Dict[str, List[str]]:
    """
    Extract function signatures from all client.py files in services directory.
    
    Args:
        services_dir: Path to the services directory
    
    Returns:
        Dictionary mapping service name to list of function signatures
    """
    client_functions = {}
    services_path = Path(services_dir)
    
    # Find all client.py files
    for client_file in services_path.rglob(client_file_name):
        service_name = client_file.parent.name
        functions = get_function_signatures(str(client_file))
        client_functions[service_name] = functions
    
    return client_functions


def init_llm_gemini(model: str) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(model=model, temperature=0)

def init_llm_ollama(model: str) -> ChatOllama:
    return ChatOllama(model=model)

def init_llm(model: str) -> ChatGoogleGenerativeAI | ChatOllama:
    if model.startswith("gemini"):
        return init_llm_gemini(model=model)
    else:
        return init_llm_ollama(model=model)
        


def build_imports(services_dir: str) -> str:
    """
    Build import statements for all client.py files in the services directory.
    
    Args:
        services_dir: Path to the services directory
    
    Returns:
        String of import statements
    """
    import_prefix = services_dir.replace("/", ".")
    imports_code = ""
    
    for client_file in Path(services_dir).rglob('client.py'):
        mod_name = client_file.parent.name
        imports_code += f"import {import_prefix}.{mod_name}.client as {mod_name}\n"
    
    return imports_code

# TODO: name it better
def create_execution_plan(prompt: str, services_directory: str, client_file_name: str, model: str) -> Tuple[str, int]:
    llm = init_llm(model=model)
    functions_list = get_all_client_functions(services_dir=services_directory, client_file_name=client_file_name)
    print(f"\nFunctions list: {functions_list}\n")
    prompts_path = Path(__file__).resolve().parent / "prompts"
    with open(prompts_path / "execution_plan.md", "r") as f:
        system_message = f.read().format(functions_list=functions_list, question=prompt)
        result = llm.invoke(system_message)
        # TODO: Figure out a good way to filter list of functions to only those needed
        code = build_imports(services_dir=services_directory) + "\n" + result.content
        return code, int(result.usage_metadata['total_tokens'])
    

def execute_plan_subprocess(execution_plan: str) -> tuple[str, str, int]:
    """
    Execute the execution plan in a separate process.
    
    Args:
        execution_plan: Python code as a string
    
    Returns:
        Tuple of (stdout, stderr, exit_code)
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(execution_plan)
        script_path = f.name
    
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.stdout, result.stderr, result.returncode
    
    finally:
        # Clean up the temporary script file
        if os.path.exists(script_path):
            os.unlink(script_path)