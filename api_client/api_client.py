import requests

class APIClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout

    def get(self, endpoint, params=None):
        response = requests.get(f"{self.base_url}/{endpoint}", params=params, timeout=self.timeout)
        return response

    def post(self, endpoint, json=None, headers=None):
        response = requests.post(f"{self.base_url}/{endpoint}", json=json, headers=headers, timeout=self.timeout)
        return response

    def put(self, endpoint, json=None):
        response = requests.put(f"{self.base_url}/{endpoint}", json=json, timeout=self.timeout)
        return response

    def delete(self, endpoint, params=None):
        response = requests.delete(f"{self.base_url}/{endpoint}", params=params, timeout=self.timeout)
        return response
