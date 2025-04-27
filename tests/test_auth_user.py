from settings.settings_doska import SettingsDoska as Sd





def test_login_user_success(api_client, create_user):
    payload = create_user

    response = api_client.post(
        endpoint=Sd.ENDPOINT_SIGNIN,
        json=payload
    )

    # Проверка статус-кода
    assert response.status_code == 201, f"Ожидался статус код 201, но получен {response.status_code}"

    # Проверка структуры ответа
    response_data = response.json()

    # 1. Проверка наличия основных полей в ответе
    assert "user" in response_data, "Ответ должен содержать объект 'user'"
    assert "token" in response_data, "Ответ должен содержать объект 'token'"

    # 2. Проверка данных пользователя
    user_data = response_data["user"]
    assert "id" in user_data and isinstance(user_data["id"], int), "ID пользователя должен быть целым числом"
    assert "name" in user_data and user_data["name"] == "User", "Имя пользователя должно быть 'User'"
    assert "email" in user_data and user_data["email"] == payload["email"], (
        f"Email пользователя должен совпадать с email из запроса ({payload['email']})"
    )
    assert "avatar" in user_data, "Должно присутствовать поле 'avatar'"
    assert "admin" in user_data and isinstance(user_data["admin"], bool), "Поле 'admin' должно быть boolean"

    # 3. Проверка токена
    token_data = response_data["token"]
    assert "access_token" in token_data, "Токен должен содержать поле 'access_token'"
    assert isinstance(token_data["access_token"], str), "Access token должен быть строкой"
    assert len(token_data["access_token"]) > 50, "Access token должен быть достаточно длинным"


