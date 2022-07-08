import json
import certifi

import pandas as pd
from flask import Flask, render_template, make_response, request, redirect, url_for

from pymongo import MongoClient
import pmdarima as pm

app = Flask(__name__)


client = MongoClient(
    "mongodb+srv://fairuz:hellothere@cluster0.ex2mp.mongodb.net/test", tlsCAFile=certifi.where())
app.db = client.hdi_webpage

lst = ['Afghanistan']
lst1 = ['Bangladesh']
lst2 = ['India']
hdi = pd.read_csv("newhdi.csv")
gni = pd.read_csv("GNI.csv")
le = pd.read_csv("LE.csv")
mys = pd.read_csv("MYS.csv")
eys = pd.read_csv("EYS.csv")
more_data = pd.read_csv("more_data.csv")
p=[.514]


@app.route('/', methods=["GET", "POST"])
def hello_world():
    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template('main.html')

@app.route("/desc", methods=["POST", "GET"])
def description():
    
    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template("desc.html")

@app.route("/about", methods=["POST", "GET"])
def about():
    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template("about_us.html")

@app.route("/predictions", methods=["POST", "GET"])
def pred(b):
    return render_template("index.html", state=lst[-1] )

@app.route("/more")

def more():
    
    more1=more_data[more_data['Country']==lst[-1]]
    x=[]
    for i in range (0,len(more1)):
        x.append(i)
    more1['index']=x
    x.clear()
    more1=more1.drop(['Country'],axis=1)
    
    more1 = more1.set_index('index')
    
    for i in range(0,len(more1)):
        y=more1.loc[i].tolist()
        x.append(y)
        print(x)
    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template("more.html",state=lst[-1], entries=x)
    

def arima(hdi1,b):
    hdi2 = hdi1[hdi1['Region']=='Total']
    hdi2 = hdi2.drop(['Region'],axis=1)
    hdi2= hdi2.set_index('Country')
    hdi2=hdi2.T
    hdi2.index = pd.to_datetime(hdi2.index,format='%Y')
    
    y=hdi2
    x = y[b].tolist()
    train = y[(y.index>='1990-01-01') & (y.index<='2018-01-01')]

    model = pm.auto_arima(train,
                    m=1,seasonal=False,
                    start_p=10,start_q=2,max_order=11,max_p=11,max_q=11,test='adf',error_action='ignore',
                    suppess_warning=True,
                    stepwise=True,trace=True)
    
    forecast = model.predict(n_periods=7,return_conf_int=True)
    x2=forecast[0].tolist()
    for i in range (len(x2)):
        x.append(x2[i])
    
    return x


@app.route('/live-data')
def live_data():

    hdi1 = hdi[hdi['Country'] == lst[-1]]
    gni1 = gni[gni['Country'] == lst[-1]]
    le1 = le[le['Country'] == lst[-1]]
    mys1 = mys[mys['Country'] == lst[-1]]
    eys1 = eys[eys['Country'] == lst[-1]]
    hdif = arima(hdi1,lst[-1])
    gnif = arima(gni1,lst[-1])
    lef = arima(le1,lst[-1])
    eysf = arima(eys1,lst[-1])
    mysf = arima(mys1,lst[-1])
    y = hdif
    y1 = gnif
    y2 = lef
    y3 = eysf
    y4 = mysf
    data1 = [y, y1, y2, y3, y4, y[-5]]
    response = make_response(json.dumps(data1))
    response.content_type = 'application/json'
    p.clear()


    return response


@app.route('/live-data1')
def live_data1():
    hdi1 = hdi[hdi['Country'] == lst1[-1]]
    gni1 = gni[gni['Country'] == lst1[-1]]
    le1 = le[le['Country'] == lst1[-1]]
    mys1 = mys[mys['Country'] == lst1[-1]]
    eys1 = eys[eys['Country'] == lst1[-1]]

    hdi2 = hdi[hdi['Country'] == lst2[-1]]
    gni2 = gni[gni['Country'] == lst2[-1]]
    le2 = le[le['Country'] == lst2[-1]]
    mys2 = mys[mys['Country'] == lst2[-1]]
    eys2 = eys[eys['Country'] == lst2[-1]]

    hdif1 = arima(hdi1,lst1[-1])
    gnif1 = arima(gni1,lst1[-1])
    lef1 = arima(le1,lst1[-1])
    eysf1 = arima(eys1,lst1[-1])
    mysf1 = arima(mys1,lst1[-1])

    y = hdif1
    y1 = gnif1
    y2 = lef1
    y3 = eysf1
    y4 = mysf1

    hdif2 = arima(hdi2,lst2[-1])
    gnif2 = arima(gni2,lst2[-1])
    lef2 = arima(le2,lst2[-1])
    eysf2 = arima(eys2,lst2[-1])
    mysf2 = arima(mys2,lst2[-1])

    y5 = hdif2
    y6 = gnif2
    y7 = lef2
    y8 = eysf2
    y9 = mysf2
    
    print(y6)

    data1 = [y, y1, y2, y3, y4, y5, y6, y7, y8, y9]
    response = make_response(json.dumps(data1))
    response.content_type = 'application/json'

    return response

@app.route('/admin_login', methods=["POST", "GET"])
def admin_login():
    x = app.db.admin_login.find_one()
    if request.method == 'POST':
        b = request.form.get("password")
        if b == x["password"]:
            return redirect(url_for("change"))
        else:
            error = 1
            return render_template("admin_login.html", error=error)

    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template('admin_login.html')


@app.route("/change", methods=["POST","GET"])
def change():

    for x in app.db.Update.find({}):
        
        a=x['contact']
        b = x['project']
        print(a,b)
    for y in app.db.admin_login.find({}):
        c=y['password']
    if request.method == "POST":
        c = request.form.get('password')
        d = request.form.get('contact')
        e = request.form.get('project')
        app.db.admin_login.replace_one(
            
            {"id":"1"},
            {
                "id":"1",
                "password":c})
        
        app.db.Update.replace_one(
            {"id":"1"},
            {
                "id":"1",
                "contact":d,
                "project":e
                })
        return redirect(url_for("admin_login"))
    #print(a,b)
    print(b)
    #a = x['contact']
    #b = x['project']

    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template("change.html",password=c,contact=a,project=b)


@app.route("/compare", methods=["POST","GET"])
def compare():

    if request.method == "POST":
        a = request.form.get('country1')
        b = request.form.get('country2')

        lst1.clear()
        lst2.clear()
        lst1.append(a)
        lst2.append(b)
        
        return redirect(url_for("compare", country1=lst1[-1],country2=lst2[-1]))

    if request.method == "POST":
        ind = request.form.get("state")
        lst.clear()
        lst.append(ind)
        return render_template("index.html", state=ind)

    return render_template("compare.html",country1=lst1[-1],country2=lst2[-1])





if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
    
    
    
    
    
    
    
    
    
    
    
