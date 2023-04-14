import random
from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager

index_bp = Blueprint('index_bp', __name__)


@index_bp.route('/')
def root():
    return redirect(url_for('index_bp.index'))


@index_bp.route('/index', methods=['GET', 'POST'])
def index():
    db_manager = DBManager()
    movie_list = []
    for i in range(18):
        movie_id = random.randint(1, 1682)
        movie_info = db_manager.get_movie_info(movie_id)
        movie_list.append(movie_info)

    curr_user_info = db_manager.get_curr_user_info()

    return render_template('index.html', movie_list=movie_list, curr_user_info=curr_user_info)

