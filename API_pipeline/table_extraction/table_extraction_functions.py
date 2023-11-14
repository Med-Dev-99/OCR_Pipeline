import tabula
import ocrmypdf
import re 
from fuzzywuzzy import fuzz
import json
import math
import cv2
import os
import tempfile

class Table_extraction_func:
    def __init__(self) -> None:
        pass


######################################################
################# extraction process from table with tabula 


    def convert_to_searchable_pdf(self,image, output_path):
        """
        Convert an OpenCV image object to a searchable PDF using ocrmypdf.
        """
        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_image:
            temp_image_path = temp_image.name
            # Save the OpenCV image to the temporary file
            cv2.imwrite(temp_image_path, image)
        
        try:
            # Convert the image to a searchable PDF
            ocrmypdf.ocr(temp_image_path, output_path, force_ocr=True, image_dpi=600)
        finally:
            # Remove the temporary image file
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

    def convert_to_searchable_pdf_test(self,image_path, output_path):
        """
        Convert the enhanced image to searchable PDF using ocrmypdf.
        """
        ocrmypdf.ocr(image_path, output_path, force_ocr=True, image_dpi=600)

    def extract_table_from_pdf(self,pdf_path):
        """
        Extract table data from the PDF using tabula.
        """
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
        
        return [table.to_dict(orient='records') for table in tables]


###############################################################################

################### process data ########################3

    def replace_nan(self,data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self.replace_nan(value)
                elif isinstance(value, float) and math.isnan(value):
                    data[key] = "NaN"
        elif isinstance(data, list):
            for i in range(len(data)):
                if isinstance(data[i], (dict, list)):
                    self.replace_nan(data[i])
                elif isinstance(data[i], float) and math.isnan(data[i]):
                    data[i] = "NaN"
        return data


##### usage :
# my_img=cv2.imread("/home/med-dev/Desktop/table_image_data/french_exemple_facture.jpg")
# output_path="/home/med-dev/Desktop/table_image_data/french_exemple_facture_test1.pdf"
# convert_to_searchable_pdf(my_img, output_path)
# table_data = extract_table_from_pdf(output_path)

# new_data=replace_nan(table_data)

###### data is ready to pre process 




# Function to remove specific key-value pairs using regex
    def remove_unwanted_entries(self,data):
        for item in data:
            for entry in item:
                # Check if the key matches the regex pattern and the value is "NaN"
                keys_to_remove = []
                for key, value in entry.items():
                    if re.match(r'^\|\.?\d*$', key) and value.strip().lower() == "nan":
                        keys_to_remove.append(key)
                    if (re.match(r'^Unnamed:\s*\d*$', key) or key == '|') and value.strip().lower() == "nan":
                        keys_to_remove.append(key)
                for key in keys_to_remove:
                    if key in entry:
                        del entry[key]
        return data

    ###### assign value to key

    def is_similar1(self,string, target):
        return fuzz.ratio(str(string).lower(), str(target).lower()) > 80

    def process_data(self,dictionary):
        modified_dict = dictionary.copy()
        
        keys = list(modified_dict.keys())
        for i in range(len(keys) - 1):
            if self.is_similar1(keys[i], "Unnamed") and not self.is_similar1(modified_dict[keys[i]], "NaN") and self.is_similar1(modified_dict[keys[i+1]], "NaN"):
                # Set the next key's value to the current key's value
                modified_dict[keys[i+1]] = modified_dict[keys[i]]
                # Delete the current key-value pair
                del modified_dict[keys[i]]
                break

        return modified_dict

# Apply the function to each block in the test_data
# new_data = [[process_data(item) for item in sublist] for sublist in data]


    def process_result(self,data):
        for item in data:
            # Convert the dictionary items into a list of key-value tuples
            items_list = list(item.items())

            i = 0
            while i < len(items_list) - 1:
                # If two consecutive values are 'NaN'
                if items_list[i][1] == 'NaN' and items_list[i+1][1] == 'NaN':
                    # Remove them from the dictionary
                    del item[items_list[i][0]]
                    del item[items_list[i+1][0]]
                    # Refresh the items list
                    items_list = list(item.items())
                    i = 0  # Reset the loop
                else:
                    i += 1
        return data

## usage :
#new_result = process_result(new_data[0])

    # Function to determine if a key closely resembles "Unnamed" using fuzzy matching
    def resembles_unnamed(self,key):
        return fuzz.partial_ratio("Unnamed", key) > 80  # Adjust the ratio threshold as needed


    def process_main_table(self,data_list):
        
        # Filter out items with keys that closely resemble "Unnamed"
        filtered_data = [{key: value for key, value in item.items() if not self.resembles_unnamed(key)} for item in data_list]

        return filtered_data

# Filter out items with keys that closely resemble "Unnamed"
#filtered_data = [{key: value for key, value in item.items() if not resembles_unnamed(key)} for item in new_result]



    # Function to group dictionaries with the same keys
    def group_dicts_by_keys(self,data):
        grouped_data = []
        current_group = []

        for item in data:
            if not current_group or set(current_group[0].keys()) == set(item.keys()):
                current_group.append(item)
            else:
                grouped_data.append(current_group)
                current_group = [item]

        if current_group:
            grouped_data.append(current_group)

        return grouped_data

# # Group dictionaries with the same keys
# grouped_data = group_dicts_by_keys(filtered_data)



# # Find the longest list from the grouped data
# table_data = max(grouped_data, key=len)



# # Find the longest list from the grouped data
# total_table_data = min(grouped_data, key=len)



# Function to remove items containing "|"
    def remove_items_with_pipe(self,dictionary):
        return {key: value for key, value in dictionary.items() if '|' not in str(value)}

    # Remove items containing "|" from each dictionary
    #filtered_data = [remove_items_with_pipe(dct) for dct in total_table_data]

    # Function to group items in dictionaries
    def group_items(self,dictionary):
        grouped_items = {}
        items = list(dictionary.items())
        for i in range(0, len(items), 2):
            if i + 1 < len(items):
                key = items[i][1]
                value = items[i + 1][1]
                grouped_items[key] = value
        return grouped_items

# Group items in each dictionary
#grouped_dicts = [group_items(dct) for dct in same_length_dicts]

# Print the grouped dictionaries
# for grouped_dict in grouped_dicts:
#     print(grouped_dict)
## result : {'Total': 3470}
##{'TVA 20%': 694}
##{'Total TTC': 4164} 

# Function to check if there's an item with a value similar to "Total"
    def has_value_similar_to_total(self,dictionary):
        for value in dictionary.values():
            if isinstance(value, str) and "Total" in value:
                return True
        return False

    # Check if there are at most two items and one with a value similar to "Total"
    def total_check(self, filtered_data):
        for dct in filtered_data:
            if len(dct) <= 2 and self.has_value_similar_to_total(dct):
                keys = list(dct.keys())
                values = list(dct.values())
                new_item = {values[0]: values[1]}
                filtered_data.remove(dct)  # Remove the original dictionary
                filtered_data.append(new_item)  # Add the new item
        return filtered_data
    
    def merge_data(self,list1,list2):
            # Decode Unicode escape sequences in the second list
        for item in list2:
            for key, value in item.items():
                if isinstance(value, str):
                    item[key] = value.encode('latin1').decode('unicode_escape')

        for item in list1:
            for key, value in item.items():
                if isinstance(value, str):
                    item[key] = value.encode('latin1').decode('unicode_escape')

        # Merge the two lists into a single dictionary
        merged_data = {
            'Invoice payment': list1,
            'Items': list2
        }

        # Convert the dictionary to JSON format
        import json
        json_output = json.dumps(merged_data, indent=4, ensure_ascii=False)
        return json_output


