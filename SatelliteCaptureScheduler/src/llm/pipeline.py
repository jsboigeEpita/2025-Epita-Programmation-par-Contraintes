import codecs
import json
import os
import sys
import click
import requests
import yaml
from dotenv import load_dotenv
from openai import OpenAI

from core.satellite import Satellite, SatelliteConfig
from integration.scheduler_interface import run_satellite_scheduler

if sys.stdout.encoding != "utf-8":
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

load_dotenv()

model = os.getenv("MODEL_NAME")
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE")

# Check for required environment variables
required_env_vars = ["MODEL_NAME", "OPENAI_API_KEY", "OPENAI_API_BASE"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please add them to your .env file")
    sys.exit(1)

llm = OpenAI(base_url=base_url, api_key=api_key)


def get_gps_coordinates(location):
    """Get GPS coordinates for a location using OpenStreetMap Nominatim API."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
        response = requests.get(url, headers={"User-Agent": "satellite-scheduler"})
        response.raise_for_status()  # Raise exception for bad responses
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        else:
            print(f"Warning: Could not find coordinates for location: {location}")
            return None
    except Exception as e:
        print(f"Error getting GPS coordinates for {location}: {str(e)}")
        return None


def parse_user_request(user_text):
    """Extract observation requests from user input using LLM."""
    try:
        response = llm.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_text}],
            functions=[
                {
                    "name": "extract_observation_requests",
                    "description": "Extract locations, priorities (1 to 5, 5 being urgent), and area sizes from user input. Please try to be as specific as possible about the location points.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "requests": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "location": {"type": "string"},
                                        "priority": {
                                            "type": "integer",
                                            "enum": [1, 2, 3, 4, 5],
                                        },
                                        "area_size_km2": {
                                            "type": "number",
                                            "minimum": 0.1,
                                            "maximum": 40.0,
                                        },
                                    },
                                    "required": ["location"],
                                },
                            }
                        },
                        "required": ["requests"],
                    },
                }
            ],
            function_call={"name": "extract_observation_requests"},
            temperature=0.3,
        )
        return response.choices[0].message.function_call.arguments
    except Exception as e:
        print(f"Error parsing user request: {str(e)}")
        return json.dumps({"requests": []})


def generate_solver_input(locations):
    """Generate input for the solver by adding GPS coordinates to locations."""
    enriched_locations = []
    for loc in locations:
        if "priority" not in loc:
            loc["priority"] = 3  # Medium priority by default
        if "area_size_km2" not in loc:
            loc["area_size_km2"] = 20.0  # Default area size

        gps_coordinates = get_gps_coordinates(loc["location"])
        loc_with_coords = loc.copy()
        loc_with_coords["gps_coordinates"] = (
            {"latitude": gps_coordinates[0], "longitude": gps_coordinates[1]}
            if gps_coordinates
            else {"latitude": None, "longitude": None}
        )

        enriched_locations.append(loc_with_coords)

    return {"locations": enriched_locations}


def simulate_solver(input_data):
    """Run the real satellite observation scheduling solver."""
    try:

        satellite = Satellite(
                SatelliteConfig(
                MU=398600.4418,
                A=7000,
                EC=0.01,
                IC=45,
                OMEGA=60,
                W=30,
                R=6371,
                NUM_FRAMES=1000,
                memory_capacity_gb=10,
                image_size_per_km2_gb=0.15,
                image_duration_per_km2_sec=3.5,
                max_photo_duration_s=120,
                recalibration_time_s=30,
                speed_kms_per_s=50,
            )
        )

        # Use our new integrated solver
        return run_satellite_scheduler(input_data["locations"], satellite)
    except Exception as e:
        print(f"Error in solver: {str(e)}")
        # Fallback to simple simulation
        output = {"observations": []}
        for req in input_data["locations"]:
            # Skip locations with no coordinates
            if req["gps_coordinates"]["latitude"] is None:
                output["observations"].append(
                    {
                        "location": req["location"],
                        "success": False,
                        "reason": "Could not determine GPS coordinates",
                    }
                )
                continue

            area_size = req.get("area_size_km2", 1.0)
            priority = req.get("priority", 3)
            photo_size = round(area_size * (1.5 - priority * 0.1), 1)
            photo_size = max(0.5, min(photo_size, 5.0))  # Limit between 0.5 and 5.0 GB
            duration = int(30 + area_size * 15)  # Between 30s and several minutes

            output["observations"].append(
                {
                    "location": req["location"],
                    "success": True,
                    "photo_size_gb": photo_size,
                    "photo_duration_s": duration,
                    "priority": priority,
                    "coordinates": f"{req['gps_coordinates']['latitude']}, {req['gps_coordinates']['longitude']}",
                }
            )

        return output


def describe_solver_output(solver_output):
    """Generate a human-readable description of the solver output using LLM."""
    try:
        # Convert the solver output to a JSON string for the LLM
        solver_output_str = json.dumps(solver_output)

        response = llm.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes satellite observation schedules.",
                },
                {
                    "role": "user",
                    "content": f"Please provide a summary of these scheduled satellite observations: {solver_output_str}",
                },
            ],
            temperature=0.5,
        )

        if response.choices and response.choices[0].message:
            return response.choices[0].message.content
        else:
            return "Could not generate a summary of the observations."
    except Exception as e:
        print(f"Error describing solver output: {str(e)}")
        return "An error occurred while generating the observation summary."


def detect_intent_with_llm(user_text):
    """Use the LLM to detect the user's intent from their input text."""
    try:
        response = llm.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": """You are an intent classifier for a satellite observation system. 
                Determine if the user is making an observation request, checking the status of a request, or asking a general question.
                - observation_request: User wants to schedule or request satellite imagery of a specific location or area
                - status_check: User is asking about the status or results of a previous observation
                - general_question: User is asking a general question about satellites, imagery, or other topics
                Respond ONLY with the exact intent name.""",
                },
                {"role": "user", "content": user_text},
            ],
            max_tokens=20,
            temperature=0.1,
        )

        if response.choices and response.choices[0].message:
            intent_text = response.choices[0].message.content.strip().lower()
            if "observation_request" in intent_text:
                return "observation_request"
            elif "status_check" in intent_text:
                return "status_check"
            else:
                return "general_question"
        else:
            return "general_question"
    except Exception as e:
        print(f"Error detecting intent with LLM: {str(e)}")
        return "general_question"

@click.command()
def cli():
    """Interactive CLI for Satellite Observation Scheduling"""
    click.secho("🛰️ Satellite Observation Scheduler CLI 🛰️", fg="green", bold=True)
    click.secho(
        "Enter observation requests or ask questions about satellite capabilities.",
        fg="blue",
    )

    conversation_history = []

    while True:
        click.echo("\n" + "=" * 50)
        click.secho("[1] Enter a new observation request or ask a question", fg="cyan")
        click.secho("[2] Exit", fg="cyan")

        choice = click.prompt(
            "Choose an option",
            type=int,
            default=1,
            show_default=False,
            prompt_suffix=": ",
        )

        if choice == 1:
            user_text = click.prompt(
                "\nEnter your observation request or question",
                prompt_suffix=": ",
            )
            click.echo("\nProcessing input...")

            conversation_history.append({"role": "user", "content": user_text})

            intent = detect_intent_with_llm(user_text)
            click.secho(f"Detected intent: {intent}", fg="blue")

            if intent == "observation_request":
                try:
                    parsed_data_str = parse_user_request(user_text)
                    parsed_data = json.loads(parsed_data_str)

                    if not parsed_data.get("requests"):
                        click.secho(
                            "No valid observation requests could be extracted. Please try again with more specific location information.",
                            fg="yellow",
                        )
                        continue

                    solver_input = generate_solver_input(parsed_data["requests"])
                    solver_output = simulate_solver(solver_input)

                    summary = describe_solver_output(solver_output)

                    click.secho(
                        "\n📋 Extracted Observation Requests:",
                        fg="green",
                        bold=True,
                    )
                    click.echo(
                        yaml.dump(
                            parsed_data,
                            default_flow_style=False,
                            allow_unicode=True,
                        )
                    )

                    click.secho(
                        "\n🗺️ Enriched Requests with Coordinates:",
                        fg="green",
                        bold=True,
                    )
                    click.echo(
                        yaml.dump(
                            solver_input,
                            default_flow_style=False,
                            allow_unicode=True,
                        )
                    )

                    click.secho("\n📊 Scheduled Observations:", fg="green", bold=True)
                    click.echo(
                        yaml.dump(
                            solver_output,
                            default_flow_style=False,
                            allow_unicode=True,
                        )
                    )

                    click.secho("\n📝 Summary:", fg="green", bold=True)
                    click.echo(summary)

                    conversation_history.append(
                        {
                            "role": "assistant",
                            "content": f"Scheduled observations for: {', '.join([r['location'] for r in parsed_data.get('requests', [])])}\n{summary}",
                        }
                    )

                except Exception as e:
                    error_msg = f"\nError processing observation request: {str(e)}"
                    click.secho(error_msg, fg="red")
                    conversation_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

            elif intent == "status_check":
                status_msg = "\nStatus Check: This functionality is not yet fully implemented. In the future, you'll be able to check the status of your scheduled observations."
                click.secho(status_msg, fg="yellow")

                conversation_history.append(
                    {"role": "assistant", "content": status_msg}
                )

            else:
                try:
                    messages = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant specializing in satellite observations and Earth monitoring. Provide informative responses about satellite capabilities, Earth observation, and related topics. Keep your responses conversational and engaging. Adapt the language of your answer depending on the language of the question.",
                        },
                        {"role": "user", "content": user_text},
                    ]

                    response = llm.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3,
                    )

                    assistant_response = response.choices[0].message.content
                    click.secho("\n🤖 Assistant's Response:", fg="green", bold=True)
                    click.echo(assistant_response)

                    conversation_history.append(
                        {"role": "assistant", "content": assistant_response}
                    )

                except Exception as e:
                    error_msg = f"\nError getting response: {str(e)}"
                    click.secho(error_msg, fg="red")
                    conversation_history.append(
                        {"role": "assistant", "content": error_msg}
                    )

        elif choice == 2:
            click.secho("Exiting. Have a great day! 👋", fg="green")
            break
        else:
            click.secho("Invalid choice. Please enter 1 or 2.", fg="red")


if __name__ == "__main__":
    cli()
