import pytest
from api_client.api_client_session import ApiClient
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg
from utilities.kandinsky_generate import KandinskyAPI
import os



@pytest.fixture
def api_client():
    """Фикстура для создания клиента API с базовым URL"""
    return ApiClient(Sd.BASE_URL)


@pytest.fixture
def registration_data():
    fake_user = Dg.create_fake_user()
    return {
        "email": fake_user.get("email"),
        "password": fake_user.get("password"),
        "submitPassword": fake_user.get("password")
    }

@pytest.fixture
def create_user(api_client, registration_data):
    response = api_client.post(endpoint=Sd.ENDPOINT_SIGNUP,
                               json=registration_data
                               )
    assert response.status_code == 201
    user = {
        "email": registration_data.get("email"),
        "password": registration_data.get("password")
    }
    return user


@pytest.fixture
def auth_token(api_client, create_user):
    payload = create_user

    response = api_client.post(
        endpoint=Sd.ENDPOINT_SIGNIN,
        json=payload
    )

    # Проверка статус-кода
    assert response.status_code == 201, f"Ожидался статус код 201, но получен {response.status_code}"

    # Проверка структуры ответа
    response_data = response.json()
    token_data = response_data["token"]
    token = token_data["access_token"]
    return token


@pytest.fixture
def another_auth_token(api_client):
    # Регистрация и логин другого пользователя
    another_user = {
        "email": "another_user@example.com",
        "password": "another_password123",
        "submitPassword": "another_password123"

    }

    # Регистрация
    api_client.post(
        endpoint=Sd.ENDPOINT_SIGNUP,
        json=another_user
    )

    # Логин
    response = api_client.post(
        endpoint=Sd.ENDPOINT_SIGNIN,
        json=another_user
    )

    return response.json()["token"]["access_token"]


@pytest.fixture
def kandinsky_api():
    return KandinskyAPI()


@pytest.fixture
def create_test_listing(api_client, auth_token, kandinsky_api):
    """Фикстура создания тестового объявления"""
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
    return response_data

@pytest.fixture
def delete_test_listing(api_client, auth_token):
    data_delete_listing = {'id': None}
    yield data_delete_listing
    # Заголовки с токеном авторизации
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/json"
    }

    delete_response = api_client.delete(
        endpoint=f"{Sd.ENDPOINT_LISTINGS}/{data_delete_listing['id']}",
        headers=headers
    )
    assert delete_response.status_code == 200, (
        f"Ожидался статус код 200 (Ok), но получен {delete_response.status_code}. "
        f"Ответ сервера: {delete_response.text}"
    )

