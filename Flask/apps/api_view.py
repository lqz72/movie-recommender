import random, os, sys
from flask import redirect, render_template, jsonify
from flask import session
from flask import url_for
from flask import Blueprint

from Recommender.mysql import DBManager
from Recommender.inference import MovieRecommender


api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

ROOT_PATH = os.path.abspath(os.path.dirname(__file__)).split('Flask')[0]

config = {
        'emb_dim': 32,
        'weight_path': ROOT_PATH + '/ml-100k_sslpop.pt',
        'device': 'cpu',
        'model': 'mf',
        'seed': 10,
        'fix_seed': True,
}


@api_bp.route('/user_pwd/<int:username>', methods=['POST'])
def get_user_pwd(username):
    db_manager = DBManager()
    res = db_manager.get_specific_user_pwd(username)
    if res == 'UnKnow':
        res = {'pwd': None}
    return jsonify(res)


@api_bp.route('/random_movie', methods=['GET', 'POST'])
def get_random_movies():
    db_manager = DBManager()
    movie_list = []
    for i in range(18):
        movie_id = random.randint(1, 1682)
        movie_info = db_manager.get_movie_info(movie_id)
        movie_list.append(movie_info)

    return jsonify(movie_list)


@api_bp.route('/recommend/<int:k>')
def get_recommend_movie(k):
    recommender = MovieRecommender(config)
    db_manager = DBManager()

    user_id = db_manager.get_curr_user_info()['user_id']
    print(user_id)
    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(db_manager.get_movie_info(movie_id))

    return jsonify(res)