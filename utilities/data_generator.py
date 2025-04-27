from faker import Faker
import allure
from datetime import datetime
import random
import string



class DataGenerator:

    @staticmethod
    def create_fake_user():
        """Метод для создания фейковых данных заказчика."""
        with allure.step("Создаём фейковые данные заказчика"):
            fake = Faker("ru_RU")
            name = fake.first_name_female()
            surname = fake.last_name_female()
            email = fake.email()
            phone = fake.phone_number()
            password = fake.password(length=10)

            user = {"name": name,
                        "surname": surname,
                        "email": email,
                        "phone": phone,
                        "password": password
                        }
            return user

    @staticmethod
    def generator_uid():
        with allure.step("Генерируем uid"):
            """Метод для генерации uid"""
            fake = Faker()
            uid = fake.uuid4()
            return uid

    @staticmethod
    def generate_unique_number():
        """
        Генерирует уникальное числовое значение из текущего времени
        в формате ЧЧММССДДММГГГГ (часы-минуты-секунды-день-месяц-год)
        Например: 14302415052024 для 14:30:24 15 мая 2024 года
        """
        with allure.step("Генерируем уникальный номер"):
            now = datetime.now()
            return int(now.strftime("%H%M%S%d%m%Y"))

    @staticmethod
    def generate_pure_letter_code(length=12):
        """Генерирует рандомно буквенное значение"""
        with allure.step("Генерирует рандомно буквенное значение"):
            return ''.join(random.choices(string.ascii_uppercase, k=length))

    @staticmethod
    def generate_amount() -> int:
        """Генерирует сумму от 1000 до 99999"""
        with allure.step("Генерирует сумму"):
            return random.randint(1000, 99999)

