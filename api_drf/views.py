from rest_framework import viewsets
from blur_del.models import File
from .serializers import FileSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from PIL import Image, ImageFilter

import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
import os
import time
from matplotlib import pyplot as plt

# from IPython import display
IMAGE_SHAPE = 512


def calcSize(width, height):
    r = width/height
    if width > height:
        return IMAGE_SHAPE, int(IMAGE_SHAPE/r)
    return int(IMAGE_SHAPE*r), IMAGE_SHAPE


def load_img(image_file):
    image = tf.io.read_file(image_file)
    image = tf.image.decode_jpeg(image)

    input_image = tf.cast(image, tf.float32)
    input_image = tf.image.resize(input_image, [IMAGE_SHAPE, IMAGE_SHAPE], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    input_image = (input_image / 127.5) - 1
    input_image = tf.reshape(input_image, [1, IMAGE_SHAPE, IMAGE_SHAPE, 3])
    print(input_image)
    return input_image


def imagBlur(file, blur, key, img):
    img = Image.open(img)
    width, height = img.size
    os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), str(file.img)))
    if width >= height:
        ratio = (256 / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((256, height))
    else:
        ratio = (256 / float(img.size[1]))
        width = int((float(img.size[0]) * float(ratio)))
        img = img.resize((width, 256))
    img = img.filter(ImageFilter.GaussianBlur(radius=int(blur) / 100))
    img.save('./blur_del/static/media/blur/' + key + str(file.img)[7:])
    # img.save(img_io, format='JPEG', quality=100)
    qqueryset = File.objects.filter(keysession=key, blurInt=int(blur))
    qqueryset.update(outputPath='/static/media/blur/' + key + str(file.img)[7:])


def imagBlurAnn(file, title, key, img_path):
    img = Image.open(img_path)
    img = img.resize(calcSize(img.size[0], img.size[1]))
    n_img = Image.new(mode="RGB", size=(IMAGE_SHAPE, IMAGE_SHAPE))
    shift_x, shift_y = int((IMAGE_SHAPE - img.size[0])/2), int((IMAGE_SHAPE - img.size[1])/2)
    n_img.paste(img, (shift_x, shift_y, img.size[0]+shift_x, img.size[1]+shift_y))
    n_img.save('photos/local/img.jpg')
    print(file.img)
    os.remove(os.path.join(os.path.dirname(os.path.dirname(__file__)), str(file.img)))

    print('Load model')
    if title == "brnann_ccr_nf_2288667.jpg":
        checkpoint_dir = 'api_drf/saved_model_car/'
    else:
        checkpoint_dir = 'api_drf/saved_model_blur/'
    with open(os.path.join('api_drf/', 'model.name'), 'r') as f:
        checkpoint_dir += f.readline()
        print("DIR  ===== ", checkpoint_dir)
    print('Path model exist -', os.path.exists(checkpoint_dir), os.getcwd())
    model = load_model(checkpoint_dir, compile=False)
    print('Model predict')
    image = load_img('photos/local/img.jpg')
    prediction = model(image, training=True)
    print(prediction)
    print('Model end predict')
    n_predict = (prediction.numpy()[0] + 1) * 127.5
    n_predict = n_predict.astype(np.uint8)
    print(n_predict)
    img = Image.fromarray(n_predict)
    img = img.crop((shift_x, shift_y, IMAGE_SHAPE-shift_x, IMAGE_SHAPE-shift_y))
    img.save('./blur_del/static/media/ann_blr/' + key + str(file.img)[7:], quality=100)

    qqueryset = File.objects.filter(keysession=key, title=title)
    qqueryset.update(outputPath='/static/media/ann_blr/' + key + str(file.img)[7:])


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        file = serializer.save(img=self.request.data.get('img'))
        blur = self.request.data['blurInt']
        key = self.request.data['keysession']

        print(str(file.img)[7:])
        imagBlur(file, blur, key, self.request.data['img'])


class BlurViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        file = serializer.save(img=self.request.data.get('img'))
        key = self.request.data['keysession']
        title = self.request.data['title']

        print(str(file.img)[7:])
        imagBlurAnn(file, title, key, self.request.data['img'])
