from settings.settings_doska import SettingsDoska as Sd



class TestRegistrationUser:

    def test_registration_success(self, api_client, registration_data):
        response = api_client.post(endpoint=Sd.ENDPOINT_SIGNUP,
            json=registration_data
        )
        assert response.status_code == 201, f"Ожидался статус код 201, но получен {response.status_code}"

        response_data = response.json()

        # Проверка структуры ответа
        assert "user" in response_data, "Ответ должен содержать объект 'user'"
        assert "access_token" in response_data, "Ответ должен содержать объект 'access_token'"

        # Проверка полей user
        user_data = response_data["user"]
        assert "id" in user_data and isinstance(user_data["id"], int), "Пользователь должен иметь целочисленный 'id'"
        assert "name" in user_data and user_data["name"] == "User", "Имя пользователя должно быть 'User'"
        assert "email" in user_data and user_data["email"] == registration_data["email"], \
            f"Email пользователя должен совпадать с email из запроса {registration_data['email']}"

        # Проверка access_token
        token_data = response_data["access_token"]
        assert "access_token" in token_data and isinstance(token_data["access_token"], str), \
            "Access token должен быть строкой"
        assert len(token_data["access_token"]) > 50, "Access token должен быть достаточно длинным"

    def test_registration_with_repeat_email(self, api_client, registration_data):
        # Первая регистрация (успешная)
        response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNUP,
            json=registration_data
        )
        assert response.status_code == 201, f"Ожидался статус код 201, но получен {response.status_code}"

        # Повторная попытка регистрации с тем же email
        repeat_response = api_client.post(
            endpoint=Sd.ENDPOINT_SIGNUP,
            json=registration_data
        )

        # Проверки для повторного запроса
        assert repeat_response.status_code == 400, (
            f"Ожидался статус код 400 для повторной регистрации, но получен {repeat_response.status_code}"
        )

        # Проверка тела ответа
        repeat_response_data = repeat_response.json()
        assert "statusCode" in repeat_response_data, "Ответ должен содержать поле 'statusCode'"
        assert repeat_response_data["statusCode"] == 400, (
            f"Ожидался statusCode 400, но получен {repeat_response_data['statusCode']}"
        )

        assert "message" in repeat_response_data, "Ответ должен содержать поле 'message'"
        assert repeat_response_data["message"] == "Почта уже используется", (
            f"Ожидалось сообщение 'Почта уже используется', но получено '{repeat_response_data['message']}'"
        )







