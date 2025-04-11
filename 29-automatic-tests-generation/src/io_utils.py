import ast
import os
import importlib.util


def get_function_code_from_file(filename: str, function_name: str) -> str:
    """
    Extracts the source code of a specific function from a Python file.
    """
    with open(filename, "r") as file:
        source = file.read()

    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            return ast.unparse(node)  # Requires Python 3.9+

    raise ValueError(f"Function '{function_name}' not found in {filename}.")


def load_function_from_file(filename: str, function_name: str):
    """
    Dynamically loads a function from a given Python file.

    Parameters:
    - filename (str): Path to the Python file.
    - function_name (str): Name of the function to retrieve.

    Returns:
    - function: The function object if found, else raises appropriate error.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File '{filename}' does not exist.")

    module_name = os.path.splitext(os.path.basename(filename))[0]
    spec = importlib.util.spec_from_file_location(module_name, filename)
    if spec is None:
        raise ImportError(f"Could not load spec for module '{module_name}'.")

    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError(f"No loader for module '{module_name}'.")

    loader.exec_module(module)

    if not hasattr(module, function_name):
        raise AttributeError(f"Function '{function_name}' not found in '{filename}'.")

    func = getattr(module, function_name)
    if not callable(func):
        raise TypeError(f"'{function_name}' in '{filename}' is not callable.")

    return func


def pretty_print_values(values: dict) -> None:
    """
    Pretty prints the values of a dictionary.
    """
    print("\n======================================================================")
    for key, value in values.items():
        print(f"\033[94m{key}: {value}\033[0m")
    print("======================================================================\n")
