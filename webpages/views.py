from django.shortcuts import render
from .models import defualtInfo
# Create your views here.
def infoTamga(request):
    infoTamgaData = defualtInfo.objects.filter(tag = 1)
    return render(request, 'defualt.html', {'content1': infoTamgaData})

def infoShuugch(request):
    infoShuugchaData = defualtInfo.objects.filter(tag = 0)
    return render(request, 'defualt.html', {'content1': infoShuugchaData})

def contactIngo(request): 
      
    # render function takes argument  - request 
    # and return HTML as response 
    return render(request, "contact.html") 