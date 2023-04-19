# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import configparser
from sqlalchemy import create_engine


def inter2csv():
    file_name = './dataset/ml-100k/u.data'
    inter = []
    with open(file_name, 'r') as fn:
        lines = fn.readlines()

        for line in lines[:]:
            u, i, r, t = line.split('\t')[:4]
            u, i, r, t = int(u), int(i), int(r), int(t)
            inter.append([u,i, r, t])

    df = pd.DataFrame(np.array(inter), columns=['user_id', 'item_id', 'rating', 'timestamp'])
    df['timestamp'].astype('long')
    df = df.sort_values(by=['user_id', 'item_id'])
    df.set_index(np.arange(df.shape[0]), inplace=True)
    df.to_csv('./rating.csv', encoding='utf-8', index=0)


def user2csv():
    file_path = './dataset/ml-100k/u.user'
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        item_list = []
        for item in f.readlines():
            sp = item.strip().split('|')

            item_info = [sp[0], sp[1], sp[2], sp[3]]

            item_list.append(item_info)
    df = pd.DataFrame(item_list, columns=['user_id', 'age', 'gender', 'occupation'])
    print(df)
    df.to_csv('./user_info.csv', index=0, encoding='utf-8')


def movie2csv():
    movie_class_dict = {
        '0': 'unknown', '1': 'Action', '2': 'Adventure', '3': 'Animation', '4': "Children's", '5': 'Comedy',
        '6': 'Crime',
        '7': 'Documentary', '8': 'Drama', '9': 'Fantasy', '10': 'Film-Noir', '11': 'Horror', '12': 'Musical',
        '13': 'Mystery', '14': 'Romance', '15': 'Sci-Fi', '16': 'Thriller', '17': 'War', '18': 'Western'
    }
    movie_class_list = ['unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 'Documentary', 'Drama',
                   'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']

    import re

    file_path = './dataset/ml-100k/u.item'
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        item_list = []
        for item in f.readlines():
            sp = item.strip().split('|')
            s = ''.join(sp[5:-1])
            class_index = [i.start() for i in re.finditer('1', s)]
            movie_class = ""
            for idx in class_index:
                movie_class += "|" + movie_class_list[idx]

            item_info = [sp[0], sp[1], sp[2], sp[4], movie_class[1:]]

            item_list.append(item_info)
    df = pd.DataFrame(item_list, columns=['movie_id', 'movie_name', 'date', 'url', 'class'])
    print(df)
    df.to_csv('./movie_info.csv', index=0, encoding='utf-8')


def csv2db():
    cf = configparser.ConfigParser()
    cf.read('./mysql.conf', encoding='utf-8')
    config = {
        'host': cf.get('Default', 'DB_HOST'),
        'port': cf.getint('Default', 'DB_PORT'),
        'user': cf.get('Default', 'DB_USER'),
        'passwd': cf.get('Default', 'DB_PASSWD'),
        'db': cf.get('Default', 'DB_NAME'),
        'charset': 'utf8mb4',
    }

    csv_path = 'dataset/merged_movie_info.csv'
    data = pd.read_csv(csv_path, encoding='utf-8')

    engine = create_engine("mysql+pymysql://{}:{}@{}:{}/{}?charset={}".format(
        config['user'], config['passwd'], config['host'], config['port'], config['db'], config['charset']
    ))

    data.to_sql(name='movie_info', con=engine, if_exists='append', index=False, index_label=False)


if __name__ == '__main__':
    # user2csv()
    # movie2csv()
    # csv2db()
    pass

