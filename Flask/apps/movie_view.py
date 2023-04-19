import random
from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager
import api_view

movie_bp = Blueprint('movie_bp', __name__, url_prefix='/movie')


@movie_bp.route('/')
def root():
    return redirect(url_for('index_bp.index'))


@movie_bp.route('/<movie_id>', methods=['GET', 'POST'])
def movie_info(movie_id):
    movie = api_view.db_manager.get_movie_info(movie_id)

    return render_template('movie.html', movie=movie)

