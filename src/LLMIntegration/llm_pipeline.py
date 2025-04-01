import click
import yaml
import requests
from openai import OpenAI

# Initialize OpenAI client
llm = OpenAI(
    base_url="https://epita.open-webui.myia.io/api",
    api_key="sk-d8c0043ee83d4188bdc2aaee9566dd51"
)

INPUT_CREATOR_PROMPT = """
You are an agent made to extract locations, priorities, and area sizes from user requests. 
Priority is a number from 1 to 5, where 5 is the highest priority.
Area size is a number in square kilometers. This number depends on the requested area. You are free to adapt it.
Please use this format:
requests:
  - location: "Tokyo"
    priority: 3
    area_size_km2: 100
"""

OUTPUT_CREATOR_PROMPT = """
Summarize satellite observation results. Describe the results and mention differences due to external factors.
"""

def get_gps_coordinates(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    response = requests.get(url, headers={"User-Agent": "satellite-scheduler"})
    data = response.json()
    if data:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None

def parse_user_request(user_text):
    response = llm.chat.completions.create(
        messages=[{"role": "system", "content": INPUT_CREATOR_PROMPT},
                  {"role": "user", "content": user_text}],
        model="OpenAI.chatgpt-4o-latest",
        temperature=0.5
    )
    return yaml.safe_load(response.choices[0].message.content)

def generate_solver_input(locations):
    for loc in locations:
        gps_coordinates = get_gps_coordinates(loc["location"])
        loc["gps_coordinates"] = {"latitude": gps_coordinates[0], "longitude": gps_coordinates[1]} if gps_coordinates else None
    return {"locations": locations}

def simulate_solver(input_data):
    output = {"observations": []}
    for req in input_data["locations"]:
        output["observations"].append({
            "location": req["location"],
            "success": True,
            "photo_size_gb": 1.2,
            "photo_duration_s": 60
        })
    return output

def describe_solver_output(solver_data):
    response = llm.chat.completions.create(
        messages=[{"role": "system", "content": OUTPUT_CREATOR_PROMPT},
                  {"role": "user", "content": yaml.dump(solver_data)}],
        model="OpenAI.chatgpt-4o-latest",
        temperature=0.5
    )
    return response.choices[0].message.content

@click.command()
def cli():
    """Interactive CLI for Satellite Observation Scheduling"""
    click.echo("Satellite Observation Scheduler CLI")
    
    while True:
        click.echo("\n[1] Enter a new observation request")
        click.echo("[2] Exit")
        choice = click.prompt("Choose an option", type=int)

        if choice == 1:
            user_text = click.prompt("\nEnter your observation request (e.g., 'I need an urgent photo of Paris')")
            click.echo("\nProcessing request...")

            parsed_data = parse_user_request(user_text)
            solver_input = generate_solver_input(parsed_data["requests"])
            solver_output = simulate_solver(solver_input)
            summary = describe_solver_output(solver_output)

            click.echo("\nGenerated Observation Requests:")
            click.echo(yaml.dump(solver_input, default_flow_style=False))

            click.echo("\nSimulation Output:")
            click.echo(yaml.dump(solver_output, default_flow_style=False))

            click.echo("\nSummary of Observations:")
            click.echo(summary)

        elif choice == 2:
            click.echo("Exiting. Have a great day!")
            break
        else:
            click.echo("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    cli()
