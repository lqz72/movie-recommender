import random
from flask import redirect, render_template
from flask import url_for, session, request
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
    curr_user_info = api_view.get_session()

    return render_template('index.html', movie_list=movie_list, curr_user_info=curr_user_info)


@index_bp.route('/index/query/<movie_name>', methods=['GET', 'POST'])
def query(movie_name):
    print(movie_name)

    movie_list = api_view.query_movie(movie_name)
    curr_user_info = api_view.get_session()

    return render_template('index.html', movie_list=movie_list, curr_user_info=curr_user_info)

