from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
import requests, json
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import HoverTool, NumeralTickFormatter, Range1d, LinearAxis, Legend, Span, BasicTickFormatter
from .forms import CoinForm, form2, form3, bookmark
import datetime
from dal import autocomplete
from django.views import View
from django.views.generic import ListView
from math import floor, log10
import numpy as np
import pandas as pd
from prophet import Prophet
from bokeh.models import ColumnDataSource
from dateutil.relativedelta import relativedelta
import time as now
import random
from .models import favouritePages
import configparser

def bettertime(n):
    return datetime.datetime.fromtimestamp(n[0]//1000)
def betterprice(n):
    return float(n[1])
def nn(n):
    if n <= 0:
        return 0
    return n

def color(val):
    if val == "#NA":
        return "black"
    if val < 0:
        return "red"
    elif val == 0:
        return "gray"
    else:
        return "green"
def r(x):
    if x == None:
        return "#NA"
    return round(x, -int(floor(log10(abs(x))))+5)
def r2(x):
    return round(x, -int(floor(log10(abs(x))))+3)

# Create your views here.
def index(request, c):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api1 = config.get('Database', 'api1')
    # favouritePages.objects.all().delete()
    url = "https://pro-api.coingecko.com/api/v3/coins/markets?vs_currency="+c+"&per_page=40&page=1&price_change_percentage=1h%2C24h%2C7d%2C30d%2C1y&x_cg_pro_api_key="+api1
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    a = response.json()
    currencies = {"usd": "$",
                "jpy": "¥",
                "gbp": "£"}
    cu = ["usd", "jpy", "gbp"]
    cu.remove(c)
    for coin in a:
        if coin["current_price"] <= 1:
            coin["current_price"] =r2(float(coin["current_price"]))
        elif coin["current_price"]>=1000:
            coin["current_price"] = f"{coin["current_price"]:,}"
        coin["market_cap"] = f"{coin["market_cap"]:,}"
        coin["price_change_percentage_1h_in_currency"], coin["price_change_percentage_7d_in_currency"], coin["price_change_percentage_30d_in_currency"], coin["price_change_percentage_1y_in_currency"] = r(coin["price_change_percentage_1h_in_currency"]),r(coin["price_change_percentage_7d_in_currency"]), r(coin["price_change_percentage_30d_in_currency"]), r(coin["price_change_percentage_1y_in_currency"])
        coin["color"] = color(coin["price_change_percentage_24h"])
        coin["color2"] = color(coin["market_cap_change_percentage_24h"])
        coin["color3"] = color(coin["price_change_percentage_1h_in_currency"])
        coin["color4"] = color(coin["price_change_percentage_7d_in_currency"])
        coin["color5"] = color(coin["price_change_percentage_30d_in_currency"])
        coin["color6"] = color(coin["price_change_percentage_1y_in_currency"])
        
    ranking = {"table": a,
               "c1": currencies[c]+" "+ c.upper(),
             "c2": currencies[cu[0]]+" "+cu[0].upper(),
             "c3": currencies[cu[1]]+" "+cu[1].upper(),
             "cu1": c,
             "cu2": cu[0],
             "cu3": cu[1],
             "sign": currencies[c]}
    response = json.loads(response.text)
    
    
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = form2(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            coin = form.cleaned_data["Search_for_a_coin"]
            # redirect to a new URL:
            return HttpResponseRedirect("/crypto/"+coin+",usd/7")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = form2()
    ranking["form"] = form
    for elem in response:
        ranking[str(elem['market_cap_rank'])+"id"] = elem['id']
        ranking[str(elem['market_cap_rank'])+"name"] = elem['name']    
    ranking["favpages"] = favouritePages.objects.all()
    return render(request, "crypto/index.html", ranking)


def form(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        if 'compare' in request.POST:
            form = CoinForm(request.POST)
            search = form2()
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                coin1 = form.cleaned_data["Coin_1"]
                coin2 = form.cleaned_data["Coin_2"]
                c=form.cleaned_data["Currency"]
                time = form.cleaned_data["Time_range_for_graph"]
                
                # redirect to a new URL:
                return HttpResponseRedirect("/crypto/compare/"+coin1+"/"+coin2+"/"+c+"/"+time)
        elif 'search' in request.POST:
            # create a form instance and populate it with data from the request:
            search = form2(request.POST)
            form = CoinForm()
            # check whether it's valid:
            if search.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                coin = search.cleaned_data["Search_for_a_coin"]
                # redirect to a new URL:
                return HttpResponseRedirect("/crypto/"+coin+",usd/7")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = CoinForm()
        search = form2()
    return render(request, "form.html", {"form": form, "search": search, "favpages": favouritePages.objects.all()})

def coins(request, c, id, time):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api2 = config.get('Database', 'api2')
    api3 = config.get('Database', 'api3')
    currencies = {"usd": "$",
                "jpy": "¥",
                "gbp": "£"}
    cu = ["usd", "jpy", "gbp"]
    cu.remove(c)
    tid = ["1", "7", "30", "183", "365", "max"]
    t = ["1 day", "1 week", "1 month", "6 months", "1 year", "Max"]
    ind = tid.index(time)
    t1 = t[ind]
    tid.pop(ind)
    t.pop(ind)

    url = "https://pro-api.coingecko.com/api/v3/coins/"+id+"?x_cg_pro_api_key="+api2
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    info = response.json()
    response = json.loads(response.text)
    ti = now.time()
    url2 = "https://pro-api.coingecko.com/api/v3/coins/"+id+"/market_chart?vs_currency="+c+"&days="+time+"&x_cg_pro_api_key="+api3
    headers2 = {"accept": "application/json"}
    response3 = requests.get(url2, headers=headers2).json()["prices"]
 
    x = list(map(bettertime, response3))
    y = list(map(betterprice, response3))


    ti = ti-now.time()
  
    hover_tool = HoverTool(tooltips=[("time", '@x{%Y-%m-%d %H:%m}'), ("price", currencies[c]+'@y')],
                  formatters={'@x': 'datetime', '@y': 'numeral'} , mode='vline')
    
    p = figure(width=1350,
                  x_axis_label="Time",
                  y_axis_label="Price in "+currencies[c],
                  background_fill_alpha=0,
                  border_fill_alpha=0,
                  tools="pan,wheel_zoom,box_zoom,reset",
                  x_axis_type = "datetime")
    p.add_tools(hover_tool)
    
    p.line(x,y,line_width=1.5,line_color="#f54290")
    graph_script, graph_div = components(p)

    coininfo = {"name": response["name"],
               "lower_name": response["name"].lower(),
               "price": "{:,}".format(response["market_data"]["current_price"][c]) if response["market_data"]["current_price"][c] > 1000 else response["market_data"]["current_price"][c],
               "logo": response["image"]["small"],
               "cap": "{:,}".format(response["market_data"]["market_cap"][c]),
               "sign": currencies[c],
               "graph_script": graph_script,
               "graph_div": graph_div,
               "id": response["id"],
               "c1": currencies[c]+" "+ c.upper(),
             "c2": currencies[cu[0]]+" "+cu[0].upper(),
             "c3": currencies[cu[1]]+" "+cu[1].upper(),
             "cu1": c,
             "cu2": cu[0],
             "cu3": cu[1],
             "tu1": time,
             "t1": t1,
             "tu2": tid[0],
             "t2": t[0], 
             "tu3": tid[1],
             "t3": t[1], 
             "tu4": tid[2],
             "t4": t[2], 
             "tu5": tid[3],
             "t5": t[3], 
             "tu6": tid[4],
             "t6": t[4],
             "ath": response["market_data"]["ath"][c],
             "athd": response["market_data"]["ath_date"][c][:9],
             "atl": float(response["market_data"]["atl"][c]),
             "atld": response["market_data"]["atl_date"][c][:9],
             "high": response["market_data"]["high_24h"][c] if c in response["market_data"]["high_24h"] else response["market_data"]["high_24h"][c.upper()],
             "low": response["market_data"]["low_24h"][c] if c in response["market_data"]["low_24h"] else response["market_data"]["low_24h"][c.upper()],
             "volume": "{:,}".format(response["market_data"]["total_volume"][c]),
             "datecreated":response["genesis_date"] if response["genesis_date"]!= None else "Not available",
             "desc": response["description"]["en"],
             "rank": response["market_data"]["market_cap_rank"] if response["market_data"]["market_cap_rank"]!=None else "Not available"}
    coininfo["t"] = ti
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        if "search" in request.POST:
            form = form2(request.POST)
            compare = form3()
            fav = bookmark()
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                coin = form.cleaned_data["Search_for_a_coin"]
                # redirect to a new URL:
                return HttpResponseRedirect("/crypto/"+coin+",usd/7")
        elif "compare" in request.POST:
            form = form2()
            compare = form3(request.POST)
            fav = bookmark()
            if compare.is_valid():
                id1 = compare.cleaned_data["Compare_with_another_coin"]
                return HttpResponseRedirect("/crypto/compare/"+id+"/"+id1+"/"+c+"/"+time)
        else:
            form = form2()
            compare = form3()
            fav = bookmark(request.POST)
            if fav.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                faved = fav.cleaned_data["bookmark_this_page"]
                if faved == True:
                    f = favouritePages(name= coininfo["name"], url="http://127.0.0.1:8000/crypto/"+id+","+c+"/"+time, currency=currencies[c], time=t1)
                    f.save()
                else:
                    favouritePages.objects.filter(name=coininfo["name"], currency=currencies[c], time=t1).delete()
                # redirect to a new URL


    # if a GET (or any other method) we'll create a blank form
    else:
        form = form2()
        compare=form3()
        fav = bookmark(initial={'bookmark_this_page':False if not favouritePages.objects.filter(name=coininfo["name"], currency=currencies[c], time=t1) else True})
    coininfo["form"] = form  
    coininfo["form2"] = compare
    coininfo["fav"] = fav
    coininfo["info"] = info
    coininfo["favpages"] = favouritePages.objects.all()
    if time != "max":
        url = "https://pro-api.coingecko.com/api/v3/coins/"+id+"/market_chart?vs_currency="+c+"&days=max&x_cg_pro_api_key=CG-wzfTQkUNqMM7efmTJ4GWP6JA"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers).json()["prices"]
    else:
        response=response3
    today = datetime.datetime.now()
    year = today - relativedelta(years=2)
    if datetime.datetime.fromtimestamp(response[0][0]//1000) > year:
        coininfo["graph_script2"], coininfo["graph_div2"] = "Not available since there is not enough data for prediction",""
    else:
        dct = {}
        dct["ds"] = map(bettertime, response)
        dct["y"] = map(betterprice, response)
        df = pd.DataFrame(dct)
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=365, include_history=False)
        forecast = m.predict(future)
        df = df.rename(columns={'y': 'yhat'})
        a = df._append(forecast,ignore_index=True)
        a['yhat'] = a['yhat'].map(nn)
        source = ColumnDataSource(a)

        p = figure(x_axis_type = "datetime", x_axis_label="Time", y_axis_label="Price in "+currencies[c], width=1350, tools="pan,wheel_zoom,box_zoom,reset",background_fill_alpha=0,
                    border_fill_alpha=0,)
        hover_tool2 = HoverTool(tooltips=[("time", '@ds{%Y-%m-%d %H:%m}'), ("price", currencies[c]+'@yhat')],
                    formatters={'@ds': 'datetime'} , mode='vline')
        p.add_tools(hover_tool2)
        dst_start = Span(location=datetime.datetime.now(), dimension='height',
                    line_color='#f54290', line_width=1.5, name="Now")
        p.add_layout(dst_start)
        r_line = p.line([datetime.datetime.now()], [0], legend_label='Now', 
                    line_color="#f54290", line_width=1.5)
        r_line.visible = False
        p.legend.location = "top_left"
        p.yaxis[0].formatter = NumeralTickFormatter(format="0.000 a")
        p.line(x="ds", y="yhat", source=source, line_width=1.5)
        graph_script, graph_div = components(p)
        coininfo["graph_script2"], coininfo["graph_div2"]=graph_script, graph_div
    return render(request, "crypto/coin_info.html", coininfo)

def compare(request, id1, id2, c, time):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api4 = config.get('Database', 'api4')
    api5 = config.get('Database', 'api5')
    api3 = config.get('Database', 'api3')
    s1 = now.time()
    url2 = "https://pro-api.coingecko.com/api/v3/coins/"+id1+"/market_chart?vs_currency="+c+"&days="+time+"&x_cg_pro_api_key="+api4
    headers2 = {"accept": "application/json"}
    response2 = requests.get(url2, headers=headers2).json()["prices"]
    
    x1 = list(map(bettertime, response2))
    y1 = list(map(betterprice, response2))

    url = "https://pro-api.coingecko.com/api/v3/coins/"+id2+"/market_chart?vs_currency="+c+"&days="+time+"&x_cg_pro_api_key="+api4
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers).json()["prices"]
    x2 = list(map(bettertime, response))
    y2 = list(map(betterprice, response))

    currencies = {"usd": "$",
                "jpy": "¥",
                "gbp": "£"}

    hover_tool = HoverTool(tooltips=[("time", '@x{%Y-%m-%d %H:%m}'), ("price", currencies[c]+'@y'), ("coin", "$name")],
                    formatters={'@x': 'datetime'})
    
    url3 = "https://pro-api.coingecko.com/api/v3/coins/"+id1+"?x_cg_pro_api_key="+api5
    headers3 = {"accept": "application/json"}
    response3 = requests.get(url3, headers=headers3)
    response3 = json.loads(response3.text)

    url4 = "https://pro-api.coingecko.com/api/v3/coins/"+id2+"?x_cg_pro_api_key="+api5
    headers4 = {"accept": "application/json"}
    response4 = requests.get(url4, headers=headers4)
    response4 = json.loads(response4.text)

    p = figure(width=1350,
               height=700,
                x_axis_label="Time",
                y_axis_label="Price in "+ c.upper(),
                background_fill_alpha=0,
                border_fill_alpha=0,
                tools="pan,wheel_zoom,box_zoom,save,reset",
                x_axis_type="datetime",
                y_range = Range1d(min(y1), max(y1), bounds=(min(y1),max(y1))))


    r0 = p.line(x1,y1, color = "deeppink", name=response3["name"], line_width=0.8)
    p.yaxis.axis_label = response3["name"]+" Price in "+currencies[c]
    p.add_tools(hover_tool)

    

    p.extra_y_ranges['foo'] = Range1d(min(y2),max(y2), bounds = (min(y2),max(y2)) )
    r1 = p.line(x2, y2, color="blue", y_range_name="foo", name=response4["name"], line_width=0.8)
    legend = Legend(items=[(response3["name"], [r0]), (response4["name"], [r1])], location="center")
    p.legend.title = 'Coins'
    

    ax2 = LinearAxis(y_range_name="foo", axis_label=response4["name"]+ " Price in "+currencies[c])
    p.add_layout(ax2, 'right')
    p.add_layout(legend, "right")
    graph_script, graph_div = components(p)

    s1 = s1-now.time()
    s2 = now.time()
    cu = ["usd", "jpy", "gbp"]
    cu.remove(c)
    tid = ["1", "7", "30", "183", "365", "max"]
    t = ["1 day", "1 week", "1 month", "6 months", "1 year", "Max"]
    ind = tid.index(time)
    t1 = t[ind]
    tid.pop(ind)
    t.pop(ind)

    coins = {"name1": response3["name"],
             "id1": id1,
             "id2": id2,
             "c1": currencies[c]+" "+ c.upper(),
             "c2": currencies[cu[0]]+" "+cu[0].upper(),
             "c3": currencies[cu[1]]+" "+cu[1].upper(),
             "cu1": c,
             "cu2": cu[0],
             "cu3": cu[1],
             "tu1": time,
             "t1": t1,
             "tu2": tid[0],
             "t2": t[0], 
             "tu3": tid[1],
             "t3": t[1], 
             "tu4": tid[2],
             "t4": t[2], 
             "tu5": tid[3],
             "t5": t[3], 
             "tu6": tid[4],
             "t6": t[4], 
               "lower_name1": response3["name"].lower(),
               "price1": "{:,}".format(response3["market_data"]["current_price"][c]),
               "logo1": response3["image"]["small"],
               "cap1": "{:,}".format(response3["market_data"]["market_cap"][c]),
               "caprank1": response3["market_data"]["market_cap_rank"],
               "day1": response3["market_data"]["price_change_percentage_24h"],
               "week1": response3["market_data"]["price_change_percentage_7d"],
               "month1": response3["market_data"]["price_change_percentage_30d"],
               "year1": response3["market_data"]["price_change_percentage_1y"],
               "sign": currencies[c],
               "graph_script": graph_script,
               "graph_div": graph_div,
               "name2": response4["name"],
               "lower_name2": response4["name"].lower(),
               "price2": "{:,}".format(response4["market_data"]["current_price"][c]),
               "logo2": response4["image"]["small"],
               "cap2": "{:,}".format(response4["market_data"]["market_cap"][c]),
               "caprank2": response4["market_data"]["market_cap_rank"],
               "day2": response4["market_data"]["price_change_percentage_24h"],
               "week2": response4["market_data"]["price_change_percentage_7d"],
               "month2": response4["market_data"]["price_change_percentage_30d"],
               "year2": response4["market_data"]["price_change_percentage_1y"],}
    coins["colorx1"] = color(coins["day1"])
    coins["colory1"] = color(coins["day2"])
    coins["colorx2"] = color(coins["week1"])
    coins["colory2"] = color(coins["week2"])
    coins["colorx3"] = color(coins["month1"])
    coins["colory3"] = color(coins["month2"])
    coins["colorx4"] = color(coins["year1"])
    coins["colory4"] = color(coins["year2"])
    coins["favpages"] = favouritePages.objects.all()
    if request.method == "POST":
        if 'search' in request.POST:
            # create a form instance and populate it with data from the request:
            form = form2(request.POST)
            fav = bookmark()
            # check whether it's valid:
            if form.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                coin = form.cleaned_data["Search_for_a_coin"]
                # redirect to a new URL:
                return HttpResponseRedirect("/crypto/"+coin+",usd/7")
        else:
            form = form2()
            fav = bookmark(request.POST)
            if fav.is_valid():
                # process the data in form.cleaned_data as required
                # ...
                faved = fav.cleaned_data["bookmark_this_page"]
                if faved == True:
                    f = favouritePages(name= coins["name1"]+" and "+ coins["name2"], url="http://127.0.0.1:8000/crypto/compare/"+id1+"/"+id2+"/"+c+"/"+time, currency=currencies[c], time=t1)
                    f.save()
                else:
                    favouritePages.objects.filter(name= coins["name1"]+" and "+ coins["name2"], currency=currencies[c], time=t1).delete()

    # if a GET (or any other method) we'll create a blank form
    else:
        form = form2()
        fav = bookmark(initial={'bookmark_this_page':False if not favouritePages.objects.filter(name= coins["name1"]+" and "+ coins["name2"], currency=currencies[c], time=t1) else True})
    
    
    coins["form"] = form
    coins["fav"] = fav
    s2 = s2 - now.time()
    s3 = now.time()
    if c!="max":
        url = "https://pro-api.coingecko.com/api/v3/coins/"+id1+"/market_chart?vs_currency="+c+"&days=max&x_cg_pro_api_key="+api3
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers).json()["prices"]
        url2 = "https://pro-api.coingecko.com/api/v3/coins/"+id2+"/market_chart?vs_currency="+c+"&days=max&x_cg_pro_api_key="+api3
        headers2 = {"accept": "application/json"}
        response2 = requests.get(url2, headers=headers2).json()["prices"]


    today = datetime.datetime.now()
    year = today - relativedelta(years=2)
    available=True
    if datetime.datetime.fromtimestamp(response[0][0]//1000) > year:
        available=False
    if datetime.datetime.fromtimestamp(response2[0][0]//1000) > year:
        available=False
    
    if available==False:
        coins["graph_script2"], coins["graph_div2"] = "Not Available since there is not enough data for prediction",""
    
    else:
        s3 = s3 - now.time()
        s4 = now.time()
        dct = {}
        dct["ds"] = map(bettertime, response)
        dct["y"] = map(betterprice, response)
        df = pd.DataFrame(dct)
        s4 = s4 - now.time()

        s5 = now.time()
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=365, include_history=False)
        forecast = m.predict(future)
        df1 = df.rename(columns={'y': 'yhat'})
        
        
        a = df1._append(forecast,ignore_index=True)
        miny1 = min(a['yhat'])
        maxy1 = max(a['yhat'])
        minx1 = min(a['ds'])
        maxx1 = max(a['ds'])
        
        a['yhat'] = a['yhat'].map(nn)
       

        source1 = ColumnDataSource(a)
        
        s5 = s5 - now.time()
        s6 = now.time()
        dct = {}
        dct["ds"] = map(bettertime, response2)
        dct["y"] = map(betterprice, response2)
        df = pd.DataFrame(dct)
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=365, include_history=False)
        forecast = m.predict(future)
        df2 = df.rename(columns={'y': 'yhat'})
        a2 = df2._append(forecast,ignore_index=True)
        
        miny2 = min(a2['yhat'])    
        maxy2 = max(a2['yhat'])
        minx2 = min(a2['ds'])
        maxx2 = max(a2['ds'])
        a2['yhat'] = a2['yhat'].map(nn)
        source2 = ColumnDataSource(a2)
        
        s6 = s6 - now.time()
        s7 = now.time()
        hover_tool2 = HoverTool(tooltips=[("time", '@ds{%Y-%m-%d %H:%m}'), ("price", currencies[c]+'@yhat'), ("coin", "$name")],
                        formatters={'@ds': 'datetime'})
        
        p = figure(width=1350,
                height=700,
                    x_axis_label="Time",
                    y_axis_label="Price in "+ c.upper(),
                    background_fill_alpha=0,
                    border_fill_alpha=0,
                    tools="pan,wheel_zoom,box_zoom,save,reset",
                    x_axis_type="datetime",
                    y_range = Range1d(miny1, maxy1, bounds=(miny1,maxy1)),
                    x_range=(max(minx1, minx2), maxx1))


        r0 = p.line(x="ds",y="yhat",source=source1, color = "deeppink", name=response3["name"], line_width=0.8)
        p.yaxis.axis_label = response3["name"]+" Price in "+currencies[c]
        p.add_tools(hover_tool2)
        dst_start = Span(location=datetime.datetime.now(), dimension='height',
                    line_color='green', line_width=1.5, name="Now")
        p.add_layout(dst_start)
        r_line = p.line([datetime.datetime.now()], [0],
                    line_color="green", line_width=1.5)
        r_line.visible = False
        
        p.extra_y_ranges['foo'] = Range1d(miny2,maxy2, bounds = (miny2,maxy2) )
        r1 = p.line(x="ds",y="yhat",source=source2,color="blue", y_range_name="foo", name=response4["name"], line_width=0.8)
        legend = Legend(items=[(response3["name"], [r0]), (response4["name"], [r1]), ("Now", [r_line])], location="center")
        p.legend.title = 'Coins'
        

        ax2 = LinearAxis(y_range_name="foo", axis_label=response4["name"]+ " Price in "+currencies[c])
        p.add_layout(ax2, 'right')
        p.add_layout(legend, "right")
        graph_script2, graph_div2 = components(p)
        coins["graph_script2"], coins["graph_div2"] = graph_script2, graph_div2
        s7 = s7 - now.time()
        coins["s1"] = s1
        coins["s2"] = s2
        coins["s3"] = s3
        coins["s4"] = s4
        coins["s5"] = s5
        coins["s6"] = s6
        coins["s7"] = s7
    return render(request, "crypto/compare.html", coins)

def hangman(request):
    data = {}
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = form2(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            coin = form.cleaned_data["Search_for_a_coin"]
            # redirect to a new URL:
            return HttpResponseRedirect("/crypto/"+coin+",usd/7")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = form2()    
        desc = {'bitcoin': 'The first decentralized cryptocurrency, market cap number 1', 
                'blockchain': 'A distributed database shared among computers in a peer-to-peer network that keeps a record of transactions. It is decentralized means no single entity controls or owns the netwrok.', 
                'cryptocurrency': 'A digital currency that uses cryptography to secure transactions', 
                'cryptography': 'Type of encryption that uses maths to secure transactions', 
                'market cap': 'Total value of all the coins that have been mined', 
                'volume': 'The total number of coins traded', 
                'price': 'It changes due to the supply and demand of the coin. The price varies on different exchanges since there is no fixed global price for a coin. Some platforms require a transaction fee. Different exchanges have different levels of supply and demand so price might vary. ', 
                'wallet': 'Software that allows users to store and use cryptocurrency', 
                'mining': 'A process that cryptocurrencies use to generate new coins and finalize transactions', 
                'exchange': 'A business where users can buy, sell or trade cryptocurrencies. They often have a transaction fee and they should have strong security.', 
                'ledger': 'Keeps a record of all transactions held in a network', 
                'digital': 'Cryptocurrency is a type of digital currency. It doesn\'t have a physical form', 
                'transaction': 'Users exchange cryptocurrencies on a blockchain. Transactions must be verified by mining. ', 
                'security': 'Crypto crime levels are increasing so it is important to have good security. Cryptography is used to secure transactions and blockchains are known to be generally safe.', 
                'computer': 'Crypto mining uses powerful computers to solve mathematical problems. This process generates more coins.', 
                'key': 'A private key is like a password and allows the user to perform transactions and prove ownership of the coins. ', 
                'satoshi nakamoto': 'Inventor of Bitcoin, it is thought to be a pseudonym.', 
                'investment': 'Cryptocurrency can be a type of investment. Crypto investments are risky since the market can be volatile and unpredictable.', 
                'encryption': 'Secures transactions to protect against fraud'}
        word = random.choice(['bitcoin', 'blockchain', 'cryptocurrency', 'cryptography', 'market cap', 'volume', 'price', 'wallet', 'mining', 'exchange', 'ledger', 'digital', 'transaction', 'security', 'computer', 'key', 'satoshi nakamoto', 'investment', 'encryption'])
        data["word"] = word
        current = ["_" if word[i]!=" " else " " for i in range(len(word))]
        data["current"] = "".join(current)
        data_json = json.dumps(data)
        return render(request, 'crypto/hangman.html', {"range": [str(elem) for elem in range(1,20)], "data": data_json, "form": form, "word": word, "current": ("".join(current)), "description": desc[word], "favpages": favouritePages.objects.all()})

def get_data_hangman(request):
    if request.method == "GET":
        keypress = request.GET['press']
        word = request.GET['word']
        current= list(request.GET['current'])
        wrong_count = request.GET['wrong_count']
        wrong_letters  = request.GET['wrong_letters']
        done = True
        wrong = False
        if keypress not in word:
            wrong = True           
            if keypress not in wrong_letters:
                wrong_count = str(int(wrong_count)+1)
                wrong_letters += keypress
        for i in range(len(word)):
            if word[i] == keypress:
                current[i] = word[i]  
            if current[i] == "_":
                done = False     
        reply = {"word": word, "current": "".join(current), "done": done, "wrong_count": wrong_count, "wrong_letters": wrong_letters}
    return JsonResponse(reply)

def memory(request):
    config = configparser.ConfigParser()
    config.read('config.ini')
    api6 = config.get('Database', 'api6')
    api7 = config.get('Database', 'api7')
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = form2(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            coin = form.cleaned_data["Search_for_a_coin"]
            # redirect to a new URL:
            return HttpResponseRedirect("/crypto/"+coin+",usd/7")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = form2()
    url = "https://pro-api.coingecko.com/api/v3/coins/list?x_cg_pro_api_key="+api6
    headers = {"accept": "application/json"}
    response2 = requests.get(url, headers=headers).json()
    ids = []
    for elem in response2:
        ids.append(elem["id"])
    coins = random.sample(ids,8)
    coins2 = [elem for elem in coins]

    url = "https://pro-api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids="+coins[0]+"%2C"+coins[1]+"%2C"+coins[2]+"%2C"+coins[3]+"%2C"+coins[4]+"%2C"+coins[5]+"%2C"+coins[6]+"%2C"+coins[7]+"&x_cg_pro_api_key="+api7
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers).json()
    coins.extend(coins)
    random.shuffle(coins)

    lst = [[response[coins2.index(id)]["name"], response[coins2.index(id)]["image"] if response[coins2.index(id)]["image"] != "missing_large.png" else "https://upload.wikimedia.org/wikipedia/commons/1/14/No_Image_Available.jpg", response[coins2.index(id)]["id"]] for id in coins]

    return render(request, "crypto/memory.html", {"data": lst, "range": [i for i in range(16)], "form": form, "favpages": favouritePages.objects.all()}) 

def favourites(request):    
    data = favouritePages.objects.all()
    return render(request, "crypto/fav.html", {'data': data})

def deleteBookmark(request):
    if request.method=="GET":
        name=request.GET['name']
        currency=request.GET['currency']
        time=request.GET['time']
        favouritePages.objects.filter(name= name, currency=currency, time=time).delete()
    return JsonResponse({"id": name+","+currency+","+time})
