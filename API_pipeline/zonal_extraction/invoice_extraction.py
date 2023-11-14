
import os
import cv2
import json
import argparse
from zonal_extraction import ZonalExtraction
from preprocessing import ImagePreprocessing
from PIL import Image

# Constants
NEW_WIDTH, NEW_HEIGHT = 1000, 1400
X, Y, WIDTH, HEIGHT = 84, 161, 913 - 84, 1107 - 161
OUTPUT_JSON_FILE = "extracted_text.json"

def extract_invoice_text(image_path, coordinate_file, result_directory_path):
    try:
        extractor = ZonalExtraction()
        image_proc = ImagePreprocessing()

        scanned_invoice = cv2.imread(image_path)
        image = Image.open(image_path)

        # Image preprocessing
        image_proc.check_resolution(image)
        image_proc.check_dimensions(image)
        image_proc.check_clarity(image)
        image_proc.check_noise(image)

        preprocessed_image = image_proc.preprocess_invoice_image(scanned_invoice)
        fixed_image = image_proc.align_image(scanned_invoice)
        resized_image = image_proc.resize_image(fixed_image)
        cropped_image = image_proc.crop_image(resized_image)

        extracted_text = extractor.extract_text_from_image(cropped_image, coordinate_file)

        # Save results
        extracted_text_file = os.path.join(result_directory_path, OUTPUT_JSON_FILE)
        with open(extracted_text_file, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_text, json_file, ensure_ascii=False, indent=4)

        output_json_file_path = os.path.join(result_directory_path, "invoice_components.json")
        result = extractor.process_extracted_text(extracted_text)
        extractor.print_invoice_items(result)


        
        with open(output_json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=4)



        print(f"Result saved to {output_json_file_path}")
        print("Extraction process completed successfully")
    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Invoice Extraction Script")
    parser.add_argument("file_path", type=str, help="Path to the invoice file to process")
    args = parser.parse_args()

    # Directories setup
    script_directory = os.path.dirname(os.path.abspath(__file__))
    coordinate_file = os.path.join(script_directory, "components_coordinates.json")

    result_directory_path = os.path.join(os.getcwd(), 'Result')
    os.makedirs(result_directory_path, exist_ok=True)

    image_extensions = ['.jpg', '.jpeg', '.png']
    pdf_extensions = ['.pdf']
    file_extension = os.path.splitext(args.file_path)[1].lower()

    if not os.path.exists(args.file_path):
        raise FileNotFoundError(f"Error: The file not found at '{args.file_path}'")
    elif not os.path.exists(coordinate_file):
        raise FileNotFoundError(f"Error: JSON file not found at '{coordinate_file}'")
    else:
        if file_extension in image_extensions:
            extract_invoice_text(args.file_path, coordinate_file, result_directory_path)
        elif file_extension in pdf_extensions:
            image_proc = ImagePreprocessing()
            if image_proc.process_pdf(args.file_path, result_directory_path, 600):  # PDF dpi converter
                invoice_image_path = os.path.join(result_directory_path, "Scanned_image.png")
                extract_invoice_text(invoice_image_path, coordinate_file, result_directory_path)
            else:
                print("Problem with PDF converter. Please try again with a valid file.")
        else:
            print("Please provide a valid file path (image or pdf).")

if __name__ == "__main__":
    main()
