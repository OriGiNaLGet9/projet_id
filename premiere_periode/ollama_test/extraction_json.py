import pdfplumber
import json


def to_json(path):
    data = []
    with pdfplumber.open(path) as pdf_a_recuperer:
        for page_number, page in enumerate(pdf_a_recuperer.pages):
            words = page.extract_words()
            for word in words : 
                data.append({
                    "page" : page_number+1,
                    "text" : word["text"],
                    "x0": word["x0"],
                    "y0": word["top"],
                    "x1": word["x1"],
                    "y1": word["bottom"]
                })
    with open("mots_positions.json", "w", encoding="utf-8") as new_file:
        json.dump(data, new_file, ensure_ascii=False, indent=4)

path = "Document2.pdf"
to_json(path)