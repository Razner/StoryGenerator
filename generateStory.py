import json
import requests
from readStory import read_story

def generate_story(prenom, age, style, duree):
    prompt = f"""
    Crée une histoire pour un enfant nommé {prenom}, âgé de {age} ans.
    Le style est {style}.
    L’histoire doit durer environ {duree} minutes et être adaptée à un jeune public.
    Garde un ton positif et imaginatif.
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt},
        stream=True
    )

    story = ""

    for line in response.iter_lines():
        if not line:
            continue
        try:
            data = json.loads(line.decode("utf-8"))
            if "response" in data:
                story += data["response"]
        except json.JSONDecodeError:
            continue

    return story.strip()

if __name__ == "__main__":
    story = generate_story("Thomas", 27, "magique", 5)
    print("\n=== HISTOIRE GÉNÉRÉE ===\n")
    print(story)
    read_story(story)
    input("Appuyez sur Entrée pour quitter...")
    exit()
