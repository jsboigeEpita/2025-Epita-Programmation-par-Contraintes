from datetime import datetime, timedelta
from openai import OpenAI
import json
from utils.conf import api_key
from utils.utils import solve_schedule


# ========== EXAMPLE GPT FUNCTION CALL ==========

if __name__ == "__main__":
    client = OpenAI(api_key=api_key)
    functions = [ {
        "name": "solve_schedule",
        "description": "Generate a football round-robin schedule minimizing breaks",
        "parameters": {
            "type": "object",
            "properties": {
                "num_teams": {"type": "integer"},
                "start_date": {"type": "string"},
                "max_consecutive_away": {"type": "integer"}
            },
            "required": ["num_teams", "start_date", "max_consecutive_away"]
        }
    }]
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[{
            "role": "user",
            "content": "Generate a tournament with 4 teams starting on 2025-04-01, and no more than 2 away games in a row."
        }],
        functions=functions,
        function_call={"name": "solve_schedule"}
    )

    if response.choices[0].message.function_call:
        args = json.loads(response.choices[0].message.function_call.arguments)
        result = solve_schedule(**args)
        print(result)