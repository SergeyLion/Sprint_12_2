import time
import allure
import pytest
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg
from faker import Faker


@allure.feature("Обновление объявлений")
class TestUpdateListing:
    fake = Faker("ru_RU")

    @allure.story("Полное обновление объявления")
    @allure.title("Проверка успешного полного обновления объявления")
    def test_full_update_listing_success(self, api_client, auth_token, create_test_listing, kandinsky_api,
                                         delete_test_listing):
        with allure.step("1. Подготовка данных для обновления"):
            listing_id = create_test_listing["id"]
            delete_test_listing['id'] = listing_id
            allure.attach(str(create_test_listing), name="Исходные данные объявления",
                          attachment_type=allure.attachment_type.JSON)

            # Генерация нового изображения
            image_data = kandinsky_api.generate_image("Новое изображение для обновления")
            allure.attach(image_data, name="Новое изображение", attachment_type=allure.attachment_type.JPG)

            # Подготовка файлов
            test_files = [
                ('images', (f'image_{Dg.generator_uid()}.jpg', image_data, 'image/jpeg'))
            ]
            updated_data = Dg.create_listing_data()
            allure.attach(str(updated_data), name="Данные для обновления", attachment_type=allure.attachment_type.JSON)

        with allure.step("2. Отправка запроса на обновление"):
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json"
            }

            response = api_client.patch(
                endpoint=f"{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}",
                headers=headers,
                data=updated_data,
                files=test_files
            )

            allure.attach(
                f"Request: PATCH {Sd.BASE_URL}{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}\n"
                f"Headers: {headers}\n"
                f"Data: {updated_data}\n"
                f"Response Status: {response.status_code}\n"
                f"Response Body: {response.text}",
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. Проверка статус-кода ответа"):
            assert response.status_code == 200, (
                f"Ожидался статус код 200, но получен {response.status_code}. "
                f"Ответ сервера: {response.text}"
            )

        with allure.step("4. Проверка обновленных данных"):
            updated_listing = response.json()
            allure.attach(str(updated_listing), name="Обновленные данные", attachment_type=allure.attachment_type.JSON)

            fields_to_check = [
                ("name", "Название"),
                ("category", "Категория"),
                ("condition", "Состояние"),
                ("city", "Город"),
                ("description", "Описание"),
                ("price", "Цена")
            ]

            for field, name in fields_to_check:
                with allure.step(f"4.1 Проверка поля {name}"):
                    if field == "price":
                        assert updated_listing[field] == int(updated_data[field]), f"{name} не обновилась"
                    else:
                        assert updated_listing[field] == updated_data[field], f"{name} не обновилось"
                    allure.attach(f"Поле {name} успешно обновлено", name="Результат проверки",
                                  attachment_type=allure.attachment_type.TEXT)

            with allure.step("4.2 Проверка даты обновления"):
                assert updated_listing["updatedAt"] != create_test_listing[
                    "updatedAt"], "Дата обновления должна измениться"
                allure.attach(
                    f"Было: {create_test_listing['updatedAt']}\n"
                    f"Стало: {updated_listing['updatedAt']}",
                    name="Сравнение дат обновления",
                    attachment_type=allure.attachment_type.TEXT
                )

    @pytest.mark.parametrize("field, new_value", [
        ("name", f"Объявление обновленное {Dg.generator_uid()}"),
        ("category", 'Технологии'),
        ("condition", 'Б/у'),
        ("city", 'Казань'),
        ("description", fake.sentence(nb_words=10)),
        ("price", fake.pyint(min_value=100, max_value=1000000)),
    ])
    @allure.story("Частичное обновление объявления")
    @allure.title("Проверка обновления поля '{field}'")
    def test_update_single_field_listing_success(self, api_client, auth_token, create_test_listing, delete_test_listing,
                                                 field, new_value):
        with allure.step("1. Подготовка данных для обновления"):
            listing_id = create_test_listing["id"]
            delete_test_listing['id'] = listing_id
            update_data = create_test_listing.copy()
            update_data[field] = new_value

            allure.attach(
                f"Обновляемое поле: {field}\n"
                f"Новое значение: {new_value}",
                name="Данные для обновления",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("2. Отправка запроса на обновление"):
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json"
            }

            time.sleep(1)  # Для различия дат создания и обновления
            response = api_client.patch(
                endpoint=f"{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}",
                headers=headers,
                json=update_data
            )

            allure.attach(
                f"Request: PATCH {Sd.BASE_URL}{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}\n"
                f"Headers: {headers}\n"
                f"Data: {{'{field}': '{new_value}'}}\n"
                f"Response Status: {response.status_code}\n"
                f"Response Body: {response.text}",
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. Проверка статус-кода ответа"):
            assert response.status_code == 200, (
                f"Ожидался статус код 200, но получен {response.status_code}. "
                f"Ответ сервера: {response.text}"
            )

        with allure.step("4. Проверка обновленных данных"):
            updated_listing = response.json()

            with allure.step("4.1 Проверка обновленного поля"):
                expected_value = new_value
                assert updated_listing[field] == expected_value, (
                    f"Поле {field} не обновилось. "
                    f"Ожидалось: {expected_value}, получено: {updated_listing[field]}"
                )
                allure.attach(f"Поле {field} успешно обновлено", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("4.2 Проверка неизменившихся полей"):
                unchanged_fields = [key for key in create_test_listing
                                    if key not in [field, "updatedAt", "id", "img1", "img2", "img3"]]
                for key in unchanged_fields:
                    assert updated_listing[key] == create_test_listing[key], (
                        f"Поле {key} изменилось, хотя не должно было. "
                        f"Было: {create_test_listing[key]}, стало: {updated_listing[key]}"
                    )
                allure.attach(f"Проверено {len(unchanged_fields)} неизменившихся полей", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("4.3 Проверка даты обновления"):
                assert updated_listing["updatedAt"] != create_test_listing["updatedAt"], (
                    "Дата обновления должна измениться после редактирования")
                allure.attach(
                    f"Было: {create_test_listing['updatedAt']}\n"
                    f"Стало: {updated_listing['updatedAt']}",
                    name="Сравнение дат обновления",
                    attachment_type=allure.attachment_type.TEXT
                )

    @allure.story("Попытка обновления чужим пользователем")
    @allure.title("Проверка запрета обновления чужого объявления")
    def test_update_listing_by_other_user_should_fail(self, api_client, auth_token, another_auth_token,
                                                      create_test_listing, delete_test_listing):
        with allure.step("1. Подготовка данных для теста"):
            listing_id = create_test_listing["id"]
            delete_test_listing['id'] = listing_id
            update_data = create_test_listing.copy()
            update_data["name"] = "Попытка изменения другим пользователем"

            allure.attach(str(create_test_listing), name="Исходные данные объявления",
                          attachment_type=allure.attachment_type.JSON)

        with allure.step("2. Отправка запроса от другого пользователя"):
            headers = {
                "Authorization": f"Bearer {another_auth_token}",
                "Accept": "application/json"
            }

            response = api_client.patch(
                endpoint=f"{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}",
                headers=headers,
                data=update_data
            )

            allure.attach(
                f"Request: PATCH {Sd.BASE_URL}{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}\n"
                f"Headers: {headers}\n"
                f"Data: {update_data}\n"
                f"Response Status: {response.status_code}\n"
                f"Response Body: {response.text}",
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("3. Проверка статус-кода ответа"):
            assert response.status_code == 401, (
                f"Ожидался статус код 401 (Unauthorized), но получен {response.status_code}. "
                f"Ответ сервера: {response.text}"
            )

        with allure.step("4. Проверка тела ответа об ошибке"):
            error_response = response.json()
            allure.attach(str(error_response), name="Ответ об ошибке", attachment_type=allure.attachment_type.JSON)

            with allure.step("4.1 Проверка наличия обязательных полей"):
                required_fields = ["message", "error", "statusCode"]
                missing_fields = [field for field in required_fields if field not in error_response]
                assert not missing_fields, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
                allure.attach("Все обязательные поля присутствуют", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("4.2 Проверка значений полей"):
                expected_values = {
                    "message": "Оффер не найден или у вас нет прав на его редактирование",
                    "error": "Unauthorized",
                    "statusCode": 401
                }

                for field, expected in expected_values.items():
                    assert error_response[field] == expected, (
                        f"Неверное значение поля {field}. "
                        f"Ожидалось: '{expected}', получено: '{error_response[field]}'"
                    )
                    allure.attach(f"Поле {field} соответствует ожидаемому", name="Результат проверки",
                                  attachment_type=allure.attachment_type.TEXT)

