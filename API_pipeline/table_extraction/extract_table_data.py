from table_extraction.table_extraction_functions import Table_extraction_func
from invoice_data_extraction import Invoice_data_extraction

class Extract_table_data:
    def __init__(self):
        self.imgage_proc=Invoice_data_extraction()
        self.tab_extraction=Table_extraction_func()

    def extract_tab(self,image,file_path):
        try:

            
            temp_path="static/uploads/french_exemple_facture.pdf"
            print(file_path)
            self.tab_extraction.convert_to_searchable_pdf_test(file_path,temp_path)
            print(" searchable done")
            table_data = self.tab_extraction.extract_table_from_pdf(temp_path)
            print(" tabula done")
            new_data=self.tab_extraction.replace_nan(table_data)
            print(" replace_nan done")
            data=self.tab_extraction.remove_unwanted_entries(new_data)
            print(" remove_unwanted_entries done")
            print(data)
            processed_data=[self.tab_extraction.process_data(dictionary) for sublist in data for dictionary in sublist]
            print(" process_data done")
            process_result=self.tab_extraction.process_result(processed_data)
            print(" process_result done")
            filtered_data = self.tab_extraction.process_main_table(process_result)
            print(" process_main_table done")
            grouped_data = self.tab_extraction.group_dicts_by_keys(filtered_data)
            print(" group_dicts_by_keys done")
            # Find the longest list from the grouped data
            table_data = max(grouped_data, key=len)
            print(" table_data done")
            total_table_data = min(grouped_data, key=len)
            print(" total_table_data done")
            total_table_data = [self.tab_extraction.remove_items_with_pipe(dct) for dct in total_table_data]
            print(" remove_items_with_pipe done")
            grouped_dicts = [self.tab_extraction.group_items(dct) for dct in total_table_data]
            print(" group_items done")
            total_table_data=self.tab_extraction.total_check(grouped_dicts)
            print(" total_check done")
            response_data=self.tab_extraction.merge_data(table_data,total_table_data)
            print(" merge_data done")
            print(response_data)


        except Exception as e:
            return print({"error": str(e)})

        return response_data


