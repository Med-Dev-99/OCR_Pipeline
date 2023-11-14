import cv2
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR
import re
from fuzzywuzzy import process, fuzz
from typing import List, Tuple, Dict, Union


class PaddleOCR_Extraction_Process:


    @staticmethod
    def apply_mask_to_image(image, coordinates):
        masked_image = np.copy(image)
        for box in coordinates:
            top_left = tuple(box['top_left'])
            bottom_right = tuple(box['bottom_right'])
            cv2.rectangle(masked_image, top_left, bottom_right, (255, 255, 255), -1)  # Create a white mask
        
        return masked_image

    @staticmethod
    def crop_image(image, coordinates):

        # Assuming there's only one set of coordinates in the list
        box = coordinates[0]
        top_left = tuple(box['top_left'])
        bottom_right = tuple(box['bottom_right'])

        # Crop the image using OpenCV
        cropped_image = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

        return cropped_image

    @staticmethod
    def perform_ocr(image):

        ocr = PaddleOCR()
        result = ocr.ocr(image)

        extracted_text = []
        for line in result[0]:
            extracted_text.append(line[1][0])

        return extracted_text 
    
    # Helper function: Extract items using fuzzy match and a threshold
    @staticmethod
    def short_comp_process_left(extracted_text_left):
        # Find and remove "Montanttotalendevises"
        if "Montanttotalendevises" in extracted_text_left:
            extracted_text_left.remove("Montanttotalendevises")

        # Initialize a new list to store the removed items
        new_list = []

        # Items to search for and remove
        components_list = ['NR.C', 'CentreR.C', 'Montant total', 'FOB', 'Fret']

        # Iterate through the original list
        index = 0
        while index < len(extracted_text_left):
            item = extracted_text_left[index]
            for search_item in components_list:
                if search_item in item:

                    # Add it to the new list
                    new_list.append(item)
                    
                    # If the item contains one of the search items, remove it from the original list
                    extracted_text_left.pop(index)

                    # Decrement the index to account for the removed item
                    index -= 1
                    break
            index += 1
        
        # Initialize a dictionary to store component-value pairs
        component_dict = {}

        # Iterate through the data list
        for item in new_list:
            # Regular expression pattern to match component names from the components list
            pattern = r'(' + '|'.join(re.escape(component) for component in components_list) + r')'
            # Split the item using the pattern
            components = re.split(pattern, item)
            # Remove empty strings from the resulting list
            components = [component.strip() for component in components if component.strip()]
            # If there are exactly two components (name and value)
            if len(components) == 2:
                # Extract component name and value
                component_name, component_value = components
                # Add to the dictionary
                component_dict[component_name] = component_value

        return component_dict,extracted_text_left


    @staticmethod
    def component_extraction(original_list, similarity_threshold=70):
        
        # components to find 
        components_to_find = ['IMPORTATEUR', 'Telephone', 'EXPEDITEUR', 'Modalites de paiement', 'Conditions de livraison', 'Designation commerciale de la marchandise']
        # Initialize a dictionary to store component-value pairs
        component_dict = {}

        # Initialize a variable to store the current component
        current_component = None

        # Iterate through the original list
        while original_list:
            item = original_list.pop(0)

            # Find the component with the highest fuzz ratio
            best_match = max(components_to_find, key=lambda component: fuzz.ratio(component.lower(), item.lower()))
            
            # If the best match has a reasonable similarity (adjust the threshold as needed)
            if fuzz.ratio(best_match.lower(), item.lower()) > similarity_threshold:
                # Set the current component
                current_component = best_match
                # Initialize a variable to store the component's value with spaces
                component_value = ""
                # Continue collecting values until the next component is found
                while original_list:
                    next_item = original_list.pop(0)
                    if any(fuzz.ratio(component.lower(), next_item.lower()) > similarity_threshold for component in components_to_find):
                        original_list.insert(0, next_item)  # Put back the item that doesn't belong to the current component
                        break
                    # Add a space if the component value is not empty
                    if component_value:
                        component_value += " "
                    component_value += next_item
                # Assign the collected component value to the current component in the dictionary
                component_dict[current_component] = component_value
                # Reset the current component
                current_component = None

        return component_dict
    
    ##### top right data 
    @staticmethod
    def extract_first_items_right(extracted_data):

        # Define the components to search for
        components_to_search = ['ldentifiant fiscal', 'Taxe Professionnelle']

        # Initialize a list to store the extracted items
        extracted_items = []

        # Iterate through the data list
        for item in extracted_data:
            # Find the best match from the components to search list using fuzzy matching
            best_match, score = process.extractOne(item, components_to_search, scorer=fuzz.token_set_ratio)
            
            # If the score is above a certain threshold (adjust as needed)
            if score > 70:
                # Add the matched item to the list of extracted items
                extracted_items.append(item)

        # Remove the extracted items from the original list
        original_list = [item for item in extracted_data if item not in extracted_items]
        return extracted_items,original_list

    def process_identif(datalist):

        # Define the component names to search for
        component_names_to_search = ['ldentifiant fiscal', 'Taxe Professionnelle']

        # Initialize a dictionary to store component-value pairs
        component_dict = {}

        # Iterate through the original list
        for item in datalist:
            # Initialize variables for component and value
            current_component = None
            component_value = None

            # Iterate through component names and find the best match
            for component in component_names_to_search:
                ratio = fuzz.ratio(component.lower(), item.lower())
                if ratio > 70:
                    matched_part = component.lower().replace(" ", "")
                    rest_part = item.lower().replace(" ", "")
                    if matched_part in rest_part:
                        current_component = component
                        component_value = rest_part.replace(matched_part, '').strip() or 'sans'
                        break

            # Add to the dictionary if both component and value are identified
            if current_component and component_value:
                component_dict[current_component] = component_value
        
        return component_dict
    @staticmethod
    def second_process_right(original_list):
        
        # Define the list of components to search for
        components_to_find = ['Adresse', 'ldentifiant fiscal', 'TaxeProfessionnelle', 'Courrierelectronique', 'Bureau douanier', "Pays d'origine", 'Paysdeprovenance', 'N°de nomenclature douaniere', 'Regime douanier', 'Poids net', 'Unites complementaires']
        
        # Initialize a dictionary to store component-value pairs
        component_dict = {}

        # Initialize a variable to store the current component
        current_component = None

        # Initialize a list to store the remaining items after extraction
        remaining_items = []

        # Iterate through the original list
        index = 0
        while index < len(original_list):
            item = original_list[index]

            # Find the component with the highest fuzz ratio
            best_match = max(components_to_find, key=lambda component: fuzz.ratio(component.lower(), item.lower()))

            # If the best match has a reasonable similarity (adjust the threshold as needed)
            if fuzz.ratio(best_match.lower(), item.lower()) > 70:
                # Set the current component
                current_component = best_match
                # Initialize a variable to store the component's value with spaces
                component_value = ""
                # Move to the next item
                index += 1
                # Continue collecting values until the next component is found
                while index < len(original_list):
                    next_item = original_list[index]
                    if any(fuzz.ratio(component.lower(), next_item.lower()) > 70 for component in components_to_find):
                        break
                    # Add a space if the component value is not empty
                    if component_value:
                        component_value += " "
                    component_value += next_item
                    index += 1
                # Assign the collected component value to the current component in the dictionary
                component_dict[current_component] = component_value
                # Reset the current component
                current_component = None
            else:
                # Add the item to the list of remaining items
                remaining_items.append(item)
                # Move to the next item
                index += 1


        return component_dict
    
    ######## bottom part 

    @staticmethod
    def extract_bottom_right(data_item, similarity_threshold=80):
        def clean_text(text):
            return re.sub(r"\s+", " ", text).lower().strip()

        key_value_dict = {}
        keys_to_find = ['Du:', 'Au:', 'Banque', 'Ndedomiciliation', 'Numerodu RIBbancaire']
        cleaned_keys = [clean_text(key) for key in keys_to_find]

        index = 0
        while index < len(data_item):
            item = data_item[index]
            cleaned_item = clean_text(item)
            
            # Find the best match in keys_to_find based on similarity ratio
            best_match, score = process.extractOne(cleaned_item, cleaned_keys, scorer=fuzz.ratio)
            
            if score > similarity_threshold:
                # If the item is similar to one of the keys, extract the key and the next value
                key = keys_to_find[cleaned_keys.index(best_match)]
                value = data_item[index + 1] if index + 1 < len(data_item) else None
                
                # Add the key-value pair to the dictionary
                key_value_dict[key] = value
                
                # Remove the key and value from the original list
                data_item.pop(index)  # Remove the key
                if index < len(data_item):  # Check if the index is still within the bounds of the list
                    data_item.pop(index)  # Remove the value
            else:
                index += 1

        return key_value_dict, data_item
    
    @staticmethod
    def separate_table_data(input_list, key_string='IMPUTATIONSDOUANIERES', similarity_threshold=90):
        def clean_text(text):
            return re.sub(r"\s+", " ", text).lower().strip()

        cleaned_input = [(index, clean_text(item)) for index, item in enumerate(input_list)]
        cleaned_key_string = clean_text(key_string)

        # Find the best match in the input list based on similarity ratio
        best_match = process.extractOne(
            cleaned_key_string,
            [text for index, text in cleaned_input],
            scorer=lambda a, b: fuzz.ratio(a, b),
            score_cutoff=similarity_threshold
        )

        if best_match:
            best_match_string, score = best_match
            index_of_imputation = next(index for index, text in cleaned_input if text == best_match_string)
            table_data = input_list[index_of_imputation + 1:]
            cleaned_list = input_list[:index_of_imputation]
        else:
            print(f"'{key_string}' not found in the list based on the similarity threshold.")
            table_data = []
            cleaned_list = input_list

        return cleaned_list, table_data
    
    @staticmethod
    def table_process(table_data):
        # Labels for the 6 columns
        labels = ["رمز", "رمز المكتب", "الرقم وتواريخ الإقرار القريد للسلع", "تاريخ التقييد", "الكمية", "القيمة"]

        # Determine the number of rows based on the length of the data and the number of columns
        num_columns = len(labels)
        num_rows = len(table_data) // num_columns

        # Create a dictionary to store the data
        data_dict = {}

        # Assign the data to their corresponding labels
        for i in range(num_rows):
            row_data = table_data[i * num_columns: (i + 1) * num_columns]
            row_dict = dict(zip(labels, row_data))
            data_dict[f"data Row {i + 1}"] = row_dict
        
        return data_dict

    @staticmethod
    def get_N_enrg(data_list):
        # Define a flexible regex pattern to match date-like strings
        pattern = r'\d{1,4}[/.-]\d{1,2}[/.-]\d{2,4}'

        # Initialize a dictionary to store key-value pairs
        key_value_dict = {}

        # Initialize a list to store matched items to be removed
        items_to_remove = []

        # Iterate through the cleaned list
        for item in data_list:
            if re.search(pattern, item):
                # If the item matches the pattern, add it to the dictionary
                key_value_dict["numero et date"] = item
                # Add the item to the list of items to remove
                items_to_remove.append(item)
            elif item == "Net date d'enregistrement(2)":
                # Handle "Net date d'enregistrement(2)" by adding it to the list of items to remove
                items_to_remove.append(item)

        # Remove the matched items and "Net date d'enregistrement(2)" from the cleaned list
        for item in items_to_remove:
            data_list.remove(item)
        return key_value_dict,data_list

    @staticmethod
    def remove_similar_strings(input_list, similarity_threshold=80):

        strings_to_remove = ["N et date d'enregistrement（2)", 'Validite(2)', 'Avis du Departement Technique', 'Decision du Ministere Charge du Commerce Exterieur']
        def clean_text(text):
            # Replace multiple spaces with a single space, convert to lowercase, and strip leading/trailing whitespace
            return re.sub(r"\s+", " ", text).lower().strip()

        cleaned_strings_to_remove = [clean_text(item) for item in strings_to_remove]
        remaining_strings = []
        bank={}

        for item in input_list:
            cleaned_item = clean_text(item)
            best_match, score = process.extractOne(cleaned_item, cleaned_strings_to_remove, scorer=fuzz.ratio)
            
            if score < similarity_threshold:
                remaining_strings.append(item)
        bank["البنك المعين موطن الوفاء لديه"]=remaining_strings[0]
        return bank
