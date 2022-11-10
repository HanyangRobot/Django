import json
import time
import datetime
import uuid
import hmac
import hashlib
import requests
import platform
from django.conf import settings

# 아래 값은 필요시 수정
from django.http import Http404, HttpResponse
from django.views import View

protocol = 'https'
domain = 'api.coolsms.co.kr'
prefix = ''


class SmsSendApiHandler(View):

    def dispatch(self, request, *args, **kwargs):
        return super(SmsSendApiHandler, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        return HttpResponse("GET 요청을 잘받았다")

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)
        if data is None:
            raise Http404
        print('data')
        receiver = data.get('receiver', None)
        _data = {
            'messages': [
                {
                    'to': receiver,
                    'from': settings.SMS_SENDER_PHONE_NUMBER,
                    'text': data.get('content', None),
                    'type': 'sms',
                }
            ]
        }
        send_sms_message(_data)
        return HttpResponse("Sending SMS Job is enqueue")

    def put(self, request, *args, **kwargs):
        return HttpResponse("POST 요청을 잘받았다")

    def delete(self, request, *args, **kwargs):
        return HttpResponse("POST 요청을 잘받았다")

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

    return requests.post(get_url('/messages/v4/send-many'), headers=get_headers(api_key, api_secret), json=parameter)

