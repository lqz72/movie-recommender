import random
from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager
import api_view

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
def root():
    return redirect(url_for('index_bp.index'))


@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    movie_list = api_view.get_random_movies(18)

    curr_user_info = api_view.db_manager.get_curr_user_info()

    return render_template('index.html', movie_list=movie_list, curr_user_info=curr_user_info)

