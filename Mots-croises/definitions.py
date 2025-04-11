from openai import OpenAI

OPENAI_API_KEY = "" #Mettre clé OpenAI ici

if OPENAI_API_KEY == "":
    raise Exception("Clé OpenAI vide")
client = OpenAI(
  api_key=OPENAI_API_KEY,
)

base_prompt = ("Je souhaite créer des grilles de mots croisés, et j'ai une liste de mots pour la grille mais je n'ai pas les"
          " définitions des mots. Donne moi une définition dans le cadre d'un mot croisé pour chaque mot de cette liste de mot, "
          "sans numéroter les lignes et en mettant une définition par ligne:\n")

def create_definitions(dictionary):
    words = '\n'.join(dictionary.values())

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": base_prompt + words}]
    )

    result = completion.choices[0].message.content
    defs = result.split('\n')
    return defs