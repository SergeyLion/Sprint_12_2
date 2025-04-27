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
def kandinsky_api():
    return KandinskyAPI()

@pytest.fixture
def create_listing_data():
    name
    data = {}
