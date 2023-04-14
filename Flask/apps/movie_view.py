import random
from flask import redirect, render_template
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager

movie_bp = Blueprint('movie_bp', __name__, url_prefix='/movie')


@movie_bp.route('/<movie_id>')
def detail(movie_id):
    db_manager = DBManager()
    movie = db_manager.get_movie_info(movie_id)

    return render_template('detail.html', movie=movie)

