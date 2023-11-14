import os
import cv2
from flask import Flask, request, jsonify
import shutil

# Local imports
from zonal_extraction.zonal_extraction import ZonalExtraction
from image_preprocessing.preprocessing import ImagePreprocessing
from invoice_data_extraction import Invoice_data_extraction
from table_extraction.extract_table_data import Extract_table_data
# Constants and configurations
UPLOAD_FOLDER = 'static/uploads'
COORDINATE_FILE = "coordinates/coordinates.json"
ARABIC_WORDS_COORDS = "coordinates/arabic_coordinates.json"
PDF_DPI = 600

LEFT_COORDINATES = [
    {
        "top_left": [
            4,
            2
        ],
        "bottom_right": [
            412,
            546
        ]
    }
]
RIGHT_COORDINATES = [
    {
        "top_left": [
            414,
            3
        ],
        "bottom_right": [
            826,
            548
        ]
    }
]
BOTTOM_COORDINATES = [
    {
        "top_left": [
            6,
            611
        ],
        "bottom_right": [
            824,
            940
        ]
    }
]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Instances
invoice_data_extraction = Invoice_data_extraction()
extractor = ZonalExtraction()
image_proc = ImagePreprocessing()
extract_tab_data=Extract_table_data()

def clear_directory(directory_path):
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f'Failed to delete {item_path}. Reason: {e}')
def process_image(file_path, chosen_process, invoice_type):

    if chosen_process == "zonal_extraction":
        # Read the image file
        image = cv2.imread(file_path)
        enhanced_image = invoice_data_extraction._image_preprocessing(image)
        if enhanced_image is None:
            return jsonify({"error": "Image preprocessing failed."}), 500  # Handle None gracefully
        response_data_zonal = invoice_data_extraction.zonal_extraction(enhanced_image, COORDINATE_FILE, invoice_type, chosen_process, extractor)
        directory_path = 'static/uploads'
        clear_directory(directory_path)
        return jsonify(response_data_zonal)

    elif chosen_process == "native_extraction":
        # Read the image file
        image = cv2.imread(file_path)
        enhanced_image = invoice_data_extraction._image_preprocessing(image)
        if enhanced_image is None:
            return jsonify({"error": "Image preprocessing failed."}), 500  # Handle None gracefully
        native_response_data = invoice_data_extraction.extract_data_from_image(enhanced_image, ARABIC_WORDS_COORDS, LEFT_COORDINATES, RIGHT_COORDINATES, BOTTOM_COORDINATES, invoice_type, chosen_process)
        directory_path = 'static/uploads'
        clear_directory(directory_path)
        return jsonify(native_response_data)

    elif chosen_process == "ner_extraction":
        # Read the image file
        image = cv2.imread(file_path)
        enhanced_image = invoice_data_extraction._image_preprocessing_ner(image)
        if enhanced_image is None:
            return jsonify({"error": "Image preprocessing failed."}), 500  # Handle None gracefully
        ner_response_data = invoice_data_extraction.ner_spacy_extraction(enhanced_image, invoice_type, chosen_process)
        directory_path = 'static/uploads'
        clear_directory(directory_path)
        return jsonify(ner_response_data)
    elif chosen_process == "table_extraction":
        image = cv2.imread(file_path)
        enhanced_image = invoice_data_extraction._image_preprocessing_ner(image)
        if enhanced_image is None:
            return jsonify({"error": "Image preprocessing failed."}), 500  # Handle None gracefully
        table_data=extract_tab_data.extract_tab(enhanced_image,file_path)
        directory_path = 'static/uploads'
        clear_directory(directory_path)
        return jsonify(table_data)
         

@app.route('/extract_invoice', methods=['POST'])
def extract_invoice():
    try:
        # Check for file in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'error': 'No selected file'})

        # Retrieve the parameters
        invoice_type = request.form['invoice_type']
        chosen_process = request.form['chosen_process']

        # Save the uploaded file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
        print(file_path)
        #jsonify({file_path})

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension in ['.jpg', '.jpeg', '.png']:
            return process_image(file_path, chosen_process, invoice_type)

        elif file_extension == '.pdf':
            if image_proc.process_pdf(file_path, app.config['UPLOAD_FOLDER'], PDF_DPI):

                invoice_image_path = os.path.join(app.config['UPLOAD_FOLDER'], "Scanned_image.png")
                invoice_image = cv2.imread(invoice_image_path)
                #jsonify({invoice_image_path})
                print(invoice_image_path)
                return process_image(invoice_image_path, chosen_process, invoice_type)
            else:
                return jsonify({"error": "There's a problem with PDF conversion. Please try again with a valid file."}), 400

        else:
            return jsonify({"error": "Please provide a valid file (image or PDF)."}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
