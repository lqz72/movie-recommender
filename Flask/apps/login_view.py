import random
from flask import redirect, render_template, jsonify
from flask import session
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager
import api_view

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login')
def login():
    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    if session.get('uid'):
        session.pop('uid')
        session.pop('utype')
    return render_template('login.html')



