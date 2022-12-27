from flask import Blueprint, request
from app.database.tables import Apartment, BinRecord, Bin
from app.database.__init__ import db
import json
import datetime
import requests
from sqlalchemy.sql.expression import func
from os import getenv

WEATHER_API_KEY = getenv('WEATHER_API_KEY')
trap_blueprint = Blueprint('trap', __name__)
#Ricevo il dato, ottengo l'id e modifico lo status


@trap_blueprint.route('/full')
def change_status_f():
    msgJson = request.get_json()
    BinRecord.query()

@trap_blueprint.route('/rigged')
def change_status_r():
    msgJson = request.get_json()


@trap_blueprint.route('/getstatus', methods=['GET', 'POST'])
def calcolastatus():
    msgJson = request.get_json() #id_bin, riempimento, angoli di inclinazione 
    
    msgJson = request.get_json()
    # 1: integro e non-pieno, 2: integro e pieno, 3: manomesso e non-pieno, 4: manomesso e pieno
    
    soglie={"plastica": 0.9, "carta": 0.9, "vetro": 0.8, "umido": 0.7} #soglie fisse
    #soglia_umido={"primavera": 0.6, "estate": 0.5, "autunno": 0.7, "inverno": 0.9} #soglia dinamica per l'organico in base alla stagione
    
    #TODO: modificare il valore del dato in quanto deve essere un datetime
    dd_umido={"medie": 5, "alte": 3, "altissime": 2} #soglia dinamica per l'organico in base alla temperatura

    status_attuale=1 #-->quando non ci sono istanze nella tabella
    tipologia = (Bin.query.filter(Bin.id_bin == msgJson["id_bin"])).first().tipologia
    soglia_attuale=0
    if (tipologia=="umido"):
        now = datetime.datetime.now()
        mese=9 #now.month   --->DA CAMBIARE!!!!!!!
        giorno=now.day
        if(mese>=4 and mese<=10): #mesi caldi
            apartment_ID=(Bin.query.filter(Bin.id_bin == msgJson["id_bin"])).first().apartment_ID
            lat=(Apartment.query.filter(Apartment.apartment_name==apartment_ID)).first().lat
            lon=(Apartment.query.filter(Apartment.apartment_name==apartment_ID)).first().lng
            
            WEATHERE_API_URL = f'https://api.openweathermap.org/data/2.5/weather'
            params = {
                'lat':lat,
                'lon':lon,
                'appid': WEATHER_API_KEY
            }
            req = requests.get(WEATHERE_API_URL, params=params)
            res = req.json()
            temp = res['main']['temp']-272.15 #conversione kelvin-celsius
            temp=int(temp)
            dd_time=0
            if(temp>=20 and temp<=25): #medie
                dd_time=dd_umido["media"]
            if(temp>25 and temp<=30): #alte
                dd_time=dd_umido["alte"]
            if(temp>30): #altissime
                dd_time=dd_umido["altissime"]
                
            #controllo che umido venga svuotato ogni quattro giorni
            #Verificare: mi deve dare la data dell'ultimo svuotamento
            timestamp=BinRecord.query.filter(Bin.id_bin==msgJson["id_bin"]).first().ultimo_svuotamento
            
            last_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            if((now-last_date).day>dd_time): 
                soglia_attuale=0
        else:
            soglia_attuale=soglie["umido"]
    elif(tipologia=='plastica'):
        soglia_attuale=soglie["plastica"]
    elif(tipologia=='carta'):
        soglia_attuale=soglie["carta"]
    elif(tipologia=='vetro'):
        soglia_attuale=soglie["vetro"]

    bin_attuale=BinRecord.query.all()
    if(len(bin_attuale)>0): 
        status_attuale=bin_attuale[0].status

    riempimento_attuale=msgJson['riempimento']

    #passaggio da accappottato a dritto
    if(status_attuale==1 and float(riempimento_attuale)>=soglia_attuale): status_attuale=2
    if(status_attuale==3 and float(riempimento_attuale)>=soglia_attuale): status_attuale=4
    if(status_attuale==2 and float(riempimento_attuale)<soglia_attuale): status_attuale=1
    if(status_attuale==4 and float(riempimento_attuale)<soglia_attuale): status_attuale=3
    
    return str(status_attuale)