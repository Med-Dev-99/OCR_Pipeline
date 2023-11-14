import json
from native_extraction.paddleOCR_extraction_process import PaddleOCR_Extraction_Process


class Native_Process_Extraction:

    def __init__(self):
        self.paddle_extraction_process = PaddleOCR_Extraction_Process()


    def mask_image(self, cropped_image, arabic_coordinates):
        with open(arabic_coordinates, 'r') as json_file:
            json_data = json.load(json_file)
        return self.paddle_extraction_process.apply_mask_to_image(cropped_image, json_data)

    def split_image(self, masked_image, left_coordinates, right_coordinates, bottom_coordinates):
        left_part_image = self.paddle_extraction_process.crop_image(masked_image, left_coordinates)
        right_part_image = self.paddle_extraction_process.crop_image(masked_image, right_coordinates)
        bottom_part_image = self.paddle_extraction_process.crop_image(masked_image, bottom_coordinates)
        return left_part_image, right_part_image, bottom_part_image

    def extract_left_segment_data(self, left_part_image):
        left_segment_data = self.paddle_extraction_process.perform_ocr(left_part_image)
        left_short_comp,new_data_list = self.paddle_extraction_process.short_comp_process_left(left_segment_data)

        left_comp = self.paddle_extraction_process.component_extraction(new_data_list)

        return left_short_comp, left_comp

    def extract_right_segment_data(self, right_part_image):
        right_segment_data = self.paddle_extraction_process.perform_ocr(right_part_image)
        first_items_right,new_data_list = self.paddle_extraction_process.extract_first_items_right(right_segment_data)

        new_first_items=   self.paddle_extraction_process.second_process_right(first_items_right)   

        right_comp= self.paddle_extraction_process.second_process_right(new_data_list)

        return new_first_items, right_comp

    def extract_bottom_segment_data(self, bottom_part_image):
        bottom_segment_data = self.paddle_extraction_process.perform_ocr(bottom_part_image)
        bottom_part_data,new_data_list = self.paddle_extraction_process.extract_bottom_right(bottom_segment_data)

        cleaned_list, table_content = self.paddle_extraction_process.separate_table_data(new_data_list)

        table_data=self.paddle_extraction_process.table_process(table_content)

        N_enrg,cleaned_data=self.paddle_extraction_process.get_N_enrg(cleaned_list)

        bank_name=self.paddle_extraction_process.remove_similar_strings(cleaned_data)


        return bottom_part_data, table_data ,N_enrg,bank_name

