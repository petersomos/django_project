from django.urls import path
from .views import quiz_view, call_tensorflow_api
from .views import translate_text_view

urlpatterns = [
    path('quiz/', quiz_view, name='quiz'),
    path('call-tensorflow/', call_tensorflow_api, name='call_tensorflow_api'),
    path('translate/', translate_text_view, name='translate_text'),
]