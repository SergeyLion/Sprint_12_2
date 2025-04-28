import pytest
from datetime import datetime
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg


class TestCreateListing:
    def test_create_listing_success(self, api_client, auth_token, kandinsky_api, delete_test_listing):
        # Генерация тестовых данных
        data = Dg.create_listing_data()

        # Генерация изображения
        prompt = data.get('description')
        image_data = kandinsky_api.generate_image(prompt)

        # Подготовка файлов
        test_files = [
            ('images', (f'image_{Dg.generator_uid()}.jpg', image_data, 'image/jpeg'))
        ]

        # Заголовки запроса
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        }

        # Отправка запроса
        response = api_client.post(
            endpoint=Sd.ENDPOINT_CREATE_LISTING,
            headers=headers,
            data=data,
            files=test_files
        )

        # Проверка статус-кода
        assert response.status_code == 201, (
            f"Ожидался статус код 201, но получен {response.status_code}. "
            f"Ответ сервера: {response.text}"
        )

        # Получение и проверка ответа
        response_data = response.json()
        delete_test_listing['id'] = response_data['id']

        # Основные проверки структуры ответа
        required_fields = [
            'id', 'name', 'category', 'condition', 'city',
            'description', 'price', 'img1', 'owner',
            'updatedAt', 'createdAt'
        ]
        for field in required_fields:
            assert field in response_data, f"Отсутствует обязательное поле: {field}"

        # Проверка типов данных
        assert isinstance(response_data['id'], int), "ID должен быть целым числом"
        assert isinstance(response_data['name'], str), "Название должно быть строкой"
        assert isinstance(response_data['category'], str), "Категория должна быть строкой"
        assert isinstance(response_data['condition'], str), "Состояние должно быть строкой"
        assert isinstance(response_data['city'], str), "Город должен быть строкой"
        assert isinstance(response_data['description'], str), "Описание должно быть строкой"
        assert isinstance(response_data['price'], int), "Цена должна быть числом"
        assert isinstance(response_data['owner'], int), "ID владельца должен быть числом"

        # Проверка формата дат
        try:
            datetime.fromisoformat(response_data['createdAt'].replace('Z', ''))
            datetime.fromisoformat(response_data['updatedAt'].replace('Z', ''))
        except ValueError:
            pytest.fail("Некорректный формат даты")

        # Проверка соответствия отправленных и полученных данных
        assert response_data['name'] == data['name'], "Название не соответствует отправленному"
        assert response_data['category'] == data['category'], "Категория не соответствует отправленной"
        assert response_data['condition'] == data['condition'], "Состояние не соответствует отправленному"
        assert response_data['city'] == data['city'], "Город не соответствует отправленному"
        assert response_data['description'] == data['description'], "Описание не соответствует отправленному"
        assert response_data['price'] == int(data['price']), "Цена не соответствует отправленной"

        # Проверка изображений
        assert response_data['img1'].startswith('http'), "Ссылка на изображение должна быть URL"


        # Проверка дополнительных полей
        assert 'isFavorite' in response_data, "Отсутствует поле isFavorite"

        # Проверка, что created и updated даты одинаковы (для нового объявления)
        assert response_data['createdAt'] == response_data[
            'updatedAt'], "Даты создания и обновления должны совпадать для нового объявления"