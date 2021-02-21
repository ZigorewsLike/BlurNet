import os
from sys import argv
import requests
from zipfile import ZipFile


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)
    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)
    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def save_response_content(response, destination):
    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)


_mode = 1  # 0 - None; 1 - first time; 2 - download model

try:
    param1 = argv[1]
    if param1 == "-f":
        _mode = 1
    elif param1 == "-d":
        _mode = 2
except IndexError:
    print('-f')

dir_list = ['photos', 'blur_del/static/media', 'blur_del/static/media/ann_blr', 'blur_del/static/media/blur',
            'api_drf/saved_model_blur', 'api_drf/saved_model_car', 'photos/local', 'download']
# wget_list = {'1pEhHEqoTQ-DNWq3_haUKpFxcQbwi7Fa3': 'saved_model_blur.zip',
# '1-HcVDTOtLh85va4No4raKzz0buSsgrL_': 'saved_model_car.zip'}
wget_list = {'11BAlo0WGYfzWeVRgdmm5WH574octhTD6': 'saved_model_jpeg.zip'}

if _mode == 1:
    for folder in dir_list:
        try:
            os.mkdir(folder)
            print('OK')
        except FileExistsError:
            print('ok')
elif _mode == 2:
    c = 0
    print(c, '%')
    for wget_item in wget_list:
        download_file_from_google_drive(wget_item, 'download/' + wget_list[wget_item])
        with ZipFile('download/' + wget_list[wget_item], 'r') as zip_obj:
             zip_obj.extractall('api_drf/' + wget_list[wget_item][:-4])
