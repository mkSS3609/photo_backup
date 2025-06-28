import requests
import json

# Я.Токен (введите)
TOKEN = input('Введите свой Я.Токен: ').strip()

# Список всех пород
breeds_dict = requests.get('https://dog.ceo/api/breeds/list/all').json()['message']

# Порода (введите)
while True:
    breed_name = input("Введите название породы (англ): ").lower().strip()
    if breed_name in breeds_dict:
        print('Порода найдена, ожидайте!')
        break
    else:
        print('Такой породы не найдено, повторите попытку!')

# наличие подпороды
availability_sub_breed = breeds_dict[breed_name] != []

# Создание папки
url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
params = {'path': breed_name}
HEADERS = {'Authorization': f'OAuth {TOKEN}'}
response = requests.put(url_create_folder, headers=HEADERS, params=params)
print(f'\tПапка "{breed_name}" создана...')

list_for_json = []

def image_upload(image_url_, breed_, sub_breed_=None, is_sub_breed=availability_sub_breed, headers=None):
    headers = HEADERS if headers is None else headers # устранение предупреждения "Default argument value is mutable"
    url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    if is_sub_breed:
        filename = f'{sub_breed_}_{breed_}_{image_url_.split('/')[-1].split('.')[0]}'
    else:
        filename = f'{breed_}_{image_url_.split('/')[-1].split('.')[0]}'
    params_ = {'path': f'{breed_}/{filename}','url': image_url_}
    requests.post(url_upload, headers=headers, params=params_)
    print(f'\tИзображение {filename} загружено на диск...')
    list_for_json.append({'file_name': f'{filename}.{image_url_.split('/')[-1].split('.')[1]}'})

def url_sub_breed(breed, sub_breeds_names):
    for sub_breed in sub_breeds_names:
        image_url = requests.get(f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random').json()['message']
        print(f'\tИзображение {sub_breed}-{breed} найдено...')
        image_upload(image_url, breed, sub_breed)

def url_breed(breed):
    image_url = requests.get(f'https://dog.ceo/api/breed/{breed}/images/random').json()['message']
    print(f'\tИзображение {breed} найдено...')
    image_upload(image_url, breed)

if availability_sub_breed:
    url_sub_breed(breed_name, breeds_dict[breed_name])
else:
    url_breed(breed_name)

with open('upload_files.json', 'w') as f:
    json.dump(list_for_json, f)

print('\tupload_files.json создан...')
print('Готово, проверяйте!')