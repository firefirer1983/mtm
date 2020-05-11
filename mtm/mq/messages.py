import json


class AddressMessage:
    """
    message = {
       ticket_id: 1,
       status: success,
       data: {
           type: store|generate,
           address: [],
           url: 'http:xxx',
           count: 100000,
       }
       timestamp: 123k123124124,  # int(time.time())
    }

    """

    def __init__(self, ticket_id=None, status=None, data=None, timestamp=None, **kwargs):
        self.ticket_id = ticket_id
        self.status = status
        self.data = data
        self.timestamp = timestamp
        self.message = {"ticket_id": self.ticket_id,
                        "status": self.status,
                        "timestamp": self.timestamp,
                        "data": self.data}

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return f"<{self.__class__.__name__}>ticket_id:{self.ticket_id}"

    def to_json(self):
        return json.dumps(self.message)

    def to_dict(self):
        return json.loads(self.to_json())
