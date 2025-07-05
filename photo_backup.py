import requests
import json

def check_yandex_token():
    """Проверяет валидность токена Яндекс Диска"""
    while True:
        token = input('Введите свой Я.Токен: ').strip()
        url = 'https://cloud-api.yandex.net/v1/disk'
        headers = {'Authorization': f'OAuth {token}'}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f'\tНеверный токен Яндекс.Диска! повторите попытку...\n')
        else:
            print('\tПользователь авторизован!\n')
            return headers

def get_breeds_dict():
    """Получает словарь всех пород собак с API dog.ceo"""
    url = 'https://dog.ceo/api/breeds/list/all'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Ошибка API dog.ceo: {response.status_code}')
    return response.json()['message']

def get_user_input_breeds(breeds):
    """Запрашивает у пользователя название породы и проверяет ее существование"""
    while True:
        breed = input("Введите название породы (на английском): ").lower().strip()
        if breed in breeds:
            print(f'\tПорода "{breed}" найдена, начинаем обработку!\n')
            return breed
        print(f'\tПорода "{breed}" не найдена, попробуйте снова!\n')

def create_yandex_folder(breed, headers):
    """Создает папку на Яндекс Диске"""
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': breed}
    response = requests.put(url, headers=headers, params=params)
    if response.status_code == 409:
        print(f'\tПапка "{breed}" уже существует...')
    elif response.status_code != 201:
        raise Exception(f"Ошибка создания папки: {response.json().get('message', 'Неизвестная ошибка')}")
    else:
        print(f'\tПапка "{breed}" успешно создана...')

def upload_image(headers, image_url, filename, breed):
    """Загружает изображение на Яндекс Диск"""
    url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': f'{breed}/{filename}', 'url': image_url}
    response = requests.post(url_upload, headers=headers, params=params)
    if response.status_code != 202:
        raise Exception(f"Ошибка загрузки изображения {filename}: {response.json().get('message', 'Неизвестная ошибка')}")
    print(f'\tИзображение {filename} загружено на диск...')
    file_info = {'file_name': f'{filename}.{image_url.split('/')[-1].split('.')[1]}'}
    return file_info

def url_breed(headers, breed):
    url = f'https://dog.ceo/api/breed/{breed}/images/random'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Ошибка API dog.ceo: {response.json().get('message', 'Неизвестная ошибка')}')
    print(f'\tИзображение {breed} найдено...')
    image_url = response.json()['message']
    filename = f'{breed}_{image_url.split('/')[-1].split('.')[0]}'
    file_info = upload_image(headers, image_url, filename, breed)
    return [file_info]

def url_sub_breed(headers, breed, sub_breeds):
    uploaded_files = []
    for sub_breed in sub_breeds:
        url = f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random'
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f'Ошибка API dog.ceo: {response.json().get('message', 'Неизвестная ошибка')}')
        print(f'\tИзображение {sub_breed}-{breed} найдено...')
        image_url = response.json()['message']
        filename = f'{sub_breed}_{breed}_{image_url.split('/')[-1].split('.')[0]}'
        file_info = upload_image(headers, image_url, filename, breed)
        uploaded_files.append(file_info)
    return uploaded_files

def save_info(uploaded_files):
    try:
        with open('upload_files.json', 'w', encoding='utf-8') as f:
            json.dump(uploaded_files, f)
        print('\tФайл upload_files.json успешно создан.')
    except Exception as e:
        print(f'\tОшибка записи в JSON: {e}')

def main():
    """Основная функция программы."""
    # Получение и проверка токена
    headers = check_yandex_token()

    # Получение списка пород
    breeds = get_breeds_dict()

    # Получение породы от пользователя
    breed = get_user_input_breeds(breeds)

    print('Процесс:')
    # Создание папки на Яндекс Диске
    create_yandex_folder(breed, headers)

    # Загрузка изображений в зависимости от наличия подпород
    has_sub_breeds = breeds[breed] != []
    if has_sub_breeds:
        uploaded_files = url_sub_breed(headers, breed, breeds[breed])
    else:
        uploaded_files = url_breed(headers, breed)

    # Сохранение информации о загруженных файлах
    if uploaded_files:
        save_info(uploaded_files)
    else:
        print('\tНе удалось загрузить ни одного изображения.')

    print('\nГотово! Проверьте Яндекс.Диск и файл upload_files.json.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nПрограмма прервана пользователем.')
    except Exception as ex:
        print(f'Произошла ошибка: {ex}')