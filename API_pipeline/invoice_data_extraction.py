import cv2
from image_preprocessing.preprocessing import ImagePreprocessing
from spacy_ner_extraction.ner_process import DocumentProcessor
from zonal_extraction.zonal_extraction import ZonalExtraction
from native_extraction.paddleOCR_extraction_process import PaddleOCR_Extraction_Process
from native_extraction.native_data_process import Native_Process_Extraction
import numpy as np
import traceback
import sys
class Invoice_data_extraction:
    
    def __init__(self):
        #self.paddle_process = PaddleOCR_Extraction_Process()
        self.document_processor = DocumentProcessor()
        self.extractor=ZonalExtraction()
        self.image_proc=ImagePreprocessing()
        self.native_process=Native_Process_Extraction()


    def extract_data_from_image(self, cropped_image, arabic_coordinates, left_coordinates, right_coordinates, bottom_coordinates, invoice_type, chosen_process):
        try:
            
            masked_image = self.native_process.mask_image(cropped_image, arabic_coordinates)
            left_part_image, right_part_image, bottom_part_image = self.native_process.split_image(masked_image, left_coordinates, right_coordinates, bottom_coordinates)
            left_short_comp, left_comp = self.native_process.extract_left_segment_data(left_part_image)
            right_short_comp, right_comp = self.native_process.extract_right_segment_data(right_part_image)
            bottom_part_data, table_data, N_enrg,bank_name = self.native_process.extract_bottom_segment_data(bottom_part_image)
            
            dicts = [left_short_comp, left_comp, right_short_comp, right_comp, N_enrg,bank_name, bottom_part_data, table_data]
            result = {k: v for d in dicts for k, v in d.items()}
            return {
                'scanned_document_type': invoice_type,
                'process_type': chosen_process,
                'invoice_data': result
            }
        except Exception as e:
            return print({"error": str(e)})
        
    @staticmethod
    def zonal_extraction(image, coordinates_file_path, invoice_type, chosen_process, extractor):
        extracted_text = extractor.extract_text_from_image(image, coordinates_file_path)
        result = extractor.process_extracted_text(extracted_text)
        return {
            'scanned_document_type': invoice_type,
            'process_type': chosen_process,
            'invoice_data': result
        }
        
    def ner_spacy_extraction(self, image, invoice_type, chosen_process):
        result = self.document_processor.process(image)
        return {
            'scanned_document_type': invoice_type,
            'process_type': chosen_process,
            'invoice_data': result
        }
    
        
    def _image_preprocessing(self, image):
        try:
            # Image preprocessing steps
            new_image, res_indicator = self.image_proc.check_resolution(image)
            print(f"Resolution indicator: {res_indicator}")
            
            dim_indicator = self.image_proc.check_dimensions(image)
            print(f"Dimensions indicator: {dim_indicator}")
            
            clarity_indicator = self.image_proc.check_clarity(image)
            print(f"Clarity indicator: {clarity_indicator}")
            
            noise_indicator = self.image_proc.check_noise(image)
            print(f"Noise indicator: {noise_indicator}")
            
            low_quality_indicator = res_indicator + dim_indicator + clarity_indicator + noise_indicator
            print(f"Low quality indicator: {low_quality_indicator}")
            
            invoice_image=new_image
            if low_quality_indicator >= 3:
                preprocessed_image = self.image_proc.preprocess_invoice_image(image)
                invoice_image = preprocessed_image
            else:
                invoice_image = image
            
            scanned_invoice = invoice_image
            fixed_image = self.image_proc.align_image(scanned_invoice)

            resized_image = self.image_proc.resize_image(fixed_image)
            cropped_image = self.image_proc.crop_image(resized_image)

            return cropped_image  # Return the processed image

        except Exception as e:
            # Extract the line number from the exception and include it in the error message
            line_number = traceback.extract_tb(sys.exc_info()[2])[-1][1]
            error_message = f"An error occurred at line {line_number}: {e}"
            print(error_message)
            return None  # Return None, but handle it in the calling function


    def _image_preprocessing_ner(self, image):
        try:
            # Image preprocessing steps
            new_image, res_indicator = self.image_proc.check_resolution(image)
            print(f"Resolution indicator: {res_indicator}")
            
            dim_indicator = self.image_proc.check_dimensions(image)
            print(f"Dimensions indicator: {dim_indicator}")
            
            clarity_indicator = self.image_proc.check_clarity(image)
            print(f"Clarity indicator: {clarity_indicator}")
            
            noise_indicator = self.image_proc.check_noise(image)
            print(f"Noise indicator: {noise_indicator}")
            
            low_quality_indicator = res_indicator + dim_indicator + clarity_indicator + noise_indicator
            print(f"Low quality indicator: {low_quality_indicator}")
            
            print("done")
            
            invoice_image=new_image
            if low_quality_indicator >= 3:
                preprocessed_image = self.image_proc.preprocess_invoice_image(image)
                invoice_image = preprocessed_image
            else:
                invoice_image = image
            print("done condition")
            scanned_invoice = invoice_image

            print("scanned_invoice = invoice_image is done ")

            return scanned_invoice  # Return the processed image

        except Exception as e:
            # Extract the line number from the exception and include it in the error message
            line_number = traceback.extract_tb(sys.exc_info()[2])[-1][1]
            error_message = f"An error occurred at line {line_number}: {e}"
            print(error_message)
            return None  # Return None, but handle it in the calling function
