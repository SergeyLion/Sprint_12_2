import pytest
from settings.settings_doska import SettingsDoska as Sd


class TestDeleteListing:
    def test_delete_listing_success(self, api_client, auth_token, create_test_listing):
        """
        Тест успешного удаления объявления
        Проверяет:
        1. Статус код при удалении
        2. Тело ответа
        """
        listing_id = create_test_listing["id"]

        # Заголовки с токеном авторизации
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json"
        }

        # 1. Отправляем DELETE запрос
        delete_response = api_client.delete(
            endpoint=f"{Sd.ENDPOINT_LISTINGS}/{listing_id}",
            headers=headers
        )
        print(delete_response.json())

        # Проверяем статус код удаления
        assert delete_response.status_code == 200, (
            f"Ожидался статус код 200 (Ok), но получен {delete_response.status_code}. "
            f"Ответ сервера: {delete_response.text}"
        )

        delete_data = delete_response.json()
        assert "message" in delete_data
        assert delete_data["message"] == "Объявление удалено успешно"


