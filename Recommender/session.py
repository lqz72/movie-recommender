import multiprocessing
import random, os, sys
import requests
import logging
import pandas as pd
from lxml import etree

from Recommender.mysql import DBManager

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;474, Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'X-Request-With': 'XMLHttpRequest',
}

db_manager = DBManager()


def scrape_api(url):
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


def spider(movie_id):
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


def main(movie_ids):
    # 设置日志格式
    logging.basicConfig(level=logging.INFO)

    movie_info = []
    for id in movie_ids:
        res = spider(id)
        curr_movie_info = [id]
        for key, value in res.items():
            if isinstance(value, list):
                value = '|'.join(value)

            curr_movie_info.append(value)

        movie_info.append(curr_movie_info)
        logging.info(f'成功获取电影信息, 当前进度{id}/1682')

    movie_df = pd.DataFrame(movie_info, columns=['id', 'rating', 'pop', 'desc', 'director', 'writer', 'star'])
    print(movie_df)
    # movie_df.to_csv('./imdb_info.csv', index=0, encoding='utf-8')


if __name__ == '__main__':
    movies_id = [59]
    main(movies_id)
    print('end')