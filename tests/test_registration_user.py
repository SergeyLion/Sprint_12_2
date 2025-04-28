from settings.settings_doska import SettingsDoska as Sd
import allure



@allure.feature("Регистрация пользователя")
class TestRegistrationUser:

    @allure.story("Успешная регистрация нового пользователя")
    @allure.title("Проверка успешной регистрации")
    def test_registration_success(self, api_client, registration_data):
        with allure.step("1. Подготовка данных для регистрации"):
            allure.attach(str(registration_data), name="Регистрационные данные",
                          attachment_type=allure.attachment_type.JSON)

        with allure.step("2. Отправка запроса на регистрацию"):
            response = api_client.post(
                endpoint=Sd.ENDPOINT_SIGNUP,
                json=registration_data
            )

            allure.attach(
                f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_SIGNUP}\n"
                f"Request Body: {registration_data}\n"
                f"Response Status: {response.status_code}\n"
                f"Response Body: {response.text}",
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. Проверка статус-кода ответа"):
            assert response.status_code == 201, \
                f"Ожидался статус код 201, но получен {response.status_code}"

        with allure.step("4. Проверка структуры ответа"):
            response_data = response.json()
            allure.attach(str(response_data), name="Полный ответ сервера",
                          attachment_type=allure.attachment_type.JSON)

            with allure.step("4.1 Проверка наличия обязательных полей"):
                assert "user" in response_data, "Ответ должен содержать объект 'user'"
                assert "access_token" in response_data, "Ответ должен содержать объект 'access_token'"

            with allure.step("4.2 Проверка данных пользователя"):
                user_data = response_data["user"]
                allure.attach(str(user_data), name="Данные пользователя",
                              attachment_type=allure.attachment_type.JSON)

                assert "id" in user_data and isinstance(user_data["id"], int), \
                    "Пользователь должен иметь целочисленный 'id'"
                assert "name" in user_data and user_data["name"] == "User", \
                    "Имя пользователя должно быть 'User'"
                assert "email" in user_data and user_data["email"] == registration_data["email"], \
                    f"Email пользователя должен совпадать с email из запроса {registration_data['email']}"

            with allure.step("4.3 Проверка access token"):
                token_data = response_data["access_token"]
                assert "access_token" in token_data and isinstance(token_data["access_token"], str), \
                    "Access token должен быть строкой"
                assert len(token_data["access_token"]) > 50, "Access token должен быть достаточно длинным"
                allure.attach(f"Токен получен (первые 10 символов): {token_data['access_token'][:10]}...",
                              name="Информация о токене",
                              attachment_type=allure.attachment_type.TEXT)

    @allure.story("Регистрация с уже существующим email")
    @allure.title("Проверка обработки повторной регистрации")
    def test_registration_with_repeat_email(self, api_client, registration_data):
        with allure.step("1. Первая регистрация (успешная)"):
            first_response = api_client.post(
                endpoint=Sd.ENDPOINT_SIGNUP,
                json=registration_data
            )
            allure.attach(str(first_response.json()), name="Ответ первой регистрации",
                          attachment_type=allure.attachment_type.JSON)
            assert first_response.status_code == 201

        with allure.step("2. Повторная попытка регистрации с тем же email"):
            repeat_response = api_client.post(
                endpoint=Sd.ENDPOINT_SIGNUP,
                json=registration_data
            )

            allure.attach(
                f"Request: POST {Sd.BASE_URL}{Sd.ENDPOINT_SIGNUP}\n"
                f"Request Body: {registration_data}\n"
                f"Response Status: {repeat_response.status_code}\n"
                f"Response Body: {repeat_response.text}",
                name="Детали повторного запроса",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. Проверки для повторного запроса"):
            assert repeat_response.status_code == 400, \
                f"Ожидался статус код 400, но получен {repeat_response.status_code}"

            repeat_response_data = repeat_response.json()
            allure.attach(str(repeat_response_data), name="Ответ на повторную регистрацию",
                          attachment_type=allure.attachment_type.JSON)

            with allure.step("3.1 Проверка поля statusCode"):
                assert "statusCode" in repeat_response_data, "Ответ должен содержать поле 'statusCode'"
                assert repeat_response_data["statusCode"] == 400, \
                    f"Ожидался statusCode 400, но получен {repeat_response_data['statusCode']}"

            with allure.step("3.2 Проверка поля message"):
                assert "message" in repeat_response_data, "Ответ должен содержать поле 'message'"
                expected_message = "Почта уже используется"
                actual_message = repeat_response_data["message"]
                assert actual_message == expected_message, \
                    f"Ожидалось '{expected_message}', получено '{actual_message}'"
                allure.attach(f"Ожидаемое: {expected_message}\nФактическое: {actual_message}",
                              name="Сравнение сообщений",
                              attachment_type=allure.attachment_type.TEXT)
