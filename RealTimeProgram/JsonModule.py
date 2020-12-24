import json
class json_class:
    def __init__(self):
        print("만들어 졌다.")
    def make_json(self, dictionaries):
        try:
            message = json.dumps(dictionaries)
        except(TypeError, ValueError):
            raise ('You can only send JSON-serializable data')
            return None

        return message