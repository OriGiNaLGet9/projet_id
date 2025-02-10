import pdfplumber
import cv2
import numpy as np

def extract_graphics(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        graphics_data = []
        
        for page_number in range(len(pdf.pages)):
            page = pdf.pages[page_number]
            # Récupérer les lignes et formes graphiques
            lines = page.lines
            rects = page.rects
            
            graphics_data.append((page_number, lines, rects))
        
        return graphics_data

def create_image_from_graphics(width, height, lines, rects):
    # Créer une image blanche
    image = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Dessiner les lignes
    for line in lines:
        x0, y0, x1, y1 = int(line['x0']), int(line['top']), int(line['x1']), int(line['bottom'])
        cv2.line(image, (x0, y0), (x1, y1), (0, 0, 255), 2)  # Lignes rouges
    
    # Dessiner les rectangles
    for rect in rects:
        x0, top, x1, bottom = int(rect['x0']), int(rect['top']), int(rect['x1']), int(rect['bottom'])
        cv2.rectangle(image, (x0, top), (x1, bottom), (0, 255, 0), 2)  # Rectangles verts
    
    return image

def visualize_graphics(image, page_number):
    # Afficher l'image avec OpenCV
    cv2.imshow(f'Graphics on Page {page_number + 1}', image)  # page_number + 1 pour afficher le numéro de page correct
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Utilisation de la fonction
pdf_path = 'KID PRIIPS - Feeder Boscalt - Class C (français).pdf'

try:
    # Extraire les éléments graphiques de toutes les pages
    graphics_data = extract_graphics(pdf_path)

    # Définir les dimensions de la page PDF (ajustez en fonction de votre PDF)
    page_width = 595  # Largeur A4 par défaut
    page_height = 842  # Hauteur A4 par défaut

    # Parcourir chaque page et visualiser les graphiques
    for page_number, lines, rects in graphics_data:
        # Créer une image à partir des graphiques
        image = create_image_from_graphics(page_width, page_height, lines, rects)

        # Visualiser les graphiques sur l'image
        visualize_graphics(image, page_number)

except Exception as e:
    print(f"Erreur : {e}")
