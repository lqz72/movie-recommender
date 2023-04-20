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

    curr_user_info = api_view.get_session()

    return render_template('recommend.html', movie_list=movie_list, curr_user_info=curr_user_info)


@rec_bp.route('/<int:k>')
def get_recommend_movie(k):
    """ 获取当前用户Top-K电影的信息
    Args:
        k: The K parameter in Top-K

    Returns:
        movie_info : [movie_dict,...]
        movie_dict likes {
            movie_id: identity ID,
            movie_name: movie title,
            date: screening date,
            url: imdb URL,
            class: the class of movie (Comedy, Action, ...),
        }
    """
    recommender = MovieRecommender(api_view.config)

    user_id = api_view.get_session()['uid']
    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(api_view.db_manager.get_movie_info(movie_id))

    return jsonify(res)


@rec_bp.route('/<int:user_id>/<int:k>')
def recommend(user_id, k):
    """ Not Usage
    """
    recommender = MovieRecommender(api_view.config)
    db_manager = DBManager()

    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(db_manager.get_movie_info(movie_id))

    print(res)


if __name__ == '__main__':
    pass

