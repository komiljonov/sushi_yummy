import requests

class Bot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{self.token}/"

    def send_message(self, user_id, message):
        url = self.base_url + "sendMessage"
        payload = {
            'chat_id': user_id,
            'text': message
        }
        response = requests.post(url, data=payload)
        return response.json()