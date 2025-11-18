import json


class Config:

    def __init__(self, data):
        self.__dict__.update(data)
    
    def get(self, attr_name):
        if attr_name in self.__dict__:
            return self.__dict__[attr_name]
        return None

    @staticmethod
    def from_json(config_path):
        with open(config_path, "r", encoding="UTF-8") as file:
            return json.load(file, object_hook=Config)
