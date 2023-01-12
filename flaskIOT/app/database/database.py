import requests
import datetime
from sqlalchemy import update
from flask import render_template, request, Blueprint
from os import getenv
from app.database.tables import *
from .faker import create_faker
from .__init__ import db
from ..trap.trap import *
from flask import jsonify


HERE_API_KEY = getenv('HERE_KEY')
WEATHER_KEY = getenv('WEATHER_KEY')
database_blueprint = Blueprint(
    'database', __name__, template_folder='templates', url_prefix='/db')

# CREA IL DB A RUNTIME, SE GIà PRESENTE DROPPA TUTTE LE TABLES
# È LA PRIMA ROUTE DA RAGGIUNGERE QUANDO SI AVVIA IL SISTEMA


@database_blueprint.route('/')
def createDB():
    db.drop_all()
    db.create_all()
    create_faker(db)
    return 'Done'

# AGGIUNTA DI INFORMAZIONI SUL BIDONE
# Le informazioni saranno inviate mediante JSON ogni N secondi.


@database_blueprint.route('/addrecord', methods=['POST'])
def addrecord():
    msgJson = request.get_json()
    msgJson["status"] = calcolastatus(
        msgJson["id_bin"], msgJson["riempimento"], msgJson["roll"], msgJson["pitch"], msgJson['co2'])

    try:
        sf = BinRecord(msgJson)
        db.session.add(sf)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

# AGGIUNTA DI UN BIDONE


@database_blueprint.route('/addbin', methods=['POST'])
def addbin():
    msgJson = request.get_json()

    try:
        db.session.add(Bin(msgJson))
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

#TODO Creare un'unica route per l'aggiunta di un utente/admin/operatore sfruttando un campo: role

# AGGIUNTA DI UN USER


@database_blueprint.route('/adduser', methods=['POST'])
def adduser():
    msgJson = request.get_json()
    try:
        user = User(Person(uid=msgJson['uid'],
                           name=msgJson['name'],
                           surname=msgJson['surname'],
                           password=msgJson['password'],
                           city=msgJson['city'],
                           birth_year=msgJson['year']),
                    apartment_ID=msgJson['apartment_ID'],
                    internal_number=msgJson['internal_number'])

        db.session.add(user)
        db.session.commit()
    except:
        return 'Error'
    return 'OK'

# AGGIUNTA DI UN ADMIN


@database_blueprint.route('/addadmin', methods=['POST'])
def addadmin():
    msgJson = request.get_json()

    admin = Admin(Person(uid=msgJson['uid'],
                         name=msgJson['name'],
                         surname=msgJson['surname'],
                         password=msgJson['password'],
                         city=msgJson['city'],
                         birth_year=msgJson['year']))
    try:
        db.session.add(admin)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

# AGGIUNTA DI UN OPERATORE


@database_blueprint.route('/addoperator', methods=['POST'])
def addoperator():
    msgJson = request.get_json()
    operator = Operator(Person(uid=msgJson['uid'],
                               name=msgJson['name'],
                               surname=msgJson['surname'],
                               password=msgJson['password'],
                               city=msgJson['city'],
                               birth_year=msgJson['year']),
                        id=msgJson['id'])
    try:
        db.session.add(operator)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

# AGGIUNTA DI UN APARTMENT
# inserire qui lat e long dell'appartamento tramite chiamata ad API
# da verificare chiamata ad API


@database_blueprint.route('/addapartment', methods=['POST'])
def addapartment():
    msgJson = request.get_json()
    URL = f'https://osm.gmichele.it/search'
    address = msgJson['street'] + " " + \
        str(msgJson['street_number']) + " " + msgJson['city']
    params = {
        'q': address + ' Italia',
    }
    req = requests.get(URL, params=params)
    result = req.json()
    lat = result[0]['lat']
    lng = result[0]['lon']
    apartment = Apartment(apartment_name=msgJson['apartment_name'],
                          city=msgJson['city'],
                          street=msgJson['street'],
                          lat=lat,
                          lng=lng,
                          apartment_street_number=msgJson['street_number'],
                          n_internals=msgJson['n_internals'],
                          associated_admin=msgJson['associated_admin'])

    try:
        db.session.add(apartment)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

# ACCESSO DI UN UTENTE AL BIDONE

@database_blueprint.route('/checkuid/<string:uid>&<int:id_bin>', methods=['GET'])
def check(uid, id_bin):
    users = User.query.all()
    operators = Operator.query.all()
    admins = Admin.query.all()
   
    ultimo_bin_record = BinRecord.query.filter(BinRecord.associated_bin == id_bin).order_by(BinRecord.timestamp.desc()).first()
    if(ultimo_bin_record is None):
        status_attuale=None
    else:
        status_attuale= ultimo_bin_record.status

    if (len(users) > 0):
        for user in users:
            if (uid == user.uid):
                if (status_attuale == 1):
                    return jsonify({"code": 200})
                else:
                    # cerco il bidone più vicino
                    return jsonify({"code": 201, "vicino": ""})
    if (len(admins) > 0):
        for admin in admins:
            if (uid == admin.uid):
                if (status_attuale == 1):
                    return jsonify({"code": 200})
                else:
                    # cerco il bidone più vicino
                    return jsonify({"code": 201, "vicino": ""})
    if (len(operators) > 0):
        for operator in operators:
            if (uid == operator.uid):
                return jsonify({"code": 203})
    
    return jsonify({"code": 202})



# Print tables
@database_blueprint.route('/items', methods=['GET'])
def stampaitems():

    elenco = [Bin.query.order_by(Bin.id_bin.desc()).all(),
              Apartment.query.order_by(Apartment.apartment_name.desc()).all(),
              User.query.order_by(User.uid.desc()).all(),
              Admin.query.order_by(Admin.uid.desc()).all(),
              BinRecord.query.order_by(BinRecord.id_record.desc()).all(),
              TelegramIDChatUser.query.all()]

    return render_template('listitems.html', listona=elenco)


def calcolastatus(id_bin, riempimento, roll, pitch, co2):

    soglie = {"plastica": 0.9, "carta": 0.9,
              "vetro": 0.8, "umido": 0.7}  # soglie fisse

    # soglia dinamica per l'organico in base alla temperatura
    dd_umido = {"medie": 5, "alte": 3, "altissime": 2}

    limite_co2 = 10  # da modificare
    status_attuale = 1  # default del primo record del bidone

    bin_attuale = BinRecord.query.filter(BinRecord.associated_bin == id_bin)
    
    if (bin_attuale.count()):
        status_attuale = (BinRecord.query.filter(BinRecord.associated_bin == id_bin).order_by(
            BinRecord.timestamp.desc()).first()).status

    tipologia = (Bin.query.filter(Bin.id_bin == id_bin)).first().tipologia
    soglia_attuale = 0

    if (tipologia == "umido"):
        now = datetime.datetime.now()
        mese = now.month
        if (mese >= 4 and mese <= 10):  # mesi caldi
            apartment_ID = (Bin.query.filter(
                Bin.id_bin == id_bin)).first().apartment_ID
            lat = (Apartment.query.filter(
                Apartment.apartment_name == apartment_ID)).first().lat
            lon = (Apartment.query.filter(
                Apartment.apartment_name == apartment_ID)).first().lng

            WEATHERE_API_URL = f'https://api.openweathermap.org/data/2.5/weather'
            params = {
                'lat': lat,
                'lon': lon,
                'appid': WEATHER_KEY
            }

            req = requests.get(WEATHERE_API_URL, params=params)
            res = req.json()
            # conversione kelvin-celsius
            temp = int(res['main']['temp']-272.15)
            dd_time = 0

            if (temp >= 20 and temp <= 25):  # medie
                dd_time = dd_umido["media"]

            if (temp > 25 and temp <= 30):  # alte
                dd_time = dd_umido["alte"]

            if (temp > 30):  # altissime
                dd_time = dd_umido["altissime"]

            timestamp = Bin.query.filter(
                Bin.id_bin == id_bin).first().ultimo_svuotamento
            last_date = datetime.datetime.strptime(
                timestamp, "%Y-%m-%d %H:%M:%S")
            now = datetime.datetime.now()

            # temperature alte + sono passo più di deltagiorni
            if ((now-last_date).days > dd_time and dd_time > 0):
                soglia_attuale = 0
            else:
                soglia_attuale = soglie["umido"]
        else:
            soglia_attuale = soglie["umido"]
    elif (tipologia == 'plastica'):
        soglia_attuale = soglie["plastica"]
    elif (tipologia == 'carta'):
        soglia_attuale = soglie["carta"]
    elif (tipologia == 'vetro'):
        soglia_attuale = soglie["vetro"]

    """ 1: integro e non-pieno, 
        2: integro e pieno, 
        3: manomesso e non-pieno, 
        4: manomesso e pieno
    """

    # TODO rendere più fine
    if(riempimento!=None):
        # passaggio da pieno a non pieno e viceversa
        if (status_attuale == 1 and float(riempimento) >= soglia_attuale):
            full_state()
            status_attuale = 2

        if (status_attuale == 3 and float(riempimento) >= soglia_attuale):
            full_state()
            status_attuale = 4

        if (status_attuale == 2 and float(riempimento) < soglia_attuale):
            status_attuale = 1
            db.session.query(Bin).filter(Bin.id_bin == id_bin).update(
                {'ultimo_svuotamento': datetime.datetime.now()})
            db.session.commit()

        if (status_attuale == 4 and float(riempimento) < soglia_attuale):
            status_attuale = 3
            db.session.query(Bin).filter(Bin.id_bin == id_bin).update(
                {'ultimo_svuotamento': datetime.datetime.now()})
            db.session.commit()

    # passaggio da accappottato a dritto e viceversa
    if(roll!=None and pitch!=None):
        if (status_attuale == 3 and (roll < 45 and (abs(pitch-90) < 45))):
            status_attuale = 1

        if (status_attuale == 1 and (roll >= 45 or (abs(pitch-90) >= 45))):
            overturn()
            status_attuale = 3

        if (status_attuale == 4 and (roll < 45 and (abs(pitch-90) < 45))):
            status_attuale = 2

        if (status_attuale == 2 and (roll >= 45 or (abs(pitch-90) >= 45))):
            overturn()
            status_attuale = 4
    if(co2!=None):
        # Caso in cui nel bidone ci dovesse essere un incendio
        if (status_attuale == 3 and co2 < limite_co2):
            status_attuale = 1

        if (status_attuale == 1 and co2 >= limite_co2):
            fire()
            status_attuale = 3

        if (status_attuale == 4 and co2 < limite_co2):
            status_attuale = 2

        if (status_attuale == 2 and co2 >= limite_co2):
            fire()
            status_attuale = 4

    return status_attuale

def set_previsione_status(id_bin, status_previsto):
    db.session.query(Bin).filter(Bin.id_bin == id_bin).update({'previsione_status': status_previsto})
    db.session.commit()

def getstringstatus(status):
    if (status == 1):
        return "integro e non-pieno"
    elif (status == 2):
        return "integro e pieno"
    elif (status == 3):
        return "manomesso e non-pieno"
    elif (status == 4):
        return "manomesso e pieno"
    else:
        return "Error"

#Getters
@database_blueprint.route('/accessAdmin/<string:uid>&<string:password>', methods=['GET'])
def login(uid, password):
    found = False
    for asw in db.session.query(Admin.uid == uid and Admin.password == password).all():
        if asw[0]:
            found = True
            
    return str(found)

@database_blueprint.route('/checkUsername/<string:usr>', methods=['GET'])
def checkusername(usr):
    found = False
    for asw in db.session.query(TelegramIDChatUser.id_user == usr).all():
        if asw[0]:
            found = True
            
    return str(found)

@database_blueprint.route('/checkSession/<string:chatid>&<string:userid>', methods=['GET'])
def checksession(userid):
    found = False
    for asw in db.session.query(TelegramIDChatUser.id_user == userid and TelegramIDChatAdmin.id_user == userid).all():
        if asw[0]:
            found = True
            
    return str(found)


@database_blueprint.route('/setSession/<string:usr>', methods=['GET'])
def setsession(usr):
    db.session.execute(update(TelegramIDChatUser).where(TelegramIDChatUser.id_user == usr).values({'logged': True}))
    db.session.commit()
    return 'done'

# Getters, return json

@database_blueprint.route('getbins/<string:city>', methods=['GET'])
def getbins(city):
    pass

@database_blueprint.route('/getusers/<string:city>', methods=['GET'])
def getusers(city):
    pass

@database_blueprint.route('/getypes/<string:apartment>', methods=['GET'])
def getypes(city):
    pass

@database_blueprint.route('/getapartmentusers/<string:apartment>', methods=['GET'])
def getapartmentusers(city):
    pass

@database_blueprint.route('/getbininfo/<string:idbin>', methods=['GET'])
def getbininfo(idbin):
    pass