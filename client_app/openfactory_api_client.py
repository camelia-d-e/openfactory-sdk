import requests
import sseclient


class OpenFactoryAPIClient:
    """Client for interacting with the OpenFactory API."""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def get_device_status(self, device_uuid):
        url = f'{self.base_url}/devices/{device_uuid}/status'
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def subcribe_device_events(self, device_uuid):
        url = f"{self.api_base_url}/devices/{device_uuid}/subscribe"
        response = requests.get(url, stream=True)
        client = sseclient.SSEClient(response)
        for event in client.events():
            yield event.data
            
    def get_all_devices(self):
        url = f'{self.base_url}/devices'
        response = requests.get(url)
        response.raise_for_status()
        print(response.json())
        return response.json()['devices']

    def close(self):
        pass
