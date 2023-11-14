# OCR Pipeline Project - API_pipline

Welcome to the OCR Pipeline project! This project is designed to automate the text extraction process from invoices through an OCR pipeline. The pipeline comprises four main components and is exposed via a RESTful API using Flask.

## Components

1. **Image Pre-processing**: Enhance the quality of scanned invoices to prepare them for OCR.
2. **Segmentation and Text Extraction**: Crop the processed image into three parts for easier text processing, then use PaddleOCR to extract text from each segment and process the extracted text.
3. **Region of Interest (ROI) Extraction**: Extract text from defined boxes using PyTesseract and return a dictionary containing components and their values.
4. **Named Entity Recognition (NER)**: Use Spacy with transformers to extract data from non-structured text.

## Project Architecture

The project is organized as follows:

- **API_pipline**: Main project folder
  - **coordinates**: Contains JSON files with coordinates used in ROI and for applying a white mask.
  - **image_preprocessing**: Contains functions to enhance image quality.
  - **native_extraction**: Implements text extraction using PaddleOCR and processes the extracted text.
  - **spacy_ner_extraction**: Contains the main class for the NER extraction process using Spacy-transformer.
  - **zonal_extraction**: Implements the ROI extraction process using coordinates.
  - **static/uploads**: Manages uploaded files from the endpoint.
  - **app.py**: Flask application runner.
  - **main.py**: Script to request and use the API.
  - **requirements.txt**: Lists the required packages.

## Installation

First, make sure you are in the main folder `API_pipline`, then install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

1. Start the Flask API:

    ```bash
    python app.py
    ```

2. To consume the API, run:

    ```bash
    python main.py <file_path> <invoice_type> <chosen_process>
    ```

   Replace `<file_path>`, `<invoice_type>`, and `<chosen_process>` with the appropriate values.

## API Endpoint

The API exposes the following endpoint:

- **POST /{file, process, document_type}**: Uploads a file, specifies the processing type, and sets the document type.

## Output

The result of the extraction process will be saved automatically as a JSON file on your local machine. If you wish to disable this feature, you can do so by modifying the `main.py` file.

## File Formats

The API accepts both image and PDF files. If a PDF file is uploaded, it will be converted to an image before processing.

## Conclusion

This project aims to provide a comprehensive and automated solution for extracting text from invoices, making it easier and more efficient to retrieve valuable information. Enjoy using the OCR Pipeline!