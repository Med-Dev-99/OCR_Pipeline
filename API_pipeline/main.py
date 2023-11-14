import requests
import json
import argparse
import os

# API endpoint URL
API_URL = "http://localhost:5000/extract_invoice"

def check_requirements(requirements_file):
    """
    Check if the packages listed in requirements_file are installed.
    """
    with open(requirements_file, 'r') as file:
        requirements = [line.strip() for line in file]

    missing_packages = []
    for requirement in requirements:
        try:
            __import__(requirement)
        except ImportError:
            missing_packages.append(requirement)

    return missing_packages

def extract_invoice_from_api(file_path, invoice_type, chosen_process):
    """
    Send a POST request to the API and get the extraction results.
    """
    # Create a dictionary with the file and form data
    data = {
        'invoice_type': invoice_type,
        'chosen_process': chosen_process,
    }

    # Open and send the file along with the form data
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(API_URL, data=data, files=files)
    return response

def main():
    # Create a command line argument parser
    parser = argparse.ArgumentParser(description='Upload invoice file to OCR API.')
    
    # Add arguments for file path, invoice type, and chosen process
    parser.add_argument('file_path', type=str, help='Path to the invoice file')
    parser.add_argument('invoice_type', type=str, help='Type of invoice')
    parser.add_argument('chosen_process', type=str, help='Chosen process')
    
    # Parse the command line arguments
    args = parser.parse_args()

    # Path to the requirements.txt file
    requirements_file = 'requirements.txt'

    # # Check if required packages are installed
    # missing_packages = check_requirements(requirements_file)

    # if missing_packages:
    #     print(f"Error: The following packages are missing: {', '.join(missing_packages)}")
    #     return

    try:
        # Send a POST request to the API
        response = extract_invoice_from_api(args.file_path, args.invoice_type, args.chosen_process)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            result = response.json()
            
            # Define the default output file path
            output_directory = "Result"
            os.makedirs(output_directory, exist_ok=True)  # Create the directory if it doesn't exist
            output_file_path = os.path.join(output_directory, "invoice_data.json")
            counter = 1
            while os.path.exists(output_file_path):
                output_file_path = f"Result/invoice_data_{counter}.json"
                counter += 1

            # Save the result to a local file
            with open(output_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)

            print(f"Result saved to {output_file_path}")

        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()