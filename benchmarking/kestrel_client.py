import os, sys
module_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'kestrel')
sys.path.append(module_dir)
import code_mode
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
from typing import Tuple
import time
from pathlib import Path
import importlib.util


def run_kestrel_code_mode(model: str, prompt: str) -> Tuple[int, int]:
    start = time.time()
    services_dir = "benchmarking/services"

    execution_plan, execution_plan_tokens = code_mode.create_execution_plan(
        prompt=prompt,
        services_directory=services_dir,
        model=model,
    )

    print(f"\n📋 Execution Plan:\n{execution_plan}")

    result, error, return_code = code_mode.execute_plan_subprocess(execution_plan=execution_plan)

    print(f"\n🧑‍💻 Execution Result:\n{result}")
    print(f"\n❌ Execution Error:\n{error}")

    return execution_plan_tokens, int(time.time() - start)