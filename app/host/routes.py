from flask import render_template, url_for, jsonify, redirect, request
from app.host import bp
from flask_login import login_required
from app.main.forms import EmptyForm
from app.models import Host
from app import db
from datetime import datetime
from app import csrf
import base64
import json


@bp.route('/host-detail/<int:pk>', methods=['GET'])
@login_required
def host_detail(pk):
    """
    Renders host detail page
    """
    form = EmptyForm()
    return render_template('host_detail.html', title='Host Detail', form=form, pk=pk)

@bp.route('/ajax-host-page/<int:pk>', methods=['GET'])
@login_required
def ajax_host_page(pk):
    """
    Ajax request to render host specific data back to host page 
    """
    data = [
        [
            item.computername, item.ip, item.open_connections, item.processes, item.systeminfo, item.arp_info, item.network_info,
        ] for item in Host.query.filter_by(id=pk).all()]
    response = {
        'data': data
    }
    return jsonify(response)