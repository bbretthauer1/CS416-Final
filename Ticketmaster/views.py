from datetime import datetime

from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse

from .forms import UserForm, CommentForm
from typing import Any

from django.shortcuts import render, redirect
import requests

from .models import Likes, Events, Comments


# Create your views here.
def createaccount(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('search')
    context = {'form': form}
    return render(request, 'create-account.html', context)

def login_view(request):
    if request.method == 'POST':
        # Plug the request.post in AuthenticationForm
        form = AuthenticationForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            # get the user info from the form data and login the user
            user = form.get_user()
            login(request, user)
            # redirect the user to index page
            return redirect('search')
    else:
        # Create an empty instance of Django's AuthenticationForm to generate the necessary html on the template.
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
events = []
def search(request):
    if request.method == "POST":
        events.clear()
        genre = request.POST["genre"]
        city = request.POST["city"]
        loggedIn = request.user.is_active
        if not genre or not city:
            return redirect('search')
        json = query(genre.lower(), city.lower())
        if json is None:
            return redirect('search')
        elif json['page']['totalElements']>0:
            results=json['_embedded']['events']
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            days = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
            for result in results:
                print(result['name'])
                actName = result['name']
                location = result['_embedded']['venues'][0]['name']
                address = result['_embedded']['venues'][0]['address']['line1']
                city = result['_embedded']['venues'][0]['city']['name']
                stateCode = result['_embedded']['venues'][0]['state']['stateCode']
                dateTime = ""
                date=0
                day=''
                month=''
                year=''
                hour=0
                minute=''
                hourTwelve=0
                timeString=''
                act = {
                    "actName": actName,
                    "location": location,
                    "address": address,
                    "city": city,
                    "state": stateCode,
                    "photo": '',
                    "dateString": '',
                    "timeString": '',
                    "tix": '',
                    'eventId':result['id'],
                    'likes':0,
                    'liked':False
                }
                if result['name']!="2026 Premium Season Tickets Wait List":
                    if not result['dates']['start']['dateTBA'] and not result['dates']['start']['dateTBD']:
                        #print('valid date')
                        dateTime = result['dates']['start']['localDate']
                        dateObject = datetime.strptime(dateTime[:10], "%Y-%m-%d")
                        day = days[dateObject.weekday()]
                        month = months[int(dateTime[5:7]) - 1]
                        date = int(dateTime[8:10])
                        act['dateString'] = "{day} {month} {date}, {year}".format(day=days[dateObject.weekday()],
                                                                                  month=months[int(dateTime[5:7]) - 1],
                                                                                  date=int(dateTime[8:10]),
                                                                                  year=dateTime[:4])
                        print(act['dateString'])
                    elif result['dates']['start']['dateTBD']:
                        act['dateString'] = 'Date TBD'
                    elif result['dates']['start']['dateTBA']:
                        act['dateString'] = 'Date TBA'
                    if not result['dates']['start']['timeTBA'] and not result['dates']['start']['noSpecificTime']:
                        #print('false')
                        localTime = result['dates']['start']['localTime']
                        hour = hour + int(localTime[:2])
                        minute = minute + localTime[3:5]
                        hourTwelve += hour % 12
                        if hourTwelve == 0:
                            hourTwelve += 12
                        ampm = ""
                        if hour / 12 >= 1:
                            ampm += "PM"
                        else:
                            ampm += "AM"
                        timeString = timeString + "{h}:{m} {a}".format(h=hourTwelve, m=minute, a=ampm)
                        act['timeString'] = timeString
                    else:
                        timeString = 'Time TBA'
                        act['timeString'] = timeString
                act['photo'] = result['images'][0]['url']
                act['tix'] = result['url']
                events.append(act)
                if Events.objects.filter(eventId=act['eventId']).exists():
                    event = Events.objects.get(eventId=act['eventId'])
                    if Likes.objects.filter(event=event).exists():
                        likes = Likes.objects.filter(event=event).count()
                        print("Likes "+str(likes))
                        act['likes']=likes
                    if loggedIn:
                        liked = Likes.objects.filter(event=event, user=request.user).exists()
                        if liked:
                            act['liked'] = True

            context={"results":events, "loggedIn":loggedIn}
            print(events)
            return render(request, "search.html", context)

    return render(request, 'search.html')

def query(genre, city):
    try:
        url="https://app.ticketmaster.com/discovery/v2/events"
        params = {
            "classificationName": genre.lower(),
            "city": city.lower(),
            "radius":50,
            "unit":"miles",
            "sort":"date,name,asc",
            "apikey":"e926GReM1L7jU4CRpaAjQDfT7VK2wKqj"
        }
        events = requests.get(url, params)
        data = events.json()
        return data
    except requests.exceptions.RequestException as e:
        print(e)
        return None

def query_single(eventId):
    try:
        url="https://app.ticketmaster.com/discovery/v2/events"
        params = {
            "id":eventId,
            "apikey":"e926GReM1L7jU4CRpaAjQDfT7VK2wKqj"
        }
        events = requests.get(url, params)
        data = events.json()
        return data
    except requests.exceptions.RequestException as e:
        print(e)
        return None

@login_required(login_url='/login/')
def likeEvent(request):
    event_id = request.POST['event_id']
    actName = request.POST['actName']
    location = request.POST['location']
    address = request.POST['address']
    city = request.POST['city']
    state = request.POST['state']
    photo = request.POST['photo']
    link = request.POST['link']
    dateString = request.POST['dateString']
    timeString = request.POST['timeString']
    user = request.user
    if not Events.objects.filter(eventId=event_id).exists():
        Events.objects.create(eventId=event_id, actName=actName, location=location,
                              address=address, city=city, stateCode=state, photo=photo,
                              link=link, dateString=dateString, timeString=timeString)
    event = Events.objects.get(eventId=event_id)
    if Likes.objects.filter(event=event, user=user).exists():
        Likes.objects.get(event=event, user=user).delete()
        return JsonResponse({'liked': False, 'message': 'Successfully unliked'})
    else:
    #print("Liking Event " + request.POST['event_id'])
        if request.method == "POST":
            Likes.objects.create(user=user,event=event)
            return JsonResponse({'liked':True, 'message':'Successfully liked'})
    return JsonResponse({'liked':False, 'message':'Something went wrong.'})

def createEvent(event_id):
    if not Events.objects.filter(eventId=event_id).exists():
        json = query_single(event_id)
        if json is None:
            return False
        elif json['page']['totalElements']>0:
            result=json['_embedded']['events'][0]
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            days = ["Mon", "Tue", "Wed", "Thur", "Fri", "Sat", "Sun"]
            #print(result['name'])
            actName = result['name']
            location = result['_embedded']['venues'][0]['name']
            address = result['_embedded']['venues'][0]['address']['line1']
            city = result['_embedded']['venues'][0]['city']['name']
            stateCode = result['_embedded']['venues'][0]['state']['stateCode']
            hour = 0
            minute = ''
            hourTwelve = 0
            timeString = ''
            act = {
                'dateString':'',
                'timeString':'',
            }
            if result['name'] != "2026 Premium Season Tickets Wait List":
                if not result['dates']['start']['dateTBA'] and not result['dates']['start']['dateTBD']:
                    # print('valid date')
                    dateTime = result['dates']['start']['localDate']
                    dateObject = datetime.strptime(dateTime[:10], "%Y-%m-%d")
                    act['dateString'] = "{day} {month} {date}, {year}".format(day=days[dateObject.weekday()],
                                                                              month=months[int(dateTime[5:7]) - 1],
                                                                              date=int(dateTime[8:10]),
                                                                              year=dateTime[:4])
                    print(act['dateString'])
                elif result['dates']['start']['dateTBD']:
                    act['dateString'] = 'Date TBD'
                elif result['dates']['start']['dateTBA']:
                    act['dateString'] = 'Date TBA'
                if not result['dates']['start']['timeTBA']:
                    # print('false')
                    localTime = result['dates']['start']['localTime']
                    hour = hour + int(localTime[:2])
                    minute = minute + localTime[3:5]
                    hourTwelve += hour % 12
                    if hourTwelve == 0:
                        hourTwelve += 12
                    ampm = ""
                    if hour / 12 >= 1:
                        ampm += "PM"
                    else:
                        ampm += "AM"
                    timeString = timeString + "{h}:{m} {a}".format(h=hourTwelve, m=minute, a=ampm)
                    act['timeString'] = timeString
                else:
                    timeString = 'Time TBA'
                    act['timeString'] = timeString
            act['photo'] = result['images'][0]['url']
            act['tix'] = result['url']
            Events.objects.create(eventId=event_id,actName=actName,location=location,
                                  address=address,city=city,stateCode=stateCode,
                                  photo=result['images'][0]['url'], link=result['url'],
                                  dateString=act['dateString'], timeString=act['timeString'])
            return True
        else:
            return False #NEED THIS
    return False


def event_view(request, event_id):
    if not Events.objects.filter(eventId=event_id).exists():
        worked = createEvent(event_id)
        if not worked:
            return render(request, 'event-dne.html', {'event_id': event_id})
    event = Events.objects.get(eventId=event_id)
    comments = Comments.objects.filter(event=event)
    context = {"event":event, 'comments':comments, 'user':request.user, 'event_id':event_id}
    return render(request, 'event-page.html', context)


@login_required(login_url='/login/')
def comment_view(request, event_id):
    if Comments.objects.filter(event_id=event_id, user_id=request.user.id).exists():
        return redirect('event_view', event_id)
    if request.method == "POST":
        if not Events.objects.filter(eventId=event_id).exists():
            worked = createEvent(event_id)
            if not worked:
                return render(request, 'event-dne.html', {'event_id': event_id})
        event = Events.objects.get(eventId=event_id)
        form = CommentForm(request.POST, initial={'event':event, 'user':request.user, 'user_id':request.user.id})
        form.user = request.user
        form.user_id = request.user.id
        if form.is_valid():
            form.save()
            return redirect('event_view', event_id)
        else:
            context = {"form":form, "event_id":event_id}
            return render(request, 'comment-form.html', context)
    if not Events.objects.filter(eventId=event_id).exists():
        createEvent(event_id)
    event = Events.objects.get(eventId=event_id)
    form = CommentForm(initial={'event':event, 'user':request.user, 'user_id':request.user.id})
    context = {"form":form, 'event_id':event_id}
    return render(request, 'comment-form.html', context)

@login_required(login_url='/login/')
def comment_edit(request, event_id):
    comment = Comments.objects.get(event_id=event_id, user_id=request.user.id)
    form = CommentForm(request.POST or None, instance=comment)
    if request.method == "POST":
        print("method is post")
        if form.is_valid():
            print("form is valid")
            form.save()
            return redirect('event_view', event_id)
    form = CommentForm(instance=comment)
    context = {"form":form, 'comment':comment, 'event_id':event_id}
    return render(request, 'comment-edit.html', context)

@login_required(login_url='/login/')
def comment_delete(request, event_id):
    comment = Comments.objects.get(event_id=event_id, user_id=request.user.id)
    if request.method == "POST":
        comment.delete()
        return redirect('event_view', event_id)
    context = {"comment":comment, 'event_id':event_id}
    return render(request, 'comment-delete.html', context)

def user_view(request, user_id):
    if not User.objects.filter(id=user_id).exists():
        context = {'user_id': user_id}
        return render(request, 'user-dne.html', context)
    userRaw = User.objects.get(id=user_id)
    user = {
        'id':str(userRaw.id),
        'username':userRaw.username,
    }
    commented='no'
    liked='no'
    comments=[]
    likes=[]
    if Comments.objects.filter(user_id=user_id).exists():
        commentsRaw = Comments.objects.filter(user_id=user_id)
        for c in commentsRaw:
            comment = {
                'actName':c.event.actName,
                'location':c.event.location,
                'eventId':str(c.event.eventId),
                'comment':c.comment,
            }
            comments.append(comment)
        commented = 'yes'
    if Likes.objects.filter(user_id=user_id).exists():
        likesRaw = Likes.objects.filter(user_id=user_id)
        for l in likesRaw:
            like = {
                'actName':l.event.actName,
                'location':l.event.location,
                'eventId':str(l.event.eventId),
                'photo':l.event.photo,
            }
            likes.append(like)
        liked = 'yes'
    context = {'user_query':user, 'comments':comments, 'commented':commented, 'likes':likes, 'liked':liked}
    return render(request, 'user-view.html', context)

def event_dne(request, event_id):
    context = {'event_id':event_id}
    return render(request, 'event-dne.html', context)
def user_dne(request, user_id):
    context = {'user_id':user_id}
    return render(request, 'user-dne.html', context)

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('search')

def get_lightdark_cookie(request):
    value = request.COOKIES.get('light_dark', 'light')
    return JsonResponse({'mode':value})

def set_lightdark_cookie(request):
    cookie_value = request.COOKIES.get('light_dark', 'light')
    request.method = "GET"
    response = redirect(request.POST.get('next', ''))
    if cookie_value == 'light':
        response.set_cookie('light_dark', 'dark')
        return response
    else:
        response.set_cookie('light_dark', 'light')
        return response

