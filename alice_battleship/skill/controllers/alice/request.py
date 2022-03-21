class Request:
    def __init__(self, request):
        self.request = request
        self.session_id = request["session"]["session_id"]
        self.application_id = request["session"]["application"]["application_id"]
        self.utterance = request["request"]["original_utterance"].lower()

    @property
    def name(self):
        for entity in self.request["request"]["nlu"]["entities"]:
            if entity["type"] == "YANDEX.FIO":
                return entity["value"].get("first_name", None)

    def __repr__(self):
        return str(self.request)
