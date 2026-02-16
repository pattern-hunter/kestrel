You are given a list of available functions and a user question. Generate ONLY a sequence of Python function calls and data transformations to answer the question. Do not include any text, explanations, or formatting other than the function calls and transformations themselves.

Available Functions:
{functions_list}

User Question:
{question}

Output only the function calls and data transformations, one per line, with proper arguments. Include any data transformation operations needed to prepare arguments for the functions. Example format:
transformed_data = transform_operation(input_data)
function_name(arg1, transformed_data)
function_name2(result_from_previous)

Import any libraries required for the execution.

The final line MUST be a Python statement that prints the final result (for example: print(result) or print(final_value)). Do not include any additional text.