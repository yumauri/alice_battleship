from flask import jsonify


class Response:
    def __init__(self, request):
        self.request = request
        self.response = {
            "version": request["version"],
            "response": {"text": "", "buttons": [], "end_session": False},
        }

    # use `res << "test"` to write response text
    def __lshift__(self, txt):
        self.response["response"]["text"] = txt
        return self

    # use `res <<= "test"` to add response text
    def __ilshift__(self, txt):
        self.response["response"]["text"] += txt
        return self

    # use `res += {}` to add button
    def __iadd__(self, button):
        self.response["response"]["buttons"].append(button)
        return self

    # use `res |= "text"` to end session with text
    def __ior__(self, txt):
        self.response["response"]["text"] = txt
        self.response["response"]["end_session"] = True
        return self

    def __repr__(self):
        return str(self.response)

    # use `+res` to jsonify response
    def __pos__(self):
        return jsonify(self.response)
