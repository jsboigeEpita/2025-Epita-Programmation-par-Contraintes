import openai  # ou ton client préféré
import json
import os
from dotenv import load_dotenv
import openai

load_dotenv()  # Charge le contenu de .env

openai.api_key = os.getenv("OPENAI_API_KEY")

def detect_intent_with_llm(prompt: str) -> str:
    system_msg = "Tu es un assistant qui classifie les requêtes utilisateur."
    user_msg = f"Voici la requête : {prompt}\nQuelle est l'intention ? (match_schedule_request, team_info_query, general_question)"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        temperature=0
    )
    return completion["choices"][0]["message"]["content"].strip()

def parse_user_request(prompt: str) -> dict:
    system_msg = (
        "Tu extrais les informations utiles d'une demande de calendrier sportif. "
        "Retourne un JSON contenant : teams, stadiums (optionnel), unavailable_dates (optionnel), constraints (optionnel)."
    )
    user_msg = f"Voici la demande : {prompt}"
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        temperature=0
    )
    try:
        return json.loads(completion["choices"][0]["message"]["content"])
    except Exception:
        raise ValueError("La réponse du LLM n'est pas un JSON valide.")

def describe_schedule_with_llm(schedule: list) -> str:
    system_msg = "Tu résumes un calendrier sportif dans un style clair et concis pour un humain."
    formatted = json.dumps(schedule, indent=2)
    user_msg = f"Voici un calendrier :\n{formatted}\nFais un résumé lisible."
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
        temperature=0.7
    )
    return completion["choices"][0]["message"]["content"].strip()
