from django.shortcuts import render
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import httpx
import json, os
from pathlib import Path

json_path = Path(__file__).resolve().parent / 'data' / 'data.json'
json_path2 = Path(__file__).resolve().parent / 'data' / 'modules.json'
# Load the JSON
with open(json_path, 'r', encoding='utf-8') as f:
    DATA = json.load(f)
with open(json_path2, 'r', encoding='utf-8') as f:
    MODULES = json.load(f)

URL = os.environ['BITRIX_API']
TELEGRAM_API = os.environ['TELEGRAM_API']

# Create your views here.
@csrf_exempt
async def RegisterView(request: HttpRequest):
    mode = request.GET.get('mode', 'register')
    context = {'mode': mode}

    if request.method == 'POST':
        mode = request.GET.get('mode', 'register')
        if mode == 'edit':
            body = request.body
            data = json.loads(body)
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(f'{URL}/crm.contact.update',
                                            json=data, headers=headers)


        else:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            body = request.body
            data = json.loads(body)

            print(data)

            async with httpx.AsyncClient() as client:
                response = await client.post(f'{URL}/crm.contact.add',
                                            json=data, headers=headers)


            content = {
                'result': 'ok'
            }
            return JsonResponse(content)

    return render(request, 'kedenwebpages/index.html', context=context)

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

        uved_root = DATA.get("УВЭД", {})
        options = uved_root.get(module, {}) # Поля/Скрины/Видео/Документ or Секции

        fields = options.get(sect).get('Поля') if sect else options.get('Поля')

        screens = options.get(sect).get('Скрины') if sect else options.get('Скрины')

        video = options.get(sect).get('Видео') if sect else options.get('Видео')

        doc = options.get(sect).get('Документ') if sect else options.get('Документ')

        context = {
            "field_names": fields or [],
            "screens": screens,
            "video": video,
            "doc": doc
        }

        # Добавить module_id, если есть
        module_id = MODULES.get(module)
        if module_id:
            context["module_id"] = module_id

        return render(request, 'kedenwebpages/bugreport.html', context=context)

    if request.method == 'POST':
        body = request.body
        data = json.loads(body)
        print(len(data['fields']['ufCrm168Files']))
        # entityTypeId = data['entityTypeId']
        # text = data['fields']

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{URL}/crm.item.add', json=data)
                json_data = response.json()
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

        udl_root = DATA.get("УДЛ", {})
        options = udl_root.get(module, {}) # Поля/Скрины/Видео/Документ or Секции

        fields = options.get(sect).get('Поля') if sect else options.get('Поля')

        screens = options.get(sect).get('Скрины') if sect else options.get('Скрины')

        video = options.get(sect).get('Видео') if sect else options.get('Видео')

        doc = options.get(sect).get('Документ') if sect else options.get('Документ')

        context = {
            "field_names": fields or [],
            "screens": screens,
            "video": video,
            "doc": doc
        }

        # Добавить module_id, если есть
        module_id = MODULES.get(module)
        if module_id:
            context["module_id"] = module_id

        return render(request, 'kedenwebpages/bugreport.html', context=context)

    if request.method == 'POST':
        body = request.body
        data = json.loads(body)
        print(len(data['fields']['ufCrm168Files']))
        # entityTypeId = data['entityTypeId']
        # text = data['fields']

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{URL}/crm.item.add', json=data)
                json_data = response.json()
                return JsonResponse(json_data)
            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

@csrf_exempt
async def return_filled_application_form(request:HttpRequest, id:int):
    # передавай параметр id
    if request.method == 'GET':
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{URL}/crm.item.list.json?entityTypeId=1444&filter[id]={id}')

            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

            else:
                json_data = response.json()
                result = json_data.get('result', {})
                items = result.get('items', [])
                if not items:
                    return

        fields_for_context: dict[str, str] = {}
        files_for_context: list[str] = []

        item = items[0]
        text = item['ufCrm168Text']

        fields = text.split('\n')

        for field in fields:
            try:
                key, value = field.split(': ', 1)
            except ValueError:
                continue  # строка без ': ', пропускаем

            if 'Скрин' in key or 'Видео' in key or 'Фото' in key:
                files_for_context.append(key)
                continue

            fields_for_context[key] = value

        context = {
            'fields': fields_for_context,
            'files': files_for_context
        }

        return render(request, 'kedenwebpages/myapplication.html', context=context)

# outbound webhook requests
@csrf_exempt
async def notify_user_about_registration(request:HttpRequest):
    if request.method == "POST":
        print("FROM BITRIX:", request.POST)
        id = request.POST.get('data[FIELDS][ID]')
        event = request.POST.get('event')

        # request on Bitrix for obtaining chat id
        req = f'{URL}/crm.contact.get'
        params = {
            'ID': id
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(req, params=params)

            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

            else:
                res = response.json()
                result = res.get('result', {})
                chat_id = result.get('UF_CRM_CHAT_ID', '')

        # send message to Telegram
        url = f'{TELEGRAM_API}/sendMessage'
        text = "Вы успешно обновили данные регистрации" if event == 'ONCRMCONTACTUPDATE' else "Вы успешно зарегистрировались"

        payload = {
            'chat_id': chat_id,
            'text': text
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, json=payload)

            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

        return JsonResponse({'result': 'OK'}, status=200)

@csrf_exempt
async def notify_user_about_appl(request:HttpRequest):
    if request.method == "POST":
        print("FROM BITRIX:", request.POST)
        id = request.POST.get('data[FIELDS][ID]')
        event = request.POST.get('event') # ONCRMDYNAMICITEMADD

        # request on Bitrix for obtaining chat id
        req = f'{URL}/crm.contact.get'
        params = {
            'ID': id
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(req, params=params)

            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

            else:
                res = response.json()
                result = res.get('result', {})
                chat_id = result.get('UF_CRM_CHAT_ID', '')

        # send message to Telegram
        url = f'{TELEGRAM_API}/sendMessage'
        text = "Ваше заявление принято. Тех.поддержка обязательно рассмотрит вашу проблему в ближайшее время"

        payload = {
            'chat_id': chat_id,
            'text': text
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, json=payload)

            except httpx.RequestError as e:
                return render(request, 'kedenwebpages/error.html', context={
                    'status': 500
                })

        return JsonResponse({'result': 'OK'}, status=200)