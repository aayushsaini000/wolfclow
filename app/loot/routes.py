from flask import render_template, url_for, jsonify, redirect, request
from app.loot import bp
from flask_login import login_required
from app.main.forms import EmptyForm
from app.models import Host
from app import db
from datetime import datetime
from app import csrf
import base64
import json


@bp.route('/host-details/<guid>', methods=['POST'])
@csrf.exempt #disable csrf on this function
def host_details(guid):
    """
    receives data from client and add it to database
    """
    if request.method == 'POST':
        #output = base64.b64decode(request.form.get('data'))
        #print(request.form.get('data'))
        output = request.get_data().decode('UTF-8')
        hostinfo = json.loads(output)
        obj = Host.query.filter_by(guid=guid).first()
        obj.systeminfo = hostinfo['systeminfo']
        obj.arp_info = hostinfo['arp']
        obj.open_connections = hostinfo['netinfo']
        obj.processes = hostinfo['procinfo']
        obj.network_info = hostinfo['domaininfo']
        db.session.commit()
        return "OK"


