class Scheme:
    @property
    def transaction(self):
        return {
            "type": "object",
            "properties": {
                "from": {"type": "string", "maxLength": 3, "minimum": 0},
                "to": {"type": "string", "maxLength": 3, "minimum": 0},
                "amount": {"type": "number"},
            },
            "required": ["from", "to", "amount"],
        }

    @property
    def signin(self):
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "format": "email"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }

    @property
    def signup(self):
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "format": "email"},
                "password": {"type": "string"},
                "repeat_password": {"type": "string"},
            },
            "required": ["username", "password", "repeat_password"],
        }
