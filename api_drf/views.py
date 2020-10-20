from rest_framework import viewsets
from blur_del.models import File
from .serializers import FileSerializer
from rest_framework.parsers import MultiPartParser, FormParser

from PIL import Image, ImageFilter

# Вся херя со всей хернёй
import tensorflow as tf
import os
import time
from matplotlib import pyplot as plt
# from IPython import display
OUTPUT_CHANNELS = 3
LAMBDA = 100


def downsample(filters, size, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = tf.keras.Sequential()
    result.add(
        tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                               kernel_initializer=initializer, use_bias=False))
    if apply_batchnorm:
        result.add(tf.keras.layers.BatchNormalization())
    result.add(tf.keras.layers.LeakyReLU())
    return result


def upsample(filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)
    result = tf.keras.Sequential()
    result.add(
        tf.keras.layers.Conv2DTranspose(filters, size, strides=2,
                                        padding='same',
                                        kernel_initializer=initializer,
                                        use_bias=False))
    result.add(tf.keras.layers.BatchNormalization())
    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))
    result.add(tf.keras.layers.ReLU())
    return result


def Generator():
    inputs = tf.keras.layers.Input(shape=[512, 512, 3])
    down_stack = [
        downsample(64, 4, apply_batchnorm=False),  # (bs, 128, 128, 64)
        downsample(128, 4),  # (bs, 64, 64, 128)
        downsample(256, 4),  # (bs, 32, 32, 256)
        downsample(512, 4),  # (bs, 16, 16, 512)
        downsample(1024, 4),  # (bs, 8, 8, 512)
        downsample(1024, 4),  # (bs, 4, 4, 512)
        downsample(1024, 4),  # (bs, 2, 2, 512)
        downsample(1024, 4),  # (bs, 1, 1, 512)
        downsample(1024, 4),  # (bs, 1, 1, 512)
    ]
    up_stack = [
        upsample(1024, 4, apply_dropout=True),  # (bs, 2, 2, 1024)
        upsample(1024, 4, apply_dropout=True),  # (bs, 2, 2, 1024)
        upsample(1024, 4, apply_dropout=True),  # (bs, 4, 4, 1024)
        upsample(1024, 4),  # (bs, 8, 8, 1024)
        upsample(512, 4),  # (bs, 16, 16, 1024)
        upsample(256, 4),  # (bs, 32, 32, 512)
        upsample(128, 4),  # (bs, 64, 64, 256)
        upsample(64, 4),  # (bs, 128, 128, 128)
    ]
    initializer = tf.random_normal_initializer(0., 0.02)
    last = tf.keras.layers.Conv2DTranspose(OUTPUT_CHANNELS, 4,
                                           strides=2,
                                           padding='same',
                                           kernel_initializer=initializer,
                                           activation='tanh')  # (bs, 256, 256, 3)
    x = inputs
    skips = []
    for down in down_stack:
        x = down(x)
        skips.append(x)
    skips = reversed(skips[:-1])
    for up, skip in zip(up_stack, skips):
        x = up(x)
        x = tf.keras.layers.Concatenate()([x, skip])
    x = last(x)
    return tf.keras.Model(inputs=inputs, outputs=x)


def imagBlur(file, blur, key, img):
    img = Image.open(img)
    width, height = img.size
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


def imagBlurAnn(file, title, key, img):
    img = Image.open(img)
    width, height = img.size
    if width >= height:
        ratio = (256 / float(img.size[0]))
        height = int((float(img.size[1]) * float(ratio)))
        img = img.resize((256, height))
    else:
        ratio = (256 / float(img.size[1]))
        width = int((float(img.size[0]) * float(ratio)))
        img = img.resize((width, 256))

    generator = Generator()

    checkpoint_dir = './training_checkpoints'
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt")
    checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                     discriminator_optimizer=discriminator_optimizer,
                                     generator=generator,
                                     discriminator=discriminator)

    img.save('./blur_del/static/media/blur/' + key + str(file.img)[7:])
    # img.save(img_io, format='JPEG', quality=100)
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
