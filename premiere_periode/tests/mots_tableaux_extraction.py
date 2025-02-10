import pdfplumber
import cv2
import numpy as np

# Extraction des positions des mots
def extract_word_positions(pdf_path, page_limit=None):
    word_positions = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages_to_process = pdf.pages if page_limit is None else pdf.pages[:page_limit]
            for page_number, page in enumerate(pages_to_process):
                words = page.extract_words()
                for word in words:
                    word_info = {
                        'text': word['text'],
                        'x0': word['x0'],
                        'top': word['top'],
                        'x1': word['x1'],
                        'bottom': word['bottom'],
                        'page_number': page_number + 1
                    }
                    word_positions.append(word_info)
    except Exception as e:
        print(f"Erreur lors de l'ouverture du PDF : {e}")
    
    return word_positions

# Extraction des lignes et rectangles
def extract_graphics(pdf_path):
    graphics_data = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages):
                lines = page.lines
                rects = page.rects
                graphics_data.append((page_number + 1, lines, rects))
    except Exception as e:
        print(f"Erreur lors de l'extraction des graphiques : {e}")
    
    return graphics_data

# Création d'une image combinée
def create_combined_image(pdf_page_width, pdf_page_height, word_positions, graphics_data, page_number):
    # Créer une image blanche
    image = np.ones((pdf_page_height, pdf_page_width, 3), dtype=np.uint8) * 255
    
    # Ajouter les mots
    filtered_words = [word for word in word_positions if word['page_number'] == page_number]
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
    graphics_for_page = next((data for data in graphics_data if data[0] == page_number), None)
    if graphics_for_page:
        _, lines, rects = graphics_for_page
        for line in lines:
            x0, y0, x1, y1 = int(line['x0']), int(line['top']), int(line['x1']), int(line['bottom'])
            cv2.line(image, (x0, y0), (x1, y1), (0, 0, 255), 2)  # Lignes rouges
        
        for rect in rects:
            x0, top, x1, bottom = int(rect['x0']), int(rect['top']), int(rect['x1']), int(rect['bottom'])
            cv2.rectangle(image, (x0, top), (x1, bottom), (0, 255, 0), 2)  # Rectangles verts
    
    return image

# Visualiser une page combinée
def visualize_combined_image(image, page_number):
    cv2.imshow(f'Page {page_number}', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Main
pdf_path = 'KID PRIIPS - Feeder Boscalt - Class C (français).pdf'
page_limit = 3  # Limiter le nombre de pages pour les tests

try:
    # Extraction des données
    word_positions = extract_word_positions(pdf_path, page_limit=page_limit)
    graphics_data = extract_graphics(pdf_path)

    # Dimensions de la page (ajustez en fonction du PDF)
    page_width = 595
    page_height = 842

    # Parcourir les pages et afficher les données combinées
    for page_number in range(1, page_limit + 1):
        combined_image = create_combined_image(page_width, page_height, word_positions, graphics_data, page_number)
        visualize_combined_image(combined_image, page_number)

except Exception as e:
    print(f"Erreur : {e}")
