import pdfplumber
import cv2
import numpy as np
import json

# Extraction des positions des mots (premier tiers de la première page)
def extract_word_positions_first_third(pdf_path):
    word_positions = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            page_width = first_page.width
            page_height = first_page.height

            # Extraction des mots uniquement pour le premier tiers de la page
            words = first_page.extract_words()
            for word in words:
                if word['top'] <= page_height / 3:  # Vérifie si le mot est dans le premier tiers
                    word_info = {
                        'text': word['text'],
                        'x0': word['x0'],
                        'top': word['top'],
                        'x1': word['x1'],
                        'bottom': word['bottom'],
                        'page_number': 1
                    }
                    word_positions.append(word_info)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du PDF : {e}")

    return word_positions

# Extraction des lignes et rectangles (premier tiers de la première page)
def extract_graphics_first_third(pdf_path):
    graphics_data = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            page_height = first_page.height

            # Filtrer les lignes et rectangles pour le premier tiers
            lines = [line for line in first_page.lines if line['top'] <= page_height / 3 and line['bottom'] <= page_height / 3]
            rects = [rect for rect in first_page.rects if rect['top'] <= page_height / 3 and rect['bottom'] <= page_height / 3]

            graphics_data.append((1, lines, rects))
    except Exception as e:
        print(f"Erreur lors de l'extraction des graphiques : {e}")

    return graphics_data

# Création d'une image combinée pour le premier tiers de la première page
def create_combined_image_first_third(pdf_page_width, pdf_page_height, word_positions, graphics_data):
    # Créer une image blanche pour le premier tiers
    image = np.ones((pdf_page_height // 3, pdf_page_width, 3), dtype=np.uint8) * 255

    # Ajouter les mots
    filtered_words = [word for word in word_positions if word['page_number'] == 1]
    for word in filtered_words:
        top_left = (int(word['x0']), int(word['top']))
        bottom_right = (int(word['x1']), int(word['bottom']))
        cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 1)

        # Ajouter le texte
        text_position = (int(word['x0']), int((word['top'] + word['bottom']) / 2))
        font_scale = (word['bottom'] - word['top']) / 30.0
        font_thickness = 1
        text_color = (0, 0, 0)
        cv2.putText(image, word['text'], text_position,
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)

    # Ajouter les graphiques
    if graphics_data:
        _, lines, rects = graphics_data[0]
        for line in lines:
            x0, y0, x1, y1 = int(line['x0']), int(line['top']), int(line['x1']), int(line['bottom'])
            cv2.line(image, (x0, y0), (x1, y1), (0, 0, 255), 2)  # Lignes rouges

        for rect in rects:
            x0, top, x1, bottom = int(rect['x0']), int(rect['top']), int(rect['x1']), int(rect['bottom'])
            cv2.rectangle(image, (x0, top), (x1, bottom), (0, 255, 0), 2)  # Rectangles verts

    return image

# Main
pdf_path = 'KID PRIIPS - Feeder Boscalt - Class C (français).pdf'
output_json = 'output_data_first_third.json'

try:
    # Dimensions de la page (ajustez en fonction du PDF)
    page_width = 595
    page_height = 842

    # Extraction des données pour le premier tiers de la première page
    word_positions = extract_word_positions_first_third(pdf_path)
    graphics_data = extract_graphics_first_third(pdf_path)

    # Enregistrer les données dans un fichier JSON
    data = {
        'words': word_positions,
        'graphics': []
    }

    for page_number, lines, rects in graphics_data:
        page_data = {
            'page_number': page_number,
            'lines': [{'x0': line['x0'], 'top': line['top'], 'x1': line['x1'], 'bottom': line['bottom']} for line in lines],
            'rects': [{'x0': rect['x0'], 'top': rect['top'], 'x1': rect['x1'], 'bottom': rect['bottom']} for rect in rects]
        }
        data['graphics'].append(page_data)

    with open(output_json, 'w') as f:
        json.dump(data, f, indent=4)

    # Visualiser le premier tiers combiné de la première page
    combined_image = create_combined_image_first_third(page_width, page_height, word_positions, graphics_data)
    cv2.imshow('Premier tiers de la première page', combined_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

except Exception as e:
    print(f"Erreur : {e}")
