from llm_utils import detect_intent_with_llm, parse_user_request, describe_schedule_with_llm
from generation.round_robin_scheduler import generate_schedule

def run_scheduling_pipeline(user_prompt: str):
    intent = detect_intent_with_llm(user_prompt)
    if intent != "match_schedule_request":
        return {"summary": "Désolé, je ne comprends pas la demande.", "schedule": []}

    parsed_request = parse_user_request(user_prompt)
    schedule = generate_schedule(
        teams=parsed_request["teams"],
        stadiums=parsed_request.get("stadiums", {}),
        unavailable_dates=parsed_request.get("unavailable_dates", []),
        constraints=parsed_request.get("constraints", {})
    )

    summary = describe_schedule_with_llm(schedule)
    return {"schedule": schedule, "summary": summary}
