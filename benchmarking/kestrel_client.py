import os, sys
module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kestrel')
sys.path.append(module_dir)
import code_mode
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
from typing import Tuple
import time


def run_kestrel_code_mode(model: str, prompt: str) -> Tuple[int, int]:
    start = time.time()
    execution_plan, functions_list, execution_plan_tokens = code_mode.create_execution_plan(
        prompt=prompt,
        services_directory="benchmarking/services",
        model=model
    )

    code_to_execute, code_writing_tokens = code_mode.write_execution_code(
        execution_plan=execution_plan,
        functions_list=functions_list,
        model=model
    )

    result, error, return_code = code_mode.execute_plan_subprocess(code_to_execute)

    return execution_plan_tokens + code_writing_tokens, int(time.time() - start)