from settings.settings_doska import SettingsDoska as Sd
import allure


@allure.feature("Удаление объявлений")
@allure.story("Успешное удаление объявления")
class TestDeleteListing:
    @allure.title("Проверка успешного удаления объявления")
    @allure.description("""
    Тест проверяет успешное удаление объявления:
    1. Статус код при удалении (200 OK)
    2. Наличие и содержание сообщения об успешном удалении
    """)
    def test_delete_listing_success(self, api_client, auth_token, create_test_listing):
        with allure.step("1. Получение ID созданного объявления"):
            listing_id = create_test_listing["id"]
            allure.attach(str(listing_id), name="ID объявления", attachment_type=allure.attachment_type.TEXT)

        with allure.step("2. Подготовка заголовков запроса"):
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json"
            }
            allure.attach(str(headers), name="Заголовки запроса", attachment_type=allure.attachment_type.TEXT)

        with allure.step("3. Отправка DELETE запроса"):
            delete_response = api_client.delete(
                endpoint=f"{Sd.ENDPOINT_LISTINGS}/{listing_id}",
                headers=headers
            )

            allure.attach(
                f"Request: DELETE {Sd.BASE_URL}{Sd.ENDPOINT_LISTINGS}/{listing_id}\n"
                f"Headers: {headers}\n"
                f"Response Status: {delete_response.status_code}\n"
                f"Response Body: {delete_response.text}",
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("4. Проверка статус-кода ответа"):
            assert delete_response.status_code == 200, (
                f"Ожидался статус код 200 (Ok), но получен {delete_response.status_code}. "
                f"Ответ сервера: {delete_response.text}"
            )
            allure.attach(f"Получен ожидаемый статус код: 200", name="Результат проверки",
                          attachment_type=allure.attachment_type.TEXT)

        with allure.step("5. Проверка тела ответа"):
            delete_data = delete_response.json()
            allure.attach(str(delete_data), name="Тело ответа", attachment_type=allure.attachment_type.JSON)

            with allure.step("5.1 Проверка наличия поля 'message'"):
                assert "message" in delete_data, "Ответ должен содержать поле 'message'"
                allure.attach("Поле 'message' присутствует в ответе", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.2 Проверка текста сообщения"):
                expected_message = "Объявление удалено успешно"
                actual_message = delete_data["message"]
                assert actual_message == expected_message, (
                    f"Ожидалось сообщение '{expected_message}', получено '{actual_message}'"
                )
                allure.attach(
                    f"Ожидаемое сообщение: {expected_message}\n"
                    f"Фактическое сообщение: {actual_message}",
                    name="Сравнение сообщений",
                    attachment_type=allure.attachment_type.TEXT
                )
