from django.db import models
from django.core.validators import MinValueValidator


class BtcRecords(models.Model):
    """
        Модель для хранения финансовой информации
    """

    calculation_date = models.DateTimeField("Дата Расчета")

    btc_price = models.DecimalField(
        "Курс Биткойна",
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(0)],
    )

    assets_price = models.DecimalField(
        "Стоимость чистых активов",
        decimal_places=2,
        max_digits=12,
        validators=[MinValueValidator(0)],
    )

    pnl = models.DecimalField(
        "Текущиий PnL",
        decimal_places=2,
        max_digits=12,
    )

    index_pnl = models.FloatField("Текущий Index PnL")
