from django.urls import path
from .views import *

app_name = "currency_rate"

urlpatterns = [
    path("", index),
    path(
        "api/get_currencies_data_by_period",
        get_currencies_data_by_period.as_view(),
        name="get_currencies_data_by_period",
    ),
]
