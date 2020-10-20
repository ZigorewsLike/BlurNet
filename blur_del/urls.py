from django.urls import path
from . import views

urlpatterns = [
    path('', views.render_main_page),
    path('ann_blurNet', views.render_blur_net_page),
    path('blur<filename>/', views.blurImage),
]