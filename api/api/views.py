from django.shortcuts import render
import requests
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import json
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .forms import URLForm
import html
from rest_framework.views import APIView
from rest_framework.response import Response

BASE_URL = 'https://www.newsrain.in/petrol-diesel-prices'


def getNationalData():
    url = BASE_URL
    try:
        response = requests.get(url)
    except:
        return 'unable to reach server'
    soup = BeautifulSoup(response.content, 'html.parser')
    result = soup.find_all('article')

    x = []
    for i in result:
        temp = i.find('div', class_='col m4 s4 fuel-title center center-align')
        stateData = temp.text
        city = temp.find('small', class_='center').text
        city = ' '.join(city.split())
        state = ' '.join(stateData.split())
        state = state.replace(city, '')
        t = {
            'state': state,
            'city': city
        }
        fuel = i.find_all('div', class_='col m6')
        for k, j in enumerate(fuel):
            fuel_type = j.find('h3', class_='block_title').text
            fuel_type = ''.join(fuel_type.split())
            price = ''.join((j.find('span', class_='price_tag').text).split())
            price_change = j.find('div', class_='price-change')
            z = str(price_change.find('i'))
            price_change = ''.join((price_change.text).split())
            change = z.split(' ')[3][9:]
            t[fuel_type] = {'price': price,
                'priceChange': price_change, 'change': change}
        x.append(t)
    res = json.dumps(x)
    return res


def getStateData(state):
    url = BASE_URL+'/'+state
    try:
        response = requests.get(url)
    except:
        return "unable to reach server"
    soup = BeautifulSoup(response.content, 'html.parser')
    district = soup.find_all('div', class_='fuel-wrapper')
    res = []
    for i in district:
        temp = {}
        distt = i.find(
            'h2', class_="col m4 s4 fuel-title-dist center center-align").text
        temp['district'] = ' '.join(distt.split())
        fuel = i.find_all('div', class_="col m6")
        for j in fuel:
            fuel_type = j.find('h3', class_='block_title').text
            fuel_type = ''.join(fuel_type.split())
            price = ''.join(j.find('span', class_='price_tag').text).split()
            priceChange = j.find('div', class_='price-change')
            z = str(priceChange.find('i'))
            change = z.split(' ')[3][9:]
            priceChange = j.find(
                'div', class_='price-change').find('span').text.split()
            temp[fuel_type] = {'price': price[0],
                'priceChange': priceChange[0], 'change': change}
        res.append(temp)
    res = json.dumps(res)
    return res


def index(request):
    data = getNationalData()
    return HttpResponse(data)


def landing(request):
    context = request.META.get('HTTP_HOST')
    form = URLForm
    return render(request, 'index.html', {'context': context, 'form': form})


def statewise(request, state):
    data = getStateData(state)
    return HttpResponse(data)


def zee5(id):
    token = requests.get("https://useraction.zee5.com/tokennd/").text
    token=json.loads(token)
    token=token['video_token']
    url = ("https://gwapi.zee5.com/content/details/{}?translation=en&country=IN&version=2").format(id)
    result= requests.get(url, headers={
        "x-access-token": token,
        'Content-Type': 'application/json'
    })
    if result.status_code==200:
        result=result.text
    else:
        res_data={
            "error":"Bad Response"
        }
        res_data=json.dumps(res_data)
        return res_data
    try:
        result=json.loads(result)
        hls=result['hls'][0]
        hls=hls.replace('drm','hls',1)
        hls=('https://zee5vodnd.akamaized.net{}{}').format(hls,token)
        response={
            "id":1,
            "title":result['title'],
            "thumbnail":result['image_url'],
            "video_url":hls,
            "description":result['description'],
            "genres":result['genres'],
            "age_rating":result['age_rating'],
            "plateform":"zee5"
        }
        # response=json.dumps(response)
        return response
    except:
        return result

def voot(id):
    url=("https://wapi.voot.com/ws/ott/getMediaInfo.json?platform=Web&pId=2&mediaId={}").format(id)
    result=requests.get(url)
    if result.status_code==200:
        result=result.text
        result=json.loads(result)
        res_data={
            "id":1,
            "title":result['assets']['MediaName'],
            "description":result['assets']['Metas'][1]['Value'],
            "video_url":result['assets']['Files'][3]['URL'],
            "plateform":"voot"
        }
        # res_data=json.dumps(res_data)
        return res_data
    else:
        res_data={
            "error":"Bad Response"
        }
        # res_data=json.dumps(res_data)
        return res_data

def hungama(id):
    url="https://www.hungama.com/index.php?c=common&m=get_video_mdn_url"
    result=requests.post(url,
    headers={
        "accept":"*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest"
    },
    data= ("content_id={}&action=movie&cnt_type=movie&movie_rights=TVOD-Premium&lang=english").format(id)
    )
    if result.status_code==200:
        result=json.loads(result.text)
        video_url=result['stream_url']
        q=video_url.split(',')
        BASE_URL=q[0]
        token=q[-1]
        res_data={
            "q_auto":video_url,
            "q_verylow":BASE_URL+q[1]+token,
            "q_low":BASE_URL+q[2]+token,
            "q_medium":BASE_URL+q[3]+token,
            "q_high":BASE_URL+q[4]+token,
            "q_fullhd":BASE_URL+q[5]+token,
            "subtitle":result['sub_title']
        }
        # res_data=json.dumps(res_data)
        return res_data
    else:
        return '{"error":"please enter valid url"}'

class Services(APIView):
    def get(self, request,ott):
        return Response({"url":"please enter url"})
    def post(self, request,ott):
        res=self.getdata(request.data.get('url'),ott)
        return Response(res)

    def getdata(self,url,ott):
        try:
            url = url.split('/')
            id = url[-1]
            if ott=="zee5":
                return zee5(id)
            if ott=="voot":
                return voot(id)
            if ott=="hungama":
                id=url[-2]
                return hungama(id)
        except:
            return {"details":"server error please try again."}

def worker(request,ott):
    if request.method=='POST':
        try:
            form = URLForm(request.POST)
            if form.is_valid():
                url = form.data.get('URL')
                url = url.split('/')
                id = url[-1]
                if ott=="zee5":
                    return HttpResponse(zee5(id))
                if ott=="voot":
                    return HttpResponse(voot(id))
                if ott=="hungama":
                    id=url[-2]
                    return HttpResponse(hungama(id))
        except:
            # print(request.data)
            return HttpResponse("request")




def searchMovies(request, plateform):
    url='https://www.hungama.com/'
    keyword=request.GET.get('keyword')
    # keyword=plateform
    params={
        'c':'search',
        'm':'getGroupedSearchByText',
        'keyword':keyword,
        'type':'movie'
    }
    
    response=requests.get(url,headers={
        "accept":"*/*",
        "x-requested-with": "XMLHttpRequest"
    },params=params)
    soup = BeautifulSoup(response.content, 'html.parser')
    res=soup.find_all('a')
    res=res[1:]
    img=soup.find_all('img')
    name=soup.find_all('span')[1:]
    data=[]
    for x in range(len(res)):
        i=img[x].get('src')
        i=i[:-10]+'190x273.jpg'
        temp={
        "id":x+1,
        "video_url":res[x].get('href'),
        "thumbnail":i,
        "title":name[x].get_text(),
        "plateform":"hungama"
        }
        
        data.append(temp)
    # print(data)
    return HttpResponse(json.dumps(data))
