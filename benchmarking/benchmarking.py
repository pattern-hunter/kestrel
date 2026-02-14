import mcp_client, kestrel_client
import asyncio

# Initialize prompts and models
prompts = ["What is the current location of the International Space Station?"]
# models = ["llama3.1"]
models = ["gemini-2.5-flash"]


for prompt in prompts:
    for model in models:
        print(f"\n\n=== Running benchmark for model: {model}, prompt: '{prompt}' ===")
        # Run mcp-use
        mcp_total_tokens, mcp_elapsed_time = mcp_client.run_agent(model=model, prompt=prompt)
        print(f"\nMCP-USE Total Tokens: {mcp_total_tokens}")
        print(f"\nMCP-USE Elapsed Time: {mcp_elapsed_time:.2f} seconds\n\n")

        # Run code-mode
        kestrel_total_tokens, kestrel_elapsed_time = kestrel_client.run_kestrel_code_mode(model=model, prompt=prompt)
        print(f"\nKestrel Code Mode Total Tokens: {kestrel_total_tokens}")
        print(f"\nKestrel Code Mode Elapsed Time: {kestrel_elapsed_time:.2f} seconds\n\n")