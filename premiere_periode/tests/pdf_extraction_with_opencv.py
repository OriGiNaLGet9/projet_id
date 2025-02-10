import pdfplumber
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def pdf_page_to_image(page, scale=2):
    # Convertir la page PDF en image à une résolution plus élevée
    pdf_image = page.to_image(resolution=scale * 72)
    im = np.array(pdf_image.original)
    return im, pdf_image

def detect_table_borders_in_image(image):
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Appliquer un seuil binaire inversé pour isoler les lignes
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    # Détection des lignes horizontales
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Détection des lignes verticales
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Combiner les lignes horizontales et verticales
    table_borders = cv2.addWeighted(horizontal_lines, 1, vertical_lines, 1, 0)

    # Trouver les contours des lignes
    contours, _ = cv2.findContours(table_borders, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    return contours

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

def cv2_to_pil(cv2_image):
    """Convertir une image OpenCV en image PIL."""
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

def pil_to_cv2(pil_image):
    """Convertir une image PIL en image OpenCV."""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def add_text_with_pillow(image, text, position, font_size):
    """Ajouter du texte avec Pillow à la position donnée."""
    pil_image = cv2_to_pil(image)
    draw = ImageDraw.Draw(pil_image)

    # Charger une police compatible avec les caractères spéciaux
    font = ImageFont.load_default()

    # Dessiner le texte
    draw.text(position, text, font=font, fill=(0, 0, 0))

    return pil_to_cv2(pil_image)

def create_blank_image(width, height):
    # Créer une image blanche de la taille spécifiée
    return np.ones((height, width, 3), dtype=np.uint8) * 255

def pdf_to_img_coords(x_pdf, y_pdf, page_width, page_height, image_width, image_height):
    """Convertir les coordonnées PDF en coordonnées d'image."""
    x_img = x_pdf * (image_width / page_width)
    y_img = image_height - (y_pdf * (image_height / page_height))
    return x_img, y_img

def visualize_word_positions_on_blank_image(blank_image, word_positions, page_number, page_width, page_height, image_width, image_height):
    filtered_words = [word for word in word_positions if word['page_number'] == page_number]

    for word in filtered_words:
        # Convertir les coordonnées PDF en coordonnées d'image
        x0_img, y0_img = pdf_to_img_coords(word['x0'], word['top'], page_width, page_height, image_width, image_height)
        x1_img, y1_img = pdf_to_img_coords(word['x1'], word['bottom'], page_width, page_height, image_width, image_height)

        # Coordonner pour le rectangle
        top_left = (int(x0_img), int(y1_img))
        bottom_right = (int(x1_img), int(y0_img))

        # Dessiner un rectangle autour du mot
        cv2.rectangle(blank_image, top_left, bottom_right, (0, 0, 255), 2)

        # Ajouter le texte avec Pillow
        text_position = (int(x0_img), int(y0_img)-10)
        font_size = 12  # Ajuster si nécessaire
        blank_image = add_text_with_pillow(blank_image, word['text'], text_position, font_size)

    return blank_image

def draw_detected_borders_on_blank_image(blank_image, contours):
    # Dessiner les bordures détectées sur l'image blanche
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 or h > 50:
            top_left = (x, y)
            bottom_right = (x + w, y + h)
            cv2.rectangle(blank_image, top_left, bottom_right, (0, 255, 0), 2)  # Rectangle vert

    return blank_image

# Utilisation de la fonction
pdf_path = 'KID PRIIPS - Feeder Boscalt - Class C (français).pdf'

# Charger la première page en image avec l'échelle
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[0]
    image, pdf_image = pdf_page_to_image(page)

# Obtenir les dimensions de l'image et de la page
image_height, image_width = image.shape[:2]
page_width, page_height = page.width, page.height

# Extraire les positions des mots
positions = extract_word_positions(pdf_path, page_limit=1)

# Créer une image blanche de la même taille que l'image
blank_image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255

# Détecter les bordures de tableau et lignes visuelles
contours = detect_table_borders_in_image(image)

# Visualiser les bordures détectées et les mots
image_with_borders = draw_detected_borders_on_blank_image(blank_image.copy(), contours)
image_with_words_and_borders = visualize_word_positions_on_blank_image(
    image_with_borders, positions, page_number=1, 
    page_width=page_width, page_height=page_height, 
    image_width=image_width, image_height=image_height
)

# Afficher l'image finale avec OpenCV
cv2.imshow('PDF with Table Borders and Words', image_with_words_and_borders)
cv2.waitKey(0)
cv2.destroyAllWindows()