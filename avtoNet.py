import json
import os
import time
from datetime import datetime

currPath = os.path.dirname(os.path.abspath(__file__))
parentPath = os.path.dirname(currPath)
libPath = parentPath+'/jan-lib'

# tole moramo dodati da lahko importamo py file iz drugih lokacij
import sys
sys.path.insert(1, libPath)

import jan_sqlite
import jan_email
import jan_avtoNet

class Url:
    def __init__(self, znamka, model, url):
        self.znamka = znamka
        self.model = model
        self.url = url

def isSamePrice(newPrice, oldPrices):
    np = newPrice.replace('.','')
    npI = int(np)

    for p in oldPrices:
        opI = p[3]

        if npI == opI:
            return True
    
    return False

def getLatestPrice(id):
    sqlConn = jan_sqlite.create_connection(currPath+"/avtoNet.db")

    with sqlConn:
        results = jan_sqlite.run_query(sqlConn,"SELECT * FROM prices WHERE avto_net_id = '"+id+"' ORDER BY created_on")

    return results[0][3]

# startDate -> 2020-03-08 17:20:00
def notifyByEmail(startDate):
    html = '<html><head></head><body><h2>Nove ponudbe</h2></br>'

    html += '<table border="1"><thead><tr><td>Naziv</td><td>Cena</td><td>Link</td></tr></thead><tbody>'

    sqlConn = jan_sqlite.create_connection(currPath+"/avtoNet.db")

    with sqlConn:
        results = jan_sqlite.run_query(sqlConn,"SELECT * FROM cars WHERE created_on > '"+startDate+"'")

    for result in results:
        avtoNetId = result[2]
        avtoNetId = str(avtoNetId)
        title = result[3]

        latestPrice = getLatestPrice(avtoNetId)

        avtoNet = jan_avtoNet.AvtoNet()
        url = avtoNet.createLink(avtoNetId)

        html += '<tr><td>'+title+'</td><td>'+str(latestPrice)+'</td><td>'+url+'</td></tr>'

    html += '</tbody></table><h2>Spremembe cen</h2>'

    html += '<table border="1"><thead><tr><td>Naziv</td><td>Nova cena</td><td>Cena</td><td>Link</td></tr></thead><tbody>'

    with sqlConn:
        results = jan_sqlite.run_query(sqlConn,"SELECT * FROM cars WHERE price_change_on > '"+startDate+"'")

    for result in results:
        avtoNetId = result[2]
        avtoNetId = str(avtoNetId)
        title = result[3]

        latestPrice = getLatestPrice(avtoNetId)

        results = jan_sqlite.run_query(sqlConn,"SELECT * FROM prices WHERE avto_net_id = '"+avtoNetId+"' ORDER BY created_on")

        beforeLatestPrice = results[1][3]

        avtoNet = jan_avtoNet.AvtoNet()
        url = avtoNet.createLink(avtoNetId)

        html += '<tr><td>'+title+'</td><td>'+str(latestPrice)+'</td><td>'+str(beforeLatestPrice)+'</td><td>'+url+'</td></tr>'

    html += '</body></html>'

    email = jan_email.Email()
    email.setEmailAsHtml('jan.cvek@gmail.com','Avto.Net API - NOVE PONUDBE',html)

def searchNewCars():
    searches = (
        Url('Volkswagen','Passat','https://www.avto.net/Ads/results.asp?znamka=Volkswagen&model=Passat&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=9000&cenaMax=14000&letnikMin=2015&letnikMax=2090&bencin=202&starost2=999&oblika=13&ccmMin=1800&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=170000&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&zaloga=10&arhiv=&presort=&tipsort=&stran=') ,
        Url('Skoda','Octavia','https://www.avto.net/Ads/results.asp?znamka=%8Akoda&model=Octavia&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=9000&cenaMax=14000&letnikMin=2015&letnikMax=2090&bencin=202&starost2=999&oblika=13&ccmMin=1800&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=170000&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&zaloga=10&arhiv=&presort=&tipsort=&stran='),
        Url('Ford','Mondeo','https://www.avto.net/Ads/results.asp?znamka=Ford&model=Mondeo&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=9000&cenaMax=14000&letnikMin=2015&letnikMax=2090&bencin=202&starost2=999&oblika=13&ccmMin=1800&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=170000&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&zaloga=10&arhiv=&presort=&tipsort=&stran='),
        Url('Peugeot','508','https://www.avto.net/Ads/results.asp?znamka=Peugeot&model=508&modelID=&tip=&znamka2=&model2=&tip2=&znamka3=&model3=&tip3=&cenaMin=9000&cenaMax=14000&letnikMin=2015&letnikMax=2090&bencin=202&starost2=999&oblika=13&ccmMin=1800&ccmMax=99999&mocMin=&mocMax=&kmMin=0&kmMax=170000&kwMin=0&kwMax=999&motortakt=&motorvalji=&lokacija=0&sirina=&dolzina=&dolzinaMIN=&dolzinaMAX=&nosilnostMIN=&nosilnostMAX=&lezisc=&presek=&premer=&col=&vijakov=&EToznaka=&vozilo=&airbag=&barva=&barvaint=&EQ1=1000000000&EQ2=1000000000&EQ3=1002000000&EQ4=100000000&EQ5=1000000000&EQ6=1000000000&EQ7=1000100020&EQ8=1010000001&EQ9=100000000&KAT=1010000000&PIA=&PIAzero=&PSLO=&akcija=&paketgarancije=0&broker=&prikazkategorije=&kategorija=&zaloga=10&arhiv=&presort=&tipsort=&stran=')
    )

    for search in searches:
        avtoNet = jan_avtoNet.AvtoNet()
        avtoNet.runSearchByUrl(search.url)

        time.sleep(3)   # Delays for 10 seconds. You can also use a float value.

        avtoNet.getOffers()

        offers = avtoNet._offers

        for offer in offers:
            id = offer.id
            price = offer.cena


            sqlConn = jan_sqlite.create_connection(currPath+"/avtoNet.db")

            with sqlConn:
                existing = jan_sqlite.run_query(sqlConn,"SELECT * FROM cars WHERE avto_net_id = '"+id+"'")

                if len(existing) > 0:
                    # AVTO ŽE OBSTAJA
                    carPrices = jan_sqlite.run_query(sqlConn,"SELECT * FROM prices WHERE avto_net_id = '"+id+"' ORDER BY created_on")

                    if not isSamePrice(price, carPrices):
                        # CENA SE JE SPREMENILA
                        # za spremljanje sprememb cen imamo na cars tabeli parameter price_change_on 

                        today = datetime.now()
                        dt_string = today.strftime("%Y-%m-%d %H:%M:%S")

                        jan_sqlite.run_query(sqlConn, "UPDATE cars SET price_change_on = '"+dt_string+"' WHERE avto_net_id='"+ id+"'")

                        pramas2 = 'avto_net_id,price' 
                        values2 = (str(id),int(price.replace('.','')))
                        jan_sqlite.insert_data(sqlConn, 'prices', pramas2, values2)
                else:
                    # NOV AVTO
                    # pri novem avto imamo parameter created on, s katerim potem lahko dobimi nove avte
                    params = 'avto_net_id,title,first_registration,km,engine,transmition,dealer'
                    values = (id,offer.title,int(offer.prvaReq),offer.km,offer.motor,offer.menjalnik,offer.prodajalec)
                    jan_sqlite.insert_data(sqlConn, 'cars', params, values)

                    pramas2 = 'avto_net_id,price' 
                    values2 = (str(id),int(price.replace('.','')))
                    jan_sqlite.insert_data(sqlConn, 'prices', pramas2, values2)

if __name__ == '__main__':
    searchNewCars()
    notifyByEmail('2020-03-10 01:20:00')    