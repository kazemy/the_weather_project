import requests
from django.shortcuts import render, redirect
from .models import City
from .forms import CityForm

def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=6933b0dcc33023e590d580db7b6cef0f'

    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        #instantiate form from CityForm ... aka ModelForm
        form = CityForm(request.POST)
        
        #check if the form is valid
        if form.is_valid():
            #is_valid will create cleaned_data dictionary containitn form fields to be accessed
            #since the data is clean then get the city which is enterd by the user
            new_city = form.cleaned_data['name']
            #now query the database to see if this city is already there
            existing_city_count = City.objects.filter(name=new_city).count()
            
            #if count is 0 
            if existing_city_count == 0:
                #check if the city is a valid city by examining the response code
                #response code should be 200; otherwise city isn't valid
                response = requests.get(url.format(new_city)).json()
                if response['cod'] ==200:
                    form.save()
                else:
                    err_msg = 'City is invalid'
            else:
                err_msg = 'City already exists'
        
        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'City added successfully'
            message_class = 'is-success'

    form = CityForm()

    cities = City.objects.all()
    weather_data = []

    for city in cities:
        response = requests.get(url.format(city)).json()
        city_weather = {
        'city': city.name,
        'temperature':response['main']['temp'],
        'description':response['weather'][0]['description'],
        'icon':response['weather'][0]['icon']
        }
    
        weather_data.append(city_weather)

    context = {
        'weather_data': weather_data, 
        'form':form, 
        'message': message, 
        'message_class':message_class
    }
    return render (request,'weather/weather.html', context)

def delete_city(request, city_name):
    City.objects.get(name=city_name).delete()
    return redirect('home')