from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .form import UploadFileForm
from django.shortcuts import redirect
from django.http import HttpResponse
import os

from PIL import Image


def render_main_page(request):
    return render(request, 'index.html')


def render_blur_net_page(request):
    return render(request, 'blurNet.html')


def render_car_fill_page(request):
    return render(request, 'carRealFill.html')


def blurImage(request, filename):
    # print(filename)
    print('PUTTT - ', os.getcwd())
    try:
        with open('blur_del/static/media/blur/' + filename, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/png")
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
    except IOError:
        red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        response = HttpResponse(content_type="image/jpeg")

        red.save(response, "JPEG")
        return response

    # with open('blur_del/static/media/blur/' + filename, 'rb') as f:
    #     response = HttpResponse(f.read(), content_type="multipart/form-data")
    #     response['Content-Disposition'] = 'inline; filename=' + os.path.basename(filename)
    # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def annBlurImage(request, filename):
    print('PUTTT - ', os.getcwd())
    try:
        with open('blur_del/static/media/ann_blr/' + filename, "rb") as f:
            response = HttpResponse(f.read(), content_type="image/png")
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response
    except IOError:
        red = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        response = HttpResponse(content_type="image/jpeg")

        red.save(response, "JPEG")
        return response


