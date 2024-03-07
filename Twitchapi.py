import requests
import json

class TwitchApi:
    
    def __init__(self, json_path = './json/api.json'):
        self.token_url = 'https://id.twitch.tv/oauth2/token'
        f = open(json_path,'r')
        self.json_file = json.load(f)
        f.close()
        self.client_id = self.json_file['platforms']['twitch']['client_id']
        self.client_secret = self.json_file['platforms']['twitch']['client_secret']
        self.grant_type = 'client_credentials'
        self.access_token = None
    
    def set_access_token(self):
        try:
            data = {'client_id':self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type':self.grant_type
                    }

            ret = requests.post(url = self.token_url, data = data)
            ret = json.loads(ret.content)

            self.access_token = ret['access_token']
        except:
            self.access_token = None

    def is_streaming(self, channel_name):
        if self.access_token == None:
            return
        try:    
            headers = {
                'Client-ID': self.client_id,
                'Authorization': f'Bearer {self.access_token}'
            }
            url = f'https://api.twitch.tv/helix/streams?user_login={channel_name}'
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data['data']:
                    # Stream is currently live
                    return True
                else:
                    # Stream is offline
                    return False
            else:
                # Failed to get stream status
                return None
        except:
            return None
