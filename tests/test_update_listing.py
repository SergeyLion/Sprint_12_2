import time
from time import sleep

import pytest
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg
from faker import Faker


class TestUpdateListing:
    fake = Faker("ru_RU")

    def test_full_update_listing_success(self, api_client, auth_token, create_test_listing, kandinsky_api):
        listing_id = create_test_listing["id"]


        # Генерация нового изображения
        image_data = kandinsky_api.generate_image("Новое изображение для обновления")

        # Подготовка файлов
        test_files = [
            ('images', (f'image_{Dg.generator_uid()}.jpg', image_data, 'image/jpeg'))
        ]
        updated_data = Dg.create_listing_data()


        # Заголовки запроса
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

        # Проверка статус-кода
        assert response.status_code == 200, (
            f"Ожидался статус код 200, но получен {response.status_code}. "
            f"Ответ сервера: {response.text}"
        )

        # Получаем обновленные данные объявления
        updated_listing = response.json()

        # Проверки обновленных данных
        assert updated_listing["name"] == updated_data["name"], "Название не обновилось"
        assert updated_listing["category"] == updated_data["category"], "Категория не обновилась"
        assert updated_listing["condition"] == updated_data["condition"], "Состояние не обновилось"
        assert updated_listing["city"] == updated_data["city"], "Город не обновился"
        assert updated_listing["description"] == updated_data["description"], "Описание не обновилось"
        assert updated_listing["price"] == int(updated_data["price"]), "Цена не обновилась"

        # Проверка что дата обновления изменилась
        assert updated_listing["updatedAt"] != create_test_listing["updatedAt"], "Дата обновления должна измениться"

    @pytest.mark.parametrize("field, new_value", [
        ("name", f"Объявление обновленное {Dg.generator_uid()}"),
        ("category", 'Технологии'),
        ("condition", 'Б/у'),
        ("city", 'Казань'),
        ("description", fake.sentence(nb_words=10)),
        ("price", fake.pyint(min_value=100, max_value=1000000)),
    ])
    def test_update_single_field_listing_success(self, api_client, auth_token, create_test_listing, field, new_value):
        """
        Тест обновления каждого поля по отдельности
        """
        listing_id = create_test_listing["id"]

        # Создаем копию исходных данных
        update_data = create_test_listing.copy()

        # Обновляем только нужное поле
        update_data[field] = new_value


        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        }

        # Отправляем PATCH запрос
        time.sleep(1) # Надо, что бы дата создания и редактировании отличалась
        response = api_client.patch(
            endpoint=f"{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}",
            headers=headers,
            json=update_data
        )

        # Проверяем успешность запроса
        assert response.status_code == 200, (
            f"Ожидался статус код 200, но получен {response.status_code}. "
            f"Ответ сервера: {response.text}"
        )

        updated_listing = response.json()

        # Проверяем что обновилось только нужное поле
        expected_value = new_value


        assert updated_listing[field] == expected_value, (
            f"Поле {field} не обновилось. "
            f"Ожидалось: {expected_value}, получено: {updated_listing[field]}"
        )

        # Проверяем что остальные поля остались без изменений
        for key in create_test_listing:
            if key not in [field, "updatedAt", "id", "img1", "img2", "img3"]:  # Исключаем технические поля
                assert updated_listing[key] == create_test_listing[key], (
                    f"Поле {key} изменилось, хотя не должно было. "
                    f"Было: {create_test_listing[key]}, стало: {updated_listing[key]}"
                )

        # Проверяем что дата обновления изменилась
        assert updated_listing["updatedAt"] != create_test_listing["updatedAt"], (
            "Дата обновления должна измениться после редактирования")

    def test_update_listing_by_other_user_should_fail(self, api_client, auth_token, another_auth_token,
                                                      create_test_listing):
        """
        Тест попытки редактирования объявления другим пользователем
        """
        # Получаем ID созданного тестового объявления
        listing_id = create_test_listing["id"]

        # Создаем копию исходных данных
        update_data = create_test_listing.copy()

        # Обновляем только нужное поле
        update_data["name"] = "Попытка изменения другим пользователем"


        # Заголовки с токеном другого пользователя
        headers = {
            "Authorization": f"Bearer {another_auth_token}",
            "Accept": "application/json"
        }

        # Отправляем PATCH запрос от другого пользователя
        response = api_client.patch(
            endpoint=f"{Sd.ENDPOINT_UPDATE_LISTING}/{listing_id}",
            headers=headers,
            data=update_data
        )


        # Проверяем статус код
        assert response.status_code == 401, (
            f"Ожидался статус код 401 (Unauthorized), но получен {response.status_code}. "
            f"Ответ сервера: {response.text}"
        )

        # Проверяем тело ответа
        error_response = response.json()

        # Проверка структуры ответа
        assert "message" in error_response, "В ответе отсутствует поле 'message'"
        assert "error" in error_response, "В ответе отсутствует поле 'error'"
        assert "statusCode" in error_response, "В ответе отсутствует поле 'statusCode'"

        # Проверка значений полей
        assert error_response["message"] == "Оффер не найден или у вас нет прав на его редактирование", (
            f"Неверное сообщение об ошибке. Получено: {error_response['message']}"
        )
        assert error_response["error"] == "Unauthorized", (
            f"Неверный тип ошибки. Получено: {error_response['error']}"
        )
        assert error_response["statusCode"] == 401, (
            f"Неверный статус код в теле ответа. Получено: {error_response['statusCode']}"
        )



