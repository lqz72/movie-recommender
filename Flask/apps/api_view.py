import random, os, sys
import requests
import logging
from flask import redirect, render_template, jsonify
from flask import session
from flask import url_for
from flask import Blueprint
from lxml import etree

from Recommender.mysql import DBManager
from Recommender.inference import MovieRecommender

ROOT_PATH = os.path.abspath(os.path.dirname(__file__)).split('Flask')[0]

config = {
    'emb_dim': 32,
    'weight_path': ROOT_PATH + '/ml-100k_sslpop.pt',
    'device': 'cpu',
    'model': 'mf',
    'seed': 10,
    'fix_seed': True,
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;474, Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'X-Request-With': 'XMLHttpRequest',
}

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')

db_manager = DBManager()


# ---------- Function ---------- #
def get_random_movies(k):
    """ 获取随机电影列表

    Args:
        k: the number of random movies

    Returns:
        movie_ids : [,...]
    """
    movie_list = []
    for i in range(k):
        movie_id = random.randint(1, 1682)
        movie_info = db_manager.get_movie_info(movie_id)
        movie_list.append(movie_info)

    return movie_list


def query_movie(keyword):
    """ 根据电影名进行模糊查找

    Returns:
        movie_list : [,...]
    """
    movie_df = db_manager.get_df_data('movie_info')

    res = movie_df[movie_df['movie_name'].str.contains(keyword)]

    movie_list = []
    for row in res.values:
        movie_list.append({
            'movie_id': row[0],
            'movie_name': row[1]
        })

    return movie_list


def get_session():
    """ Return current session data
    """
    res = {
        'uid': session.get('uid', ''),
        'utype': session.get('utype', '')
    }
    return res


# ---------- Router ---------- #
@api_bp.route('/user_pwd/<int:username>', methods=['POST'])
def get_user_pwd(username):
    """ 获取用户密码

    Args:
        username: User's name

    Return:
        A dict likes {'pwd': password}
    """
    res = db_manager.get_specific_user_pwd(username)
    if res == 'UnKnow':
        res = {'pwd': None}
    return jsonify(res)


@api_bp.route('/random_movie', methods=['GET', 'POST'])
def update_random_movies():
    """ 更新随机电影列表

    Returns:
        movie_ids : [ID_1, ID_2, ..., ID_n]
    """
    random_movies = get_random_movies(18)
    return jsonify(random_movies)


@api_bp.route('/add_session/<uid>/<utype>')
def add_session(uid, utype):
    response = redirect(url_for('index_bp.index'))

    session['uid'] = uid
    session['utype'] = utype
    return response


if __name__ == '__main__':
    pass
