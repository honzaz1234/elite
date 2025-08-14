import copy
import json
import scrapy



class TestDataLoader():


    def __init__(self):

        pass

    def get_names_with_formats(self, names: list, format_type: str) -> list:

        new_names = []
        for name in names:
            new_name = name + '.' + format_type
            new_names.append(new_name)

        return new_names
        
    def load_dict(self, file_path: str) -> dict:

        f = open(file_path)
        dict_ = json.load(f)
        
        return dict_

    def load_html(self, file_path: str):

        with open(file_path, "r") as f:
            html_file = f.read()

        return html_file

    def load_data(
            self, type_: str, path: str, 
            file_names: list, key_names: list) -> dict:
        
        return_dict = {}
        for ind in range(len(file_names)):
            path_file =  path + file_names[ind]
            key_name = key_names[ind]
            if type_ == 'json':
                return_dict[key_name] = self.load_dict(path_file)
            elif type_ == 'html':
                return_dict[key_name] = self.load_html(path_file)

        return return_dict
    
    def create_selectors(self, htmls: list, names: list) -> list:

        selectors = {}
        for ind in range(len(htmls)):
            sel = scrapy.Selector(text=htmls[list(htmls.keys())[ind]])
            selectors[names[ind]] = sel

        return selectors

    def get_nested_item(self, dict_: dict, keys: list) -> dict:
        
        d = copy.deepcopy(dict_)
        for key in keys:
            if isinstance(d, dict) and key in d:
                d = d[key]
            else:
                return None  # Path doesn't exist
  
        return d
     
    def delete_nested_key(self, d: dict, keys: list) -> dict:

        if not keys:
            return False
        
        key = keys[0]
        if len(keys) == 1:
            # Base case: Delete the key if it exists
            if isinstance(d, dict) and key in d:
                del d[key]
                return True
            return False
        
        # Recursive case: Navigate deeper into the dictionary
        if isinstance(d, dict) and key in d:
            return self.delete_nested_key(d[key], keys[1:])
        
        return False
