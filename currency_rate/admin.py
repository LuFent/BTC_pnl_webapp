from django.contrib import admin
from currency_rate.models import *


@admin.register(BtcRecords)
class BtcRecordsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "calculation_date",
        "btc_price",
        "assets_price",
        "pnl",
        "index_pnl",
    )
