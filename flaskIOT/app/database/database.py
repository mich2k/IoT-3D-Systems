from flask import render_template, request, Blueprint
from app.database.tables import *
from .faker2 import create_faker
from .__init__ import db
import requests
from os import getenv
HERE_API_KEY = getenv('HERE_KEY')

database_blueprint = Blueprint('database', __name__, template_folder='templates', url_prefix='/db')

#CREA IL DB A RUNTIME, SE GIà PRESENTE DROPPA TUTTE LE TABLES
#È LA PRIMA ROUTE DA RAGGIUNGERE QUANDO SI AVVIA IL SISTEMA
@database_blueprint.route('/')
def createDB():
    db.drop_all()
    db.create_all()
    create_faker(db)
    return 'Done'

#AGGIUNTA DI INFORMAZIONI SUL BIDONE
#Le informazioni saranno inviate mediante JSON ogni N secondi.
@database_blueprint.route('/addrecord', methods=['POST'])
def addrecord():
    msgJson = request.get_json()

    #  sf = BinRecord(id_bin, status_attuale, temperature, humidity, co2, str(riempimento))
    try:
        sf = BinRecord(msgJson)
        db.session.add(sf)
        db.session.commit()
    except:
        return 'Error' 
    return 'Done'

#AGGIUNTA DI UN BIDONE
@database_blueprint.route('/addbin', methods=['POST'])
def addbin():
    msgJson = request.get_json()

    try:
        sf = Bin(msgJson)
        db.session.add(sf)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'

#ACCESSO DI UN UTENTE AL BIDONE
@database_blueprint.route('/checkUser/<string:uid>', methods=['GET'])
def checkUser(uid):
    users=User.query.all()
    
    if(len(users)>0): 
        for user in users:
            if(uid == user.uid): return user.uid, '200 OK'
            
    return '201 ERRORE' 

#ACCESSO DI UN OPERATORE AL BIDONE
@database_blueprint.route('/checkOp/<int:id>', methods=['GET'])
def checkOp(id):
    operators=Operator.query.all()
    
    if(len(operators)>0): 
        for operator in operators:
            if(id == operator.id_operator): return operator.id_operator, '200 OK'
            
    return '201 ERRORE' 

#ACCESSO DI UN AMMINISTRATORE AL BIDONE
@database_blueprint.route('/checkAdmin/<string:username>', methods=['GET'])
def checkAdmin(uid):
    admins=Admin.query.all()
    
    if(len(admins)>0): 
        for admin in admins:
            if(uid == admin.uid): return admin.uid, '200 OK'
            
    return '201 ERRORE' 

#AGGIUNTA DI UN USER
@database_blueprint.route('/adduser', methods=['POST'])
def adduser():
    msgJson = request.get_json()
    user = User(Person(username=msgJson['username'], 
                   name=msgJson['name'], 
                   surname=msgJson['surname'],
                   password=msgJson['password'], 
                   city=msgJson['city'], 
                   birth_year=msgJson['year']),
                apartment_ID=msgJson['apartment_ID'],
                internal_number=msgJson['internal_number'])
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return 'Error'
    return 'OK'

#AGGIUNTA DI UN ADMIN
@database_blueprint.route('/addadmin', methods=['POST'])
def addadmin():
    msgJson = request.get_json()
    admin = Admin(Person(username=msgJson['username'], 
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

#AGGIUNTA DI UN OPERATORE
@database_blueprint.route('/addoperator', methods=['POST'])
def addoperator():
    msgJson = request.get_json()
    print(msgJson)
    operator = Operator(id=msgJson['id'])
    try:
        db.session.add(operator)
        db.session.commit()
    except:
        return 'Error'
    return 'Done'
  
#AGGIUNTA DI UN APARTMENT
#inserire qui lat e long dell'appartamento tramite chiamata ad API
#da verificare chiamata ad API
@database_blueprint.route('/addapartment', methods=['POST'])
def addapartment():
    msgJson = request.get_json()
    HERE_API_URL = f'https://geocode.search.hereapi.com/v1/geocode'
    
    #TO CHECK
    address = msgJson['city'] + msgJson['street'] + str(msgJson['street_number'])
    
    params = {
        'q': address + 'italia', 
        'apiKey': HERE_API_KEY
    }
    
    # Do the request and get the response data
    req = requests.get(HERE_API_URL, params=params)
    result = req.json()
    # Use the first result
    lat = result['items'][0]['position']['lat']
    lng = result['items'][0]['position']['lng']
    
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


#Print tables
@database_blueprint.route('/items', methods=['GET'])
def stampaitems():
    
    elenco=[Bin.query.order_by(Bin.id_bin.desc()).all(),
            Apartment.query.order_by(Apartment.apartment_name.desc()).all(),
            User.query.order_by(User.uid.desc()).all(),
            Admin.query.order_by(Admin.uid.desc()).all(),
            BinRecord.query.order_by(BinRecord.id_record.desc()).all()] 
    
    return render_template('listitems.html', listona=elenco)