from django.urls import path
from api.views import SmsSendApiHandler

app_name = 'api'

urlpatterns = [
    path("v1/send/sms", SmsSendApiHandler.as_view(),name='refresh-token'),
]

