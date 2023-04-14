import random
from flask import redirect, render_template, jsonify
from flask import session
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager

login_bp = Blueprint('login_bp', __name__, url_prefix='/login')


@login_bp.route('/')
def login():
    return render_template('log.html')


@login_bp.route('/verify/<uid>/<utype>')
def verify(uid, utype):
    response = redirect(url_for('index_bp.index'))

    session['uid'] = uid
    session['utype'] = utype
    response.set_cookie('utype', utype, max_age=60*60*24)

    db_manager = DBManager()
    db_manager.add_curr_user2db(user_id=uid, user_type=utype)
    return response

