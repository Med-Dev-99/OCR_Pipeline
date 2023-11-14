import cv2
import json
import pytesseract
from PIL import Image
import os
import re


class ZonalExtraction:
    TESSERACT_CONFIG = "--oem 1 --psm 6 -l eng+ara+fre"

    COMPONENT_LIST = ["IMPORTATEUR", "Téléphone", "N° R.C", "Centre RC", "Adresse", "Identifiant fiscal",
                               "Taxe Professionnelle", "Courrier électronique", "EXPEDITEUR", "Bureau douanier",
                               "Montant total", "FOB", "Fret", "Pays d'origine", "Modalités de paiement",
                               "Pays de provenance", "Conditions de livraison", "N° de nomenclature douanière",
                               "Régime douanier", "Désignation commerciale de la marchandise", "Poids net",
                               "Unités complémentaires", "Date, cachet et signature de l'importateur",
                               "N° et date d'enregistrement(2)", "Validité Du:", "Validité Au:",
                               "Avis de département technique", "Décision du Ministère Chargé du Commerce Extérieur",
                               "البنك المعين موطن الوفاء لديه", "Numéro du RIB bancaire", "Banque", "N° de domiciliation",
                               "رمز المكتب", "الرقم وتواريخ الإقرار القريد للسلع", "تاريخ التقييد", "الكمية", "القيمة"]


    def __init__(self):
        pass

    @staticmethod
    def _load_json(json_file_path):
        """Load JSON data from a given path."""
        if not os.path.isfile(json_file_path):
            raise FileNotFoundError(f"JSON file not found at '{json_file_path}'")
        
        with open(json_file_path, 'r') as json_file:
            return json.load(json_file)

    def extract_text_from_image(self, preprocessed_image, json_file_path):
        box_coordinates = self._load_json(json_file_path)
        extracted_text_dict = {}

        for idx, box in enumerate(box_coordinates):
            cropped_image_rgb = self._crop_image_using_box(preprocessed_image, box)
            recognized_text = self._extract_text_from_cropped_image(cropped_image_rgb)
            extracted_text_dict[f"box_{idx}"] = recognized_text.strip()

        return extracted_text_dict

    @staticmethod
    def _crop_image_using_box(image, box):
        top_left, bottom_right = tuple(box["top_left"]), tuple(box["bottom_right"])
        cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        if cropped_image is None or cropped_image.size == 0:
            raise ValueError("Cropped image is empty")

        return cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB)

    @classmethod
    def _extract_text_from_cropped_image(cls, cropped_image_rgb):
        return pytesseract.image_to_string(Image.fromarray(cropped_image_rgb), config=cls.TESSERACT_CONFIG)

    def process_extracted_text(self, extracted_text_dic):
        return {
            comp: self._clean_text(extracted_text_dic.get(f"box_{idx}", "sans"), idx)
            for idx, comp in enumerate(self.COMPONENT_LIST)
        }

    @staticmethod
    def _clean_text(text, idx):
        text = text.strip()
        
        if idx == 26 and re.match(r'^\s*[a-zA-Z0-9\s\n;:]+\s*$', text):
            return "sans"
        if not re.search(r'[a-zA-Z0-9]', text) or len(re.findall(r'[a-zA-Z0-9]', text)) <= 1:
            return "sans"
        
        return text

    @staticmethod
    def print_invoice_items(result):
        for component, value in result.items():
            print(f"{component}: {value}")


