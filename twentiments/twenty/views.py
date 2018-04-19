from django.shortcuts import render
from django.http import HttpResponse
from twenty.app import getInputFromUser
import json

def index(request):
	return render(request, 'index.html', {
        'foo': 'bar',
    })

def search(request, searchQuery):
	# importlib.import_module('app')
	response =getInputFromUser(searchQuery)
	return HttpResponse(response)