import pytest
from datetime import datetime
from settings.settings_doska import SettingsDoska as Sd
from utilities.data_generator import DataGenerator as Dg
import allure
from pathlib import Path


@allure.feature("Создание объявлений")
@allure.story("Успешное создание объявления")
class TestCreateListing:
    @allure.title("Проверка успешного создания объявления")
    def test_create_listing_success(self, api_client, auth_token, delete_test_listing):
        with allure.step("1. Подготовка тестовых данных"):
            data = Dg.create_listing_data()
            allure.attach(str(data), name="Данные для создания объявления", attachment_type=allure.attachment_type.TEXT)

        with allure.step("2. Подготовка файлов для отправки"):
            # Путь к изображению в проекте
            image_path = Path(__file__).parent.parent / "settings" / "test_image.jpg"

            # Чтение изображения
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()

            test_files = [
                ('images', (f'image_{Dg.generator_uid()}.jpg', image_data, 'image/jpeg'))
            ]

        with allure.step("3. Отправка запроса на создание объявления"):
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Accept": "application/json"
            }

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
                name="Детали запроса и ответа",
                attachment_type=allure.attachment_type.TEXT
            )

        with allure.step("4. Проверка статус-кода ответа"):
            assert response.status_code == 201, (
                f"Ожидался статус код 201, но получен {response.status_code}. "
                f"Ответ сервера: {response.text}"
            )

        with allure.step("5. Обработка и проверка ответа"):
            response_data = response.json()
            delete_test_listing['id'] = response_data['id']
            allure.attach(str(response_data), name="Полный ответ сервера", attachment_type=allure.attachment_type.JSON)

            with allure.step("5.1 Проверка наличия обязательных полей"):
                required_fields = [
                    'id', 'name', 'category', 'condition', 'city',
                    'description', 'price', 'img1', 'owner',
                    'updatedAt', 'createdAt'
                ]
                missing_fields = [field for field in required_fields if field not in response_data]
                assert not missing_fields, f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
                allure.attach("Все обязательные поля присутствуют", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.2 Проверка типов данных"):
                type_checks = [
                    ('id', int),
                    ('name', str),
                    ('category', str),
                    ('condition', str),
                    ('city', str),
                    ('description', str),
                    ('price', int),
                    ('owner', int)
                ]

                type_errors = []
                for field, expected_type in type_checks:
                    if not isinstance(response_data[field], expected_type):
                        type_errors.append(
                            f"Поле '{field}': ожидался {expected_type.__name__}, получен {type(response_data[field]).__name__}")

                assert not type_errors, "Ошибки проверки типов:\n" + "\n".join(type_errors)
                allure.attach("Все типы данных корректны", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.3 Проверка формата дат"):
                try:
                    datetime.fromisoformat(response_data['createdAt'].replace('Z', ''))
                    datetime.fromisoformat(response_data['updatedAt'].replace('Z', ''))
                    allure.attach("Формат дат корректный", name="Результат проверки",
                                  attachment_type=allure.attachment_type.TEXT)
                except ValueError as e:
                    allure.attach(str(e), name="Ошибка формата даты", attachment_type=allure.attachment_type.TEXT)
                    pytest.fail("Некорректный формат даты")

            with allure.step("5.4 Проверка соответствия отправленных и полученных данных"):
                data_comparison = [
                    ('name', 'Название'),
                    ('category', 'Категория'),
                    ('condition', 'Состояние'),
                    ('city', 'Город'),
                    ('description', 'Описание')
                ]

                comparison_errors = []
                for field, name in data_comparison:
                    if response_data[field] != data[field]:
                        comparison_errors.append(
                            f"{name}: ожидалось '{data[field]}', получено '{response_data[field]}'")

                # Проверка цены отдельно, так как она преобразуется в int
                if response_data['price'] != int(data['price']):
                    comparison_errors.append(f"Цена: ожидалось {data['price']}, получено {response_data['price']}")

                assert not comparison_errors, "Несоответствия данных:\n" + "\n".join(comparison_errors)
                allure.attach("Все данные соответствуют отправленным", name="Результат проверки",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.5 Проверка изображений"):
                assert response_data['img1'].startswith('http'), "Ссылка на изображение должна быть URL"
                allure.attach(response_data['img1'], name="Ссылка на изображение",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.6 Проверка дополнительных полей"):
                assert 'isFavorite' in response_data, "Отсутствует поле isFavorite"
                allure.attach(f"isFavorite: {response_data.get('isFavorite')}", name="Поле isFavorite",
                              attachment_type=allure.attachment_type.TEXT)

            with allure.step("5.7 Проверка дат создания и обновления"):
                assert response_data['createdAt'] == response_data[
                    'updatedAt'], "Даты создания и обновления должны совпадать для нового объявления"
                allure.attach(
                    f"createdAt: {response_data['createdAt']}\n"
                    f"updatedAt: {response_data['updatedAt']}",
                    name="Даты создания и обновления",
                    attachment_type=allure.attachment_type.TEXT
                )
