import time
import datetime
import uuid
import hmac
import hashlib
import requests
import platform
from django.conf import settings
from drf_yasg import openapi
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

protocol = 'https'
domain = 'api.coolsms.co.kr'
prefix = ''
param1 = openapi.Parameter('receiver', openapi.IN_FORM, description="test manual param", type=openapi.TYPE_STRING)
param2 = openapi.Parameter('content', openapi.IN_FORM, description="test manual param", type=openapi.TYPE_STRING)
class SmsSendApiHandler(APIView):
    parser_classes = [FormParser,MultiPartParser]
    @swagger_auto_schema(
        manual_parameters=[param1,param2],
        responses={
            200:openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'status':openapi.Schema('status',type=openapi.TYPE_STRING)
                }
            )

        }
    )
    def post(self,request):
        receiver = request.POST['receiver']
        content = request.POST['content']
        _data = {
            'messages': [
                {
                    'to': [receiver],
                    'from': settings.SMS_SENDER_PHONE_NUMBER,
                    'text': content ,
                    'type': 'sms',
                }
            ]
        }
        response = send_sms_message(_data)
        status_str=response.json()['status']
        custom_response = {'status':status_str}
        return Response(custom_response,status=status.HTTP_200_OK,content_type="application/json")


def unique_id():
    return str(uuid.uuid1().hex)


def get_iso_datetime():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()


def get_signature(key, msg):
    return hmac.new(key.encode(), msg.encode(), hashlib.sha256).hexdigest()


def get_headers(api_key, api_secret):
    date = get_iso_datetime()
    salt = unique_id()
    combined_string = date + salt

    return {
        'Authorization': 'HMAC-SHA256 ApiKey=' + api_key + ', Date=' + date + ', salt=' + salt + ', signature=' +
                         get_signature(api_secret, combined_string),
        'Content-Type': 'application/json; charset=utf-8'
    }


def get_url(path):
    url = '%s://%s' % (protocol, domain)
    if prefix != '':
        url = url + prefix
    url = url + path
    return url


def send_sms_message(parameter):
    # 반드시 관리 콘솔 내 발급 받으신 API KEY, API SECRET KEY를 입력해주세요

    api_key = settings.COOL_SMS_API_KEY
    api_secret = settings.COOL_SMS_API_SECRET

    parameter['agent'] = {
        'sdkVersion': 'python/4.2.0',
        'osPlatform': platform.platform() + " | " + platform.python_version()
    }
    res = requests.post(get_url('/messages/v4/send-many'), headers=get_headers(api_key, api_secret), json=parameter)
    return res

