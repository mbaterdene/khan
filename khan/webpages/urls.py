from django.urls import path
from . import views

urlpatterns = [
    path('tamgiingazar', views.infoTamga, name = 'infoTamga'),
    path('shuugch', views.infoShuugch, name = 'infoShuugch'),
    path('contact', views.contactIngo, name = 'contactIngo'),
]