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
        movie_ids : [ID_1, ID_2, ..., ID_n]
    """
    movie_list = []
    for i in range(k):
        movie_id = random.randint(1, 1682)
        movie_info = db_manager.get_movie_info(movie_id)
        movie_list.append(movie_info)

    return movie_list


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


@api_bp.route('/recommend/<int:k>')
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
    recommender = MovieRecommender(config)

    user_id = db_manager.get_curr_user_info()['user_id']
    rec_movie_ids = recommender.topk(user_id, k).tolist()

    res = []
    for movie_id in rec_movie_ids:
        res.append(db_manager.get_movie_info(movie_id))

    return jsonify(res)


@api_bp.route('/query_movie/<keyword>')
def query_movie(keyword):
    """ 根据电影名进行模糊查找

    Returns:
        movie_list : [ID_1, ID_2, ..., ID_n]
    """
    movie_df = db_manager.get_df_data('movie_info')

    res = movie_df[movie_df['movie_name'].str.contains(keyword)]
    if len(res) > 0:
        return jsonify(res['movie_id'].tolist())


def scrape_api(url):
    """ 爬取网页接口
    """
    logging.info(f'scraping {url}')
    try:
        session = requests.session()
        response = session.get(url, headers=headers)

        print('response:', response)
        if response.status_code == 200:
            return response
        logging.error(f'scraping {url} status code error')
    except requests.RequestException:
        logging.error(f'scraping {url} error')
        return None


@api_bp.route('/movie_info/<movie_id>')
def get_movie_info_from_imdb(movie_id):
    """ 根据电影ID从imdb.com实时获取电影的的详细信息

    Args:
        movie_id: The ID of movie

    Returns:
        movie_info: A dict likes
        {
            'rating': [movie rating, the number of rating number],
            'pop': [popularity, popularity trend, change value],
            'desc': the description of movie
        }
    """

    xpath_list = [
        '//*[@id="__next"]/main//div[@data-testid="hero-rating-bar__aggregate-rating"]',
        '//*[@id="__next"]/main//div[@data-testid="hero-rating-bar__popularity"]',
        '//*[@id="__next"]/main//div[@data-testid="hero-rating-bar__aggregate-rating__score"]',
        '//*[@id="__next"]/main//div[@data-testid="hero-rating-bar__popularity__score"]',
        '//*[@id="__next"]/main//div[@data-testid="hero-rating-bar__popularity__delta"]',
        '//*[@id="__next"]/main//span[@data-testid="plot-xl"]',
        '//*[@id="__next"]/main//li[@data-testid="title-pc-principal-credit"]/div/ul'
    ]

    try:
        res = {
            'rating': None,
            'pop': None,
            'desc': None,
            'director': None,
            'writer': None,
            'star': None
        }
        search_url = db_manager.get_movie_info(movie_id)['url']

        response = scrape_api(search_url)
        selector = etree.HTML(response.text)
        rating_elem = selector.xpath(xpath_list[0])
        pop_elem = selector.xpath(xpath_list[1])

        rating = selector.xpath(xpath_list[2])[0].xpath('./span[1]/text()')[0]
        rating_num = selector.xpath(xpath_list[2])[0].xpath('./following-sibling::*')[1].text

        res['rating'] = [rating, rating_num]

        desc = selector.xpath(xpath_list[5])[0].text
        res['desc'] = desc

        if len(pop_elem) > 0:
            pop = selector.xpath(xpath_list[3])[0].text
            trend = selector.xpath(xpath_list[4])[0]

            if trend.xpath('./svg/@id')[0] == 'iconContext-arrow-drop-up':
                up_or_down = 'up'
            else:
                up_or_down = 'down'

            change = trend.xpath('./text()')[0]

            res['pop'] = [pop, up_or_down, change]

        director = selector.xpath(xpath_list[6])[0].xpath('./li/a/text()')
        writer = selector.xpath(xpath_list[6])[1].xpath('./li/a/text()')
        star = selector.xpath(xpath_list[6])[2].xpath('./li/a/text()')
        res['director'] = director
        res['writer'] = writer
        res['star'] = star

        return res

    except Exception as e:
        print('get movie {} url error'.format(movie_id))
        print(e)
        return res


if __name__ == '__main__':
    get_movie_info_from_imdb(1)
