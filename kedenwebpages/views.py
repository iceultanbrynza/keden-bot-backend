import json
from pathlib import Path

from django.shortcuts import render
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from kedenbot.settings import URL, TELEGRAM_API, DJANGO_URL

import httpx

from .redis_async import redis_client

# Load the JSON
json_path = Path(__file__).resolve().parent / 'data' / 'data.json'
json_path2 = Path(__file__).resolve().parent / 'data' / 'modules.json'
with open(json_path, 'r', encoding='utf-8') as f:
    DATA = json.load(f)
with open(json_path2, 'r', encoding='utf-8') as f:
    MODULES = json.load(f)

CONSTRAINTS = {
    "LAST_NAME": 50,
    "NAME": 50,
    "SECOND_NAME": 50,
    "PHONE": 12,
    "EMAIL": 100
}


def isValidLength(fields:dict):
    for key, constraint in CONSTRAINTS.items():
        value = fields.get(key)

        if isinstance(value, list):
            for item in value:
                val = item.get("VALUE")

                if len(val) > constraint:
                    return False

        elif len(value) > constraint:
            return False

    return True


async def sendPostToCRM(url: str, request: HttpRequest, data: dict = None, headers: dict = None):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response
    except httpx.RequestError:
        return render(request, 'kedenwebpages/error.html', context={'status': 500})
    except httpx.HTTPStatusError as e:
        return render(request, 'kedenwebpages/error.html', context={'status': e.response.status_code})


@csrf_exempt
@require_GET
async def RestrationPage(request: HttpRequest):
    mode = request.GET.get('mode', 'register')
    return render(request, 'kedenwebpages/index.html', context={'mode': mode, 'django_url': DJANGO_URL})


@csrf_exempt
async def RegisterView(request: HttpRequest):
    mode = request.GET.get('mode', 'register')

    body = request.body
    data = json.loads(body)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    if mode == 'edit':
        await sendPostToCRM(f'{URL}/crm.contact.update', request, data, headers)
        return HttpResponse(status=200)

    fields = data.get('FIELDS')
    chat_id = fields.get('UF_CRM_CHAT_ID')

    if not isValidLength(fields):
        return render(request, 'kedenwebpages/error.html', context={
            'status': 400
        })

    await sendPostToCRM(f'{URL}/crm.contact.add', request, data, headers)

    await redis_client.set(str(chat_id), 1, ex=3600)

    return HttpResponse(status=200)


@csrf_exempt
async def fetchContactId(request: HttpRequest):
    if request.method == 'GET':
        chat_id = request.GET.get('UF_CRM_CHAT_ID')
        if not chat_id or chat_id=='undefined':
            print('error')
            return JsonResponse({'error': 'UF_CRM_CHAT_ID is required'}, status=400)

        headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f'{URL}/crm.contact.list?filter[UF_CRM_CHAT_ID]={chat_id}', headers=headers
                )
                json_data = response.json()
                return JsonResponse(json_data)
            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })


@csrf_exempt
async def UVEDModules(request:HttpRequest):
    # structure:
    # GET request returns template and static files. They are accepted from users who press the button
    # POST request make request on Bitrix. They are accepted from static JS file
    if request.method == 'GET':
        # ALL GET REQUEST MUST CONTAIN param type which can be equal to ПИ, ДТ и т.д.
        module = request.GET.get('module')
        sect = request.GET.get('sect')
        message_id = request.GET.get('msg_id')
        chat_id = request.GET.get('c_id')

        uved_root = DATA.get("УВЭД", {})
        options = uved_root.get(module, {}) # Поля/Скрины/Видео/Документ or Секции

        fields = options.get(sect).get('Поля') if sect else options.get('Поля')

        screens = options.get(sect).get('Скрины') if sect else options.get('Скрины')

        video = options.get(sect).get('Видео') if sect else options.get('Видео')

        doc = options.get(sect).get('Документ') if sect else options.get('Документ')

        module_id = MODULES.get(module)

        context = {
            "field_names": fields or [],
            "screens": screens,
            "video": video,
            "doc": doc,
            "role": 'uved',
            "message_id": message_id,
            "chat_id": chat_id,
            "module_id": int(module_id),
            "django_url": DJANGO_URL
        }

        return render(request, 'kedenwebpages/bugreport.html', context=context)

    if request.method == 'POST':
        msg_id = request.GET.get("msg_id")
        chat_id = request.GET.get("chat_id")
        body = request.body
        data = json.loads(body)

        # validation
        resultText = data.get('fields', {}).get('ufCrm168Text')
        if len(resultText) > 2000:
            return JsonResponse({"error": "Text too long or missing"}, status=400)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{URL}/crm.item.add', json=data)
                json_data = response.json()
                response = await client.get(f'{TELEGRAM_API}/deleteMessage?chat_id={chat_id}&message_id={msg_id}')
                return JsonResponse(json_data)
            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })


@csrf_exempt
async def UDLModules(request:HttpRequest):
    if request.method == 'GET':
        # ALL GET REQUEST MUST CONTAIN param type which can be equal to ПИ, ДТ и т.д.
        module = request.GET.get('module')
        sect = request.GET.get('sect')
        message_id = request.GET.get('msg_id')
        chat_id = request.GET.get('c_id')

        udl_root = DATA.get("УДЛ", {})
        options = udl_root.get(module, {}) # Поля/Скрины/Видео/Документ or Секции

        fields = options.get(sect, {}).get('Поля') if sect else options.get('Поля')

        screens = options.get(sect, {}).get('Скрины') if sect else options.get('Скрины')

        video = options.get(sect, {}).get('Видео') if sect else options.get('Видео')

        doc = options.get(sect, {}).get('Документ') if sect else options.get('Документ')

        module_id = MODULES.get(module)

        context = {
            "field_names": fields or [],
            "screens": screens,
            "video": video,
            "doc": doc,
            "role": 'udl',
            "message_id": message_id,
            "chat_id": chat_id,
            "module_id": module_id,
            "django_url": DJANGO_URL
        }

        return render(request, 'kedenwebpages/bugreport.html', context=context)

    if request.method == 'POST':
        msg_id = request.GET.get("msg_id")
        chat_id = request.GET.get("chat_id")
        body = request.body
        data = json.loads(body)

        # validation
        resultText = data.get('fields', {}).get('ufCrm168Text')
        if len(resultText) > 2000:
            return JsonResponse({"error": "Text too long or missing"}, status=400)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{URL}/crm.item.add', json=data)
                json_data = response.json()
                response = await client.get(f'{TELEGRAM_API}/deleteMessage?chat_id={chat_id}&message_id={msg_id}')
                return JsonResponse(json_data)
            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })


@csrf_exempt
async def return_filled_application_form(request:HttpRequest, id:int=None):
    # передавай параметр id
    if request.method == 'GET':
        # names for fileds
        fields_for_context: dict[str, str] = {}
        urls: list[str] = []

        # возвращает список с одной задачей (item)
        response = await sendPostToCRM(url=f'{URL}/crm.item.list.json?entityTypeId=1444&filter[id]={id}', request=request)
        json_data = response.json()
        result = json_data.get('result', {})
        items = result.get('items', [])
        if not items:
            return
        item = items[0]
        # в поле ufCrm168Text хранится ответ тех.поддержки, который нужно разпарсить
        text = item['ufCrm168Text']
        
        fields = text.split('\n')
        for field in fields:
            try:
                key, value = field.split(': ', 1)
            except ValueError:
                continue  # строка без ': ', пропускаем
            # файлы не показываются в веб-страничке, отсылаются отдельно через телеграм (при условии что пользователь нажал на кнопку)
            if 'Скрин' in key or 'Видео' in key or 'Фото' in key or 'Документ' in key or 'ПДФ' in key:
                continue

            fields_for_context[key] = value

        # ссылки на файлы
        files = item['ufCrm168Files']
        for file in files:
            url = file['urlMachine']
            print(file['urlMachine'])
            urls.append(url)

        context = {
            'fields': fields_for_context,
            'urls': urls,
            "django_url": DJANGO_URL
        }

        return render(request, 'kedenwebpages/myapplication.html', context=context)

    if request.method == 'POST':
        chat_id = request.GET.get('chat_id')
        body = request.body
        urls = json.loads(body)
        media = [{"type": "document", "media": url} for url in urls]
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{TELEGRAM_API}/sendMediaGroup',
                                            json={
                                                "chat_id": chat_id,
                                                "media": media
                                            })
                json_data = response.json()
                return JsonResponse(json_data)
            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })
