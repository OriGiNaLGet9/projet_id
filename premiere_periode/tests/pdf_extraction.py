import pdfplumber
import cv2
import numpy as np

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

def visualize_word_positions_opencv(word_positions, page_number, pdf_page_width, pdf_page_height):
    # Créer une image blanche de la taille de la page PDF
    image = np.ones((pdf_page_height, pdf_page_width, 3), dtype=np.uint8) * 255
    
    # Filtrer les mots pour la page spécifiée
    filtered_words = [word for word in word_positions if word['page_number'] == page_number]
    
    for word in filtered_words:
        # Dessiner un rectangle autour du mot
        top_left = (int(word['x0']), int(word['top']))
        bottom_right = (int(word['x1']), int(word['bottom']))
        cv2.rectangle(image, top_left, bottom_right, (0, 0, 255), 1)
        
        # Calculer la taille du texte à afficher
        rect_height = int(word['bottom'] - word['top'])
        font_scale = rect_height / 30.0  # Ajuster cette valeur selon les besoins pour une taille de texte correcte
        font_thickness = 1
        
        # Ajouter le texte à l'intérieur du rectangle
        # Ajouter le texte à l'intérieur du rectangle
        text_color = (0, 0, 0)  # Noir pour le texte
        text_position = (int(word['x0']), int((word['top'] + word['bottom']) / 2))  # Centrer le texte verticalement
        
        cv2.putText(image, word['text'], text_position, 
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness, cv2.LINE_AA)
    
    # Afficher l'image avec OpenCV
    cv2.imshow(f'Page {page_number}', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Utilisation de la fonction
pdf_path = 'KID PRIIPS - Feeder Boscalt - Class C (français).pdf'
positions = extract_word_positions(pdf_path, page_limit=3)  # Limiter l'extraction à la première page

# Afficher les positions des mots sur la page 1
if positions:
    page_width = 595  # Valeur par défaut pour un A4 (PDF)
    page_height = 842  # Valeur par défaut pour un A4 (PDF)
    for page in range(3):
        visualize_word_positions_opencv(positions, page_number=page+1, pdf_page_width=page_width, pdf_page_height=page_height)