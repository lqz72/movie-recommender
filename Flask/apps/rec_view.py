import os, random, json
from flask import request, redirect, url_for
from flask import jsonify
from flask import Blueprint
from flask import render_template

from Recommender.inference import MovieRecommender
from Recommender.mysql import DBManager
import api_view

rec_bp = Blueprint('rec_bp', __name__, url_prefix='/recommend')


@rec_bp.route('/')
def root():
    movie_list = api_view.get_random_movies(18)

    curr_user_info = api_view.db_manager.get_curr_user_info()

    return render_template('recommend.html', movie_list=movie_list, curr_user_info=curr_user_info)


@rec_bp.route('/<int:user_id>/<int:k>')
def recommend(user_id, k):
    recommender = MovieRecommender(api_view.config)
    db_manager = DBManager()

    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(db_manager.get_movie_info(movie_id))

    print(res)


if __name__ == '__main__':
    pass

