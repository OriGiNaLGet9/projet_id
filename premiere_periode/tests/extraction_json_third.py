import pdfplumber
import json


def to_json(path):
    data = []
    with pdfplumber.open(path) as pdf_a_recuperer:
        # Récupérer la première page
        first_page = pdf_a_recuperer.pages[0]
        page_width = first_page.width
        page_height = first_page.height

        # Extraire les mots de la première page
        words = first_page.extract_words()
        for word in words:
            # Filtrer pour ne récupérer que les mots dans le premier tiers de la page
            if word["top"] <= page_height / 3:  # Si le mot est dans le premier tiers de la page
                data.append({
                    "page": 1,
                    "text": word["text"],
                    "x0": word["x0"],
                    "y0": word["top"],
                    "x1": word["x1"],
                    "y1": word["bottom"]
                })

    # Sauvegarder les données extraites dans un fichier JSON
    with open("mots_positions.json", "w", encoding="utf-8") as new_file:
        json.dump(data, new_file, ensure_ascii=False, indent=4)


path = "tests/KID PRIIPS - Feeder Boscalt - Class C (français).pdf"
to_json(path)
