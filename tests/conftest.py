import pytest
from api_client.api_client import APIClient
from settings.settings_doska import SettingsDoska as St
from utilities.data_generator import DataGenerator as Dg




@pytest.fixture
def api_client():
    """Фикстура для создания клиента API с базовым URL"""
    return APIClient(St.BASE_URL)


@pytest.fixture
def registration_data():
    fake_user = Dg.create_fake_user()
    return {
        "email": fake_user.get("email"),
        "password": fake_user.get("password"),
        "submitPassword": fake_user.get("password")
    }


