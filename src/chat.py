from dotenv import load_dotenv
import ast
import json
import openai
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = openai.OpenAI(api_key=api_key)


def extract_parameters_and_domains(function_code: str):
    # Define the MCP-compliant prompt
    mcp_prompt = {
        "version": "1.0",
        "context": {
            "task": (
                "Extract the list of parameters and their possible domains from the given Python function. "
                "The domain should be inferred from the code logic, not just from type annotations or default values. "
                "For example, if the function contains a condition like `if x == 4`, then the domain of `x` should be: [4, (a random number different from 4)]. "
                "If the function contains `y = y / 2` followed by `if y == 1`, then the domain of `y` should be: [2, (a random number different from 2)]. "
                "If a parameter can be any real number, pick one representative value randomly. (e.g. 1 or 2 or 3)"
            ),
            "function_code": function_code,
        },
        "instruction": (
            "Return only a valid Python dictionary literal, using correct syntax. "
            "Do not include any explanation, markdown formatting, or extra text. "
            "Only output the dictionary. Example of valid output:\n"
            "{\n"
            "  'x': [4, 7],\n"
            "  'y': [2, 5]\n"
            "}"
        ),
    }

    # Send the prompt to ChatGPT using the new API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful and very competent assistant that understands Python code and can extract parameter information.",
            },
            {"role": "user", "content": f"<mcp>{mcp_prompt}</mcp>"},
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content


def parse_llm_response(response_str):
    """
    Converts a string representation of a dictionary into an actual Python dictionary.

    Args:
        response_str (str): The string returned by the LLM.

    Returns:
        dict: Parsed dictionary.
    """
    try:
        result = ast.literal_eval(response_str)
        if isinstance(result, dict):
            return result
        else:
            raise ValueError("Parsed object is not a dictionary.")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing LLM response: {e}")
        return {}


def robust_parse(llm_output):
    try:
        return ast.literal_eval(llm_output)
    except Exception:
        try:
            return json.loads(llm_output)
        except Exception as e:
            print("Parsing failed:", e)
            return {}

    # Example usage


python_function = """
def calculate_discount(price: float, customer_type: str, is_member: bool = False, y: float):
    if customer_type == "student":
        discount = 0.2
    elif customer_type == "senior":
        discount = 0.3
    else:
        discount = 0.1
    if is_member:
        discount += 0.05
    if y == 3:
        print("coucou")
    elif y == 5
        print("HI")
    else
        print("lule")
    return price * (1 - discount)
"""


# result = extract_parameters_and_domains(python_function)
# print(result)
# print(parse_llm_response(result))
