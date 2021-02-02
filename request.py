import requests


class Request:
    def __init__(self, config, data):
        self.config = config
        self.data = data

    def send_request(self):
        url = self.config['api_url']
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "XF-Api-Key": self.config['api_key'],
            "XF-Api-User": self.config['api_user']
        }

        response = requests.post(url, headers=headers, data=self.data)

        if response.status_code == 200:
            return True
        else:
            return False
