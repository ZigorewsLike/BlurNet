import os
from sys import argv

_mode = 1  # 0 - None; 1 - first time; 2 - download model

try:
    param1 = argv[1]
    if param1 == "-f":
        _mode = 1
except IndexError:
    print('-f')

dir_list = ['photos', 'blur_del/static/media', 'blur_del/static/media/ann_blr', 'blur_del/static/media/blur',
            'api_drf/saved_model_blur', 'api_drf/saved_model_car', 'photos/local']

if _mode == 1:
    for folder in dir_list:
        try:
            os.mkdir(folder)
            print('OK')
        except FileExistsError:
            print('ok')
