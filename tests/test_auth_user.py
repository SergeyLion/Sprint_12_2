from settings.settings_doska import SettingsDoska as Sd
import allure


@allure.feature("Аутентификация пользователя")
@allure.story("Успешный вход пользователя")
@allure.title("Тест успешного входа пользователя в систему")
def test_login_user_success(api_client, create_user):
    payload = create_user

    with allure.step("Подготовка данных для входа"):
        allure.attach(str(payload), name="Данные для входа", attachment_type=allure.attachment_type.TEXT)
        allure.attach(f"Endpoint: {Sd.ENDPOINT_SIGNIN}", name="Endpoint", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Отправка запроса на вход"):
        response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNIN,
            json=payload
        )

        allure.attach(
            f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_SIGNIN}\n"
            f"Request Body: {payload}\n"
            f"Response Status: {response.status_code}\n"
            f"Response Body: {response.text}",
            name="Детали запроса/ответа",
            attachment_type=allure.attachment_type.TEXT
        )

    with allure.step("Проверка статус-кода ответа"):
        assert response.status_code == 201, f"Ожидался статус код 201, но получен {response.status_code}"

    response_data = response.json()

    with allure.step("Проверка структуры ответа"):
        # 1. Проверка наличия основных полей в ответе
        with allure.step("Проверка наличия основных полей"):
            assert "user" in response_data, "Ответ должен содержать объект 'user'"
            assert "token" in response_data, "Ответ должен содержать объект 'token'"
            allure.attach("Наличие полей 'user' и 'token' подтверждено", name="Результат проверки",
                          attachment_type=allure.attachment_type.TEXT)

        # 2. Проверка данных пользователя
        with allure.step("Проверка данных пользователя"):
            user_data = response_data["user"]

            assert "id" in user_data and isinstance(user_data["id"], int), "ID пользователя должен быть целым числом"
            assert "name" in user_data and user_data["name"] == "User", "Имя пользователя должно быть 'User'"
            assert "email" in user_data and user_data["email"] == payload["email"], (
                f"Email пользователя должен совпадать с email из запроса ({payload['email']})"
            )
            assert "avatar" in user_data, "Должно присутствовать поле 'avatar'"
            assert "admin" in user_data and isinstance(user_data["admin"], bool), "Поле 'admin' должно быть boolean"

            allure.attach(
                f"ID: {user_data.get('id')}\n"
                f"Name: {user_data.get('name')}\n"
                f"Email: {user_data.get('email')}\n"
                f"Avatar: {'присутствует' if user_data.get('avatar') else 'отсутствует'}\n"
                f"Admin: {user_data.get('admin')}",
                name="Данные пользователя",
                attachment_type=allure.attachment_type.TEXT
            )

        # 3. Проверка токена
        with allure.step("Проверка токена доступа"):
            token_data = response_data["token"]

            assert "access_token" in token_data, "Токен должен содержать поле 'access_token'"
            assert isinstance(token_data["access_token"], str), "Access token должен быть строкой"
            assert len(token_data["access_token"]) > 50, "Access token должен быть достаточно длинным"

            # Прикрепляем часть токена (без полного отображения из соображений безопасности)
            allure.attach(
                f"Токен получен (первые 10 символов): {token_data['access_token'][:10]}...\n"
                f"Длина токена: {len(token_data['access_token'])} символов",
                name="Информация о токене",
                attachment_type=allure.attachment_type.TEXT
            )
