import os
import spacy
from spaczz.pipeline import SpaczzRuler
from spacy.matcher import Matcher
from pyarabic.araby import is_arabicword
from spacy.language import Language
import re
import pytesseract

# Register the SpaczzRuler component with spaCy
@Language.factory("custom_spaczz_ruler")
def create_spaczz_ruler(nlp, name):
    return SpaczzRuler(nlp)

class DocumentProcessor:
    
    def __init__(self):
        print("Initializing DocumentProcessor...")
        self.patterns = [
            {"label": "SHIP_NAME", "pattern": [{"TEXT": {"REGEX": "(MS\s)?[A-Z][a-z]+"}}, {"TEXT": {"REGEX": "[A-Z][a-z]*"}, "OP": "?"}]},
            {"label": "IMO_CODE", "pattern": [{"TEXT": {"REGEX": "IMO\s*\d{5,7}[A-Z]+"}}]}, 
            {"label": "SWIFT", "pattern": [{"TEXT": {"REGEX": "[A-Z0-9]{8,11}"}}]},
            {"label": "BIC", "pattern": [{"TEXT": {"REGEX": "[A-Z0-9]{8,12}"}}]},
            {"label": "PORT", "pattern": [{"LOWER": "port"}, {"LOWER": "de"}, {"TEXT": {"REGEX": "[A-Z][a-z]+(\s[A-Z][a-z]+)*"}}]}
        ]

        self.nlp = self.load_spacy_model()
        print("spaCy model loaded.")
        
        self.matcher = Matcher(self.nlp.vocab)
        print("Matcher initialized.")
        self._setup_spacy_matcher()
        self._setup_spacy_pipeline()

    @staticmethod
    def load_spacy_model():
        # Path to your trained model 
        model_path = "./ner_model_fr"
        
        # Check if the model folder exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model folder '{model_path}' not found.")
        
        nlp = spacy.load(model_path)
        return nlp
    
    def _setup_spacy_matcher(self):
        for pattern in self.patterns:
            self.matcher.add(pattern["label"], [pattern["pattern"]])

    def _setup_spacy_pipeline(self):
        # Use the registered name when adding the component to the pipeline
        self.nlp.add_pipe("custom_spaczz_ruler", before="ner")

    def extract_text_from_image(self, image):
        
        extracted_text = pytesseract.image_to_string(image, lang='fra')
        output_filename="/home/med-dev/Desktop/ner_extracted_text.txt"
        with open(output_filename, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)

        return extracted_text

    def remove_arabic(self, text):
        return ' '.join(word for word in text.split() if not is_arabicword(word))

    def clean_text(self, text):
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text

    def extract_entities(self, text):
        doc = self.nlp(text)
        matches = self.matcher(doc)
        entities_dict = {}
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            entities_dict[label] = span.text
        return entities_dict
    
    def process(self, image_path):
        text = self.extract_text_from_image(image_path)
        print("here's the text")
        print(text)
        text = self.remove_arabic(text)
        #text = self.clean_text(text)
        entities_dict = self.extract_entities(text)
        return entities_dict
