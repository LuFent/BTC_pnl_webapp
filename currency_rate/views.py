from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import *
from django.utils import timezone


def index(request):
    """
    Вьюха, возвращающая главную страницу
    """
    return render(request, "index.html")


class get_currencies_data_by_period(APIView):
    """
    REST-API Вьюха, которая получает в параметрах GET-запроса начало и конец временного периода
     и отдает pnl, pnl_%, index_pnl
    """

    def get(self, request, format=None):
        datetime_format_string = "%Y_%m_%d_%H_%M_%S"
        tz = timezone.get_current_timezone()

        try:
            period_start = request.query_params.get("period_start")
            if period_start:
                period_start = datetime.strptime(
                    period_start, datetime_format_string
                ).replace(tzinfo=tz)

            period_end = request.query_params.get("period_end")
            if period_end:
                period_end = datetime.strptime(
                    period_end, datetime_format_string
                ).replace(tzinfo=tz)

        except Exception:
            return Response(data="Wrong parameters", status=status.HTTP_400_BAD_REQUEST)

        records = BtcRecords.objects.all()

        if period_start:
            records = records.filter(calculation_date__gte=period_start)
        if period_end:
            records = records.filter(calculation_date__lte=period_end)

        if not records:
            return Response(data="Not Found", status=status.HTTP_404_NOT_FOUND)

        first_record = records.first()
        last_record = records.last()

        return Response(
            {
                "pnl": last_record.assets_price - first_record.assets_price,
                "pnl_%": round(
                    (last_record.assets_price / first_record.assets_price - 1) * 100, 5
                ),
                "index_pnl": round(
                    last_record.assets_price / first_record.assets_price, 5
                ),
            }
        )
