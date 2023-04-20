import os
from sys import path
from flask import Flask
from flask import flash, redirect, url_for
from flask import request, session

path.append('..')
path.append(os.path.abspath(os.path.dirname(__file__)).split('apps')[0])
path.append(os.path.abspath(os.path.dirname(__file__)).split('apps')[0] + 'apps\\')
path.append(os.path.abspath(os.path.dirname(__file__)).split('Flask')[0] + 'Recommender\\')

from Flask import settings
from login_view import login_bp
from index_view import index_bp
from api_view import api_bp
from movie_view import movie_bp
from rec_view import rec_bp


def create_app():
    """创建一个web应用程序
    """
    app = Flask(__name__)
    app.static_folder = '../static'
    app.template_folder = '../templates'
    app.config.from_object(settings)

    app.register_blueprint(login_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(rec_bp)

    @app.before_request
    def my_before_request():
        require_login_path = ['', 'index', 'recommend', 'movie']
        url_head = request.path.split('/')[1]

        if url_head in require_login_path:
            utype = session.get('utype', None)
            if not utype:
                flash("您还没有登录账号！")
                return redirect(url_for('login_bp.login'))

    return app
