import pymysql.cursors
import os


def getConnection(): 

    connection = pymysql.connect(host=os.environ.get('mysql_host'),
                                 port=os.environ.get('mysql_port'),
                                 user=os.environ.get('mysql_user'),
                                 password=os.environ.get('mysql_pass'),                             
                                 db=os.environ.get('mysql_bd'),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    return connection
