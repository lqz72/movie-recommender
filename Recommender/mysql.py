# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import pymysql
import configparser
import os
import time


class DBManager(object):
    """ MySQL database interface """

    def __init__(self):
        self.root_dir = os.path.abspath(os.path.dirname(__file__)).split('Recommender')[0]
        self.db_name = 'mysql'

    def get_db_config(self):
        """ Get database configure
        """
        cf = configparser.ConfigParser()
        cf.read('{}/{}.conf'.format(self.root_dir, self.db_name), encoding='utf-8')

        config = {
            'host': cf.get('Default', 'DB_HOST'),
            'port': cf.getint('Default', 'DB_PORT'),
            'user': cf.get('Default', 'DB_USER'),
            'passwd': cf.get('Default', 'DB_PASSWD'),
            'db': cf.get('Default', 'DB_NAME'),
            'charset': 'utf8mb4',
        }

        return config

    def connect_to_db(self):
        # 远程数据库连接
        # conn = MySQLdb.connect(host='118.178.88.14', port=3306, user='lqz',
        # passwd='863JTcyPGezGEXmm', db='lqz', charset='utf8mb4')

        # 本地数据库连接
        config = self.get_db_config()
        conn = pymysql.connect(**config)

        return conn

    def get_df_data(self, table_name):
        """ Return table as DataFrame form
        """
        conn = self.connect_to_db()

        try:
            print('正在读取%s中的数据' % table_name)
            start = time.time()

            sql = 'SELECT * FROM %s' % table_name
            df = pd.read_sql(sql, con=conn)

            end = time.time()
            print('读取时间:', end - start)
            return df

        except Exception as e:
            conn.rollback()
            print('error', e)
        finally:
            conn.close()

    def get_user_info(self, user_id):
        """ Query user info by user id
        """
        conn = self.connect_to_db()

        try:
            sql = 'SELECT * from user_info WHERE `user_id` = "%s"' % user_id
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            if len(data) > 0:
                return {
                    'user_id': data[0][0],
                    'age': data[0][1],
                    'gender': data[0][2],
                    'occupation': data[0][3]
                }

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()

        return 'UnKnow'

    def get_specific_user_pwd(self, username):
        """ Query user password by username
        """
        conn = self.connect_to_db()

        try:
            sql = 'SELECT pwd from user_login_info WHERE `username` = "%s"' % username
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            if len(data) > 0:
                return {
                    'pwd': data[0][0]
                }

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()

        return 'UnKnow'

    def get_movie_info(self, movie_id):
        """ Query movie info by movie id
        """
        conn = self.connect_to_db()

        try:
            sql = 'SELECT * from movie_info WHERE `movie_id` = "%s"' % movie_id
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            if len(data) > 0:
                return {
                    'movie_id': data[0][0],
                    'movie_name': data[0][1].split('(')[0],
                    'date': data[0][2],
                    'url': data[0][3],
                    'class': data[0][4].split('|'),
                    'rating': data[0][5].split('|'),
                    'pop': data[0][6].split('|'),
                    'desc': data[0][7],
                    'director': data[0][8].split('|'),
                    'writer': data[0][9].split('|'),
                    'star': data[0][10].split('|'),
                }

        except Exception as e:
            print('error:', e)
            print(movie_id)
            conn.rollback()
            conn.close()

        return 'UnKnow'

    def add_curr_user2db(self, user_id, user_type):
        """ Add current user information to database
        """
        conn = self.connect_to_db()
        try:
            sql = 'SELECT * from curr_user_info'
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()

            if len(data) > 0:
                old_user_id = data[0][0]
                print(old_user_id)
                sql = 'UPDATE curr_user_info SET `user_id` = "%s",`user_type` = "%s" WHERE `user_id` = "%s"' % (user_id, user_type, old_user_id)
            else:
                sql = 'INSERT INTO curr_user_info VALUES ("%s", "%s")' % (user_id, user_type)

            cursor.execute(sql)
            conn.commit()
            conn.close()
            return 'Success'

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()
        return 'UnKnow'

    def get_curr_user_info(self):
        """ Get current user information from database
        """
        conn = self.connect_to_db()
        try:
            sql = 'SELECT * from curr_user_info'
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.close()

            if len(data) > 0:
                return {
                    'user_id': data[0][0],
                    'user_type': data[0][1]
                }

        except Exception as e:
            print('error:', e)
            conn.rollback()
            conn.close()
        return 'UnKnow'


if __name__ == '__main__':
    manager = DBManager()
    movie_df = manager.get_df_data('movie_info')
    keyword = 'Casper'

    res = movie_df[movie_df['movie_name'].str.contains(keyword)]
    if len(res) > 0:
        print(res['movie_id'].values[0])
    # print(res)