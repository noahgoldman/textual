from flask import request
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError, IntegrityError

from textlink import app, Session
from textlink.models import Entry, Phone, List, PhoneCarrier
from textlink.Obj2JSON import jsonobj
from textlink.helpers import API, get_or_abort
from textlink.sources.sendByTwilio import sendSMS
from textlink.sources.emailgateway import *

@app.route('/lists', methods=['POST'])
@API
def create_list():
    """Creates a list with name and returns a JSON object of the list"""
    name = request.form.get('name')
    lst = List(name)
    
    session = Session()
    session.add(lst)
    session.commit()

    return jsonobj(lst)

@app.route('/entries/', methods=['GET']) #for Testing:
def get_all_entries():
    """Returns a list containing all entries in a JSON object"""
    session = Session()
    es = session.query(Entry).all()
    es = jsonobj(es)
    return es

@app.route('/phones/', methods=['GET']) #for Testing:
def get_all_phones():
    """Returns a list containing all phones in a JSON object"""
    session = Session()
    es = session.query(Phone).all()
    es = jsonobj(es)
    return es

@app.route('/phones/<phone_id>/allEntries', methods=['GET']) #for Testing:
def getPhoneEntries(phone_id):
    """Returns a list in JSON form of all entries containing phone_id"""
    session = Session()
    try:
        es = session.query(Entry).filter_by(phone_id=phone_id).all()
    except NoResultFound:
        return none
    else:
        es = jsonobj(es)
        return es

@app.route('/phones/<phone_id>', methods=['GET']) #for Testing:
def get_phone(phone_id):
    """Returns a JSON object with the name and number belonging to phone_id"""
    session = Session()
    es = get_or_abort(Phone, phone_id, session)
    es = jsonobj(es)
    return es

@app.route('/lists/getAll', methods=['GET']) #for Testing:
def getLists():
    """Returns a list of all Lists in the db, in the form of a JSON object"""
    session = Session()
    es = session.query(List).all()
    es = jsonobj(es)
    return es
    
@app.route('/lists/<list_id>', methods=['GET']) #for Testing:
def list_list(list_id):
    """Returns a list of all the entries in list_id, in JSON"""
    session = Session()
    try:
        es = session.query(Entry).filter_by(list_id=list_id).all()
    except NoresultFound:
        return None
    else: 
        es = jsonobj(es)
        return es

@app.route('/phones/', methods=['GET']) #for Testing:
def get_phones():
    session = Session()
    try:
        es = session.query(Phone).all()
    except NoresultFound:
        return None
    else: 
        es = jsonobj(es)
        return es
    
@app.route('/phones/<phone_id>/carriers', methods=['GET']) #for Testing:
def get_carriers(phone_id):
    session = Session()
    try:
        es = session.query(Phone).filter_by(phone_id=phone_id).one()
    except NoresultFound:
        return None
    else: 
        carriers = session.query(PhoneCarrier).filter_by(phone_id=phone_id).all()
        return jsonobj(carriers)

    
@app.route('/lists/<list_id>/add', methods=['POST']) #for Testing:
def add_user(list_id):
    """Creates new entry in list_id with number and name. 
    Returns a JSON object of the entry or an error if it alreayd exists"""
    num = request.form.get('number')
    name = request.form.get('name')
    session = Session()
    email = ""
    try:
        phone = session.query(Phone).filter_by(number=num).one()
    except NoResultFound:
        phone = Phone(name,int(num))
        session.add(phone)
        session.commit()
        init_possible_carriers(num)
    
    entry = Entry(list_id, phone.phone_id)
    
    try:
        session.add(entry)
        session.commit()
    except (IntegrityError,InvalidRequestError):
        Session.rollback()
        return "Phone already exists for this list"
    else: 
        return jsonobj(entry)

@app.route('/lists/<list_id>/send_email',methods=['POST'])
def send_text(list_id):
    """Sends a text via email to all entries in list_id"""
    sender = request.form.get('sender')
    #print sender
    message = request.form.get('message')
    session = Session()
    lst = session.query(List).get(list_id)
    #attachments = request.form.get('attachments')
    #print message
    for ent in lst.entries:
        print dir(ent)
        text_by_email(ent.phone.number, sender, message, ent.phone.textemail)
    return {}
        
@app.route('/lists/check_for_bounces',methods=['GET'])
def check_for_bounces():
    checkForBounces()
    return jsonobj({})


@app.route('/lists/<list_id>/send_twilio',methods=['POST'])
def send_text_Twilio(list_id):
    """Sends a text via the Twilio API to all entries in list_id"""
    sender = request.form.get('sender')
    print sender
    message = request.form.get('message')

    session = Session()
    lst = session.query(List).get(list_id)
    assert lst
    #attachments = request.form.get('attachments')
    print message
    for entry in lst.entries:
        print "sent message"
        sendSMS("AC0955b5ae6e4e14861d9e1f61e7d0680f","2dc773f8f669503c2dd6021d8b7bf5b7", sender, entry.phone.number, message)
    return "hello"
