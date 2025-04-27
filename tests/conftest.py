import pytest
from api_client.api_client import APIClient
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg




@pytest.fixture
def api_client():
    """Фикстура для создания клиента API с базовым URL"""
    return APIClient(Sd.BASE_URL)


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




