import json


class DecodeRequestBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.content_type == 'application/json':
            try:
                body_text = request.body.decode('utf-8')
                body_data = json.loads(body_text)
                request._body = json.dumps(body_data).encode('utf-8')
            except UnicodeDecodeError:
                pass  # Ошибка декодирования, оставляем body без изменений
        response = self.get_response(request)
        return response
