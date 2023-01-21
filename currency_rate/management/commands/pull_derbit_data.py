from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
import requests
from currency_rate.models import BtcRecords
from decimal import Decimal
import redis


class Command(BaseCommand):
    """
    Команда, которая обращается к API Derbit, и берет от туда информацию о счете и курсе биткойна.
    Так как Апи-Ключ нужно постоянно обновлять он хранится в redis,
    """

    r = redis.StrictRedis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB_NUM,
        charset="utf-8",
        decode_responses=True,
    )

    def create_api_token(self):
        """
        Метод создает API ключ Derbit и кладет его в редис
        Должен запускаться 1 раз
        """
        headers = {
            "Content-Type": "application/json",
        }

        params = {
            "client_id": settings.DERBIT_CLIENT_ID,
            "client_secret": settings.DERBIT_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

        response = requests.get(
            "https://test.deribit.com/api/v2/public/auth",
            params=params,
            headers=headers,
        )
        response.raise_for_status()

        api_key = response.json()["result"]["access_token"]
        refresh_token = response.json()["result"]["refresh_token"]
        self.r.set("DERBIT_API_KEY", api_key)
        self.r.set("DERBIT_REFRESH_TOKEN", refresh_token)

    def refresh_api_token(self):
        """
        Метод обновляет API ключ Derbit и кладет его в редис
        Должен запускаться, когда токен просрочился
        """
        refresh_token = self.r.get("DERBIT_REFRESH_TOKEN")

        headers = {
            "Content-Type": "application/json",
        }

        params = {
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        response = requests.get(
            "https://test.deribit.com/api/v2/public/auth",
            params=params,
            headers=headers,
        )
        response.raise_for_status()

        api_key = response.json()["result"]["access_token"]
        refresh_token = response.json()["result"]["refresh_token"]
        self.r.set("DERBIT_API_KEY", api_key)
        self.r.set("DERBIT_REFRESH_TOKEN", refresh_token)

    @property
    def api_key(self):
        """
        Возвращает API ключ
        """
        key = self.r.get("DERBIT_API_KEY")
        if not key:
            self.create_api_token()
            key = self.r.get("DERBIT_API_KEY")

        return key

    def get_deposits(self, currency="BTC"):
        """
        Метод обращается к API Derbit и получает баланс пользователя
        """
        url = "https://test.deribit.com/api/v2/private/get_deposits"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        params = {
            "count": "1",
            "currency": currency,
        }

        response = requests.get(url, params=params, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 400:
                self.refresh_api_token()

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()

        current_amount = response.json()["result"]["data"][0]["amount"]
        return current_amount

    def get_price(self, index_name="btc_usd"):
        """
        Метод обращается к API Derbit и получает курс биткойна
        """
        url = "https://test.deribit.com/api/v2/public/get_index_price"

        headers = {
            "Content-Type": "application/json",
        }

        params = {
            "index_name": index_name,
        }

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        currency_price = response.json()["result"]["index_price"]
        return currency_price

    def handle(self, *args, **options):
        """
        Получает нужную информацию по API и создает записи в БД
        """
        current_amount = self.get_deposits()
        current_price = self.get_price()
        current_assets_price = current_price * current_amount

        first_record = BtcRecords.objects.order_by("calculation_date").first()

        if not first_record:
            BtcRecords.objects.create(
                calculation_date=timezone.now(),
                btc_price=current_price,
                assets_price=current_assets_price,
                pnl=0,
                index_pnl=1,
            )
            return

        current_total_pnl = Decimal(current_assets_price) - first_record.assets_price
        current_total_index_pnl = round(
            current_assets_price / float(first_record.assets_price), 5
        )

        BtcRecords.objects.create(
            calculation_date=timezone.now(),
            btc_price=current_price,
            assets_price=current_assets_price,
            pnl=current_total_pnl,
            index_pnl=current_total_index_pnl,
        )
