import os
import json
from flask import request, redirect, url_for
from flask import jsonify
from flask import Blueprint
from flask import render_template

from Recommender.inference import MovieRecommender
from Recommender.mysql import DBManager

rec_bp = Blueprint('rec_bp', __name__, url_prefix='/recommend')

config = {
        'emb_dim': 32,
        'weight_path': '../../ml-100k_sslpop.pt',
        'device': 'cuda',
        'model': 'mf',
        'seed': 10,
        'fix_seed': True,
    }


@rec_bp.route('/')
def root():
    return redirect(url_for('index_bp.index'))


@rec_bp.route('/<int:user_id>/<int:k>')
def recommend(user_id, k):
    recommender = MovieRecommender(config)
    db_manager = DBManager()

    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(db_manager.get_movie_info(movie_id))

    print(res)


if __name__ == '__main__':
    pass

