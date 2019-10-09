from api_client import BaseAPIClient


class PushbulletAPIClient(BaseAPIClient):
    force_trailing_backslash = False


    def __init__(self, api_key=None, *args, **kwargs):
        super(PushbulletAPIClient, self).__init__(*args, **kwargs)
        if api_key:
            self.api_key = api_key
        else:
            try:
                with open("api_key.txt", "r") as key_file:
                    self.api_key = key_file.read().strip()
            except:
                raise Exception(
                    "API key wasn't specified nor in start parameters, "
                    "neither in api_key.txt file")


    def get_endpoint(self):
        return "https://api.pushbullet.com/v2/"


    def prepare_headers(self, extra_headers=None):
        headers = super(PushbulletAPIClient, self).prepare_headers(
            extra_headers=extra_headers)

        headers["Access-Token"] = self.api_key

        return headers

    def get_devices(self):
        response = self.get("devices")
        return response.json()


    def push_to_device(self, device_id, push_data):
        data = {
            "device_iden": device_id,            
        }

        data.update(push_data)

        response = self.post("pushes", data=data)
        return response.json()

    def push_note_to_device(self, device_id, body, title=""):
        note = {
            "type": "note",
            "title": title,
            "body": body,
        }
        result = self.push_to_device(device_id, note)
        return result
