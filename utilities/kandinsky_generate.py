import requests
import base64
import time
import json



class KandinskyAPI:
    def __init__(self):
        self.URL = "https://api-key.fusionbrain.ai/"
        self.API_KEY = "62AE403D6D4031FA310199ECE610B0EC"
        self.SECRET_KEY = "431FD21BABD49D47E13EA5E2C8068CC7"
        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.API_KEY}',
            'X-Secret': f'Secret {self.SECRET_KEY}',
        }

    def generate_image(self, prompt):
        # Получаем pipeline ID
        pipeline_id = self._get_pipeline()

        # Генерируем изображение
        uuid = self._generate(prompt, pipeline_id)

        # Проверяем статус и получаем результат
        image_data = self._check_generation(uuid)

        # Декодируем base64 в бинарные данные
        return base64.b64decode(image_data[0])

    def _get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def _generate(self, prompt, pipeline, width=512, height=512):
        params = {
            "type": "GENERATE",
            "numImages": 1,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }

        response = requests.post(
            self.URL + 'key/api/v1/pipeline/run',
            headers=self.AUTH_HEADERS,
            files=data
        )
        return response.json()['uuid']

    def _check_generation(self, request_id, attempts=10, delay=3):
        while attempts > 0:
            response = requests.get(
                self.URL + 'key/api/v1/pipeline/status/' + request_id,
                headers=self.AUTH_HEADERS
            )
            data = response.json()

            if data['status'] == 'DONE':
                return data['result']['files']
            elif data['status'] == 'FAIL':
                raise Exception("Генерация изображения не удалась")

            attempts -= 1
            time.sleep(delay)

        raise Exception("Превышено время ожидания генерации изображения")
