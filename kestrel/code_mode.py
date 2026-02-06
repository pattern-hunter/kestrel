import ast
import os
from pathlib import Path
from typing import Dict, List, Tuple
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

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
            if isinstance(node, ast.FunctionDef):
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
                
                signature = f"{node.name}({', '.join(arg_strs)}) -> {return_type}"
                functions.append(signature)
    
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
    
    return functions

def get_all_client_functions(services_dir: str) -> Dict[str, List[str]]:
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
    for client_file in services_path.rglob('client.py'):
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
        


def create_execution_plan(prompt: str, services_directory: str, model: str) -> Tuple[str, Dict[str, List[str]]]:
    llm = init_llm(model=model)
    functions_list = get_all_client_functions(services_directory)
    with open("prompts/execution_plan.md", "r") as f:
        system_message = f.read().format(functions_list=functions_list, question=prompt)
        result = llm.invoke(system_message)
        # TODO: Figure out a good way to filter list of functions to only those needed
        return result.content, functions_list
    
def write_execution_code(execution_plan: str, functions_list: Dict[str, List[str]], model: str) -> None:
    with open("prompts/write_code.md", "r") as f:
        system_message = f.read().format(functions_list=functions_list, execution_plan=execution_plan)
        llm = init_llm(model=model)
        result = llm.invoke(system_message)
        return result.content