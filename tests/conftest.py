import pytest
import allure
from api_client.api_client_session import ApiClient
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg
from utilities.kandinsky_generate import KandinskyAPI


@pytest.fixture
def api_client():
    """Фикстура для создания клиента API с базовым URL"""
    with allure.step("Создание API клиента с базовым URL"):
        return ApiClient(Sd.BASE_URL)


@pytest.fixture
def registration_data():
    with allure.step("Генерация тестовых данных для регистрации пользователя"):
        fake_user = Dg.create_fake_user()
        data = {
            "email": fake_user.get("email"),
            "password": fake_user.get("password"),
            "submitPassword": fake_user.get("password")
        }
        allure.attach(str(data), name="Регистрационные данные", attachment_type=allure.attachment_type.TEXT)
        return data


@pytest.fixture
def create_user(api_client, registration_data):
    with allure.step("Создание нового пользователя"):
        response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNUP,
            json=registration_data
        )

        allure.attach(
            f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_SIGNUP}\n"
            f"Request Body: {registration_data}\n"
            f"Response Status: {response.status_code}\n"
            f"Response Body: {response.text}",
            name="Детали запроса/ответа",
            attachment_type=allure.attachment_type.TEXT
        )

        assert response.status_code == 201
        user = {
            "email": registration_data.get("email"),
            "password": registration_data.get("password")
        }
        return user


@pytest.fixture
def auth_token(api_client, create_user):
    with allure.step("Получение токена аутентификации"):
        payload = create_user

        response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNIN,
            json=payload
        )

        allure.attach(
            f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_SIGNIN}\n"
            f"Request Body: {payload}\n"
            f"Response Status: {response.status_code}\n"
            f"Response Body: {response.text}",
            name="Детали запроса/ответа аутентификации",
            attachment_type=allure.attachment_type.TEXT
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
    with allure.step("Создание и аутентификация другого пользователя"):
        # Регистрация и логин другого пользователя
        another_user = {
            "email": "another_user@example.com",
            "password": "another_password123",
            "submitPassword": "another_password123"
        }

        # Регистрация
        reg_response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNUP,
            json=another_user
        )

        # Логин
        login_response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNIN,
            json=another_user
        )

        allure.attach(
            f"Другой пользователь:\n"
            f"Email: {another_user['email']}\n"
            f"Password: {another_user['password']}\n\n"
            f"Response Status (регистрация): {reg_response.status_code}\n"
            f"Response Status (логин): {login_response.status_code}",
            name="Детали другого пользователя",
            attachment_type=allure.attachment_type.TEXT
        )

        return login_response.json()["token"]["access_token"]


@pytest.fixture
def kandinsky_api():
    with allure.step("Инициализация API Kandinsky"):
        return KandinskyAPI()


@pytest.fixture
def create_test_listing(api_client, auth_token, kandinsky_api):
    """Фикстура создания тестового объявления"""
    with allure.step("Создание тестового объявления"):
        # Генерация тестовых данных
        data = Dg.create_listing_data()
        allure.attach(str(data), name="Данные для создания объявления", attachment_type=allure.attachment_type.TEXT)

        # Генерация изображения
        prompt = data.get('description')
        with allure.step(f"Генерация изображения по описанию: '{prompt}'"):
            image_data = kandinsky_api.generate_image(prompt)
            allure.attach(image_data, name="Сгенерированное изображение", attachment_type=allure.attachment_type.JPG)

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

        allure.attach(
            f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_CREATE_LISTING}\n"
            f"Headers: {headers}\n"
            f"Data: {data}\n"
            f"Response Status: {response.status_code}\n"
            f"Response Body: {response.text}",
            name="Детали запроса создания объявления",
            attachment_type=allure.attachment_type.TEXT
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

    with allure.step("Удаление тестового объявления"):
        if data_delete_listing['id'] is None:
            return

        # Заголовки с токеном авторизации
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        }

        delete_response = api_client.delete(
            endpoint=f"{Sd.ENDPOINT_LISTINGS}/{data_delete_listing['id']}",
            headers=headers
        )

        allure.attach(
            f"Request: DELETE {Sd.BASE_URL}{Sd.ENDPOINT_LISTINGS}/{data_delete_listing['id']}\n"
            f"Headers: {headers}\n"
            f"Response Status: {delete_response.status_code}\n"
            f"Response Body: {delete_response.text}",
            name="Детали запроса удаления объявления",
            attachment_type=allure.attachment_type.TEXT
        )

        assert delete_response.status_code == 200, (
            f"Ожидался статус код 200 (Ok), но получен {delete_response.status_code}. "
            f"Ответ сервера: {delete_response.text}"
        )
