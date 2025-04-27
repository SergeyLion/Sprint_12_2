import requests

class ApiClient:
    def __init__(self, base_url, timeout=10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()  # Добавляем сессию

    def get(self, endpoint, params=None, headers=None):
        response = self.session.get(
            f"{self.base_url}/{endpoint}", params=params, headers=headers, timeout=self.timeout
        )
        return response

    def post(self, endpoint, data=None, headers=None, json=None, files=None):
        response = self.session.post(
            f"{self.base_url}/{endpoint}", data=data, json=json, headers=headers, files=files, timeout=self.timeout
        )
        return response

    def patch(self, endpoint, data=None, headers=None, json=None, files=None):
        response = self.session.patch(
            f"{self.base_url}/{endpoint}", data=data, json=json, headers=headers, files=files, timeout=self.timeout
        )
        return response


    def put(self, endpoint, data=None, headers=None, json=None):
        response = self.session.put(
            f"{self.base_url}/{endpoint}", data=data, json=json, headers=headers, timeout=self.timeout
        )
        return response

    def delete(self, endpoint, params=None, headers=None):
        response = self.session.delete(
            f"{self.base_url}/{endpoint}", params=params, headers=headers, timeout=self.timeout
        )
        return response
