from flask import Flask
from flask_restful import Api,Resource,reqparse
import random
import string
import logging
import pymysql
import mysql
import time


log = logging.getLogger('Proxy_Api')
logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(message)s')


app = Flask(__name__)
api = Api(app)

def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str


def excecutemysql(ls,ret,sql,arg=None):
    error=1
    while error==1:
        try:
            connection=mysql.getConnection()
            error=0
        except pymysql.Error as e:
            log.error('Ошибка работы с БД: %s'%e)
            time.sleep(10)
    error=1
    while error==1:
        try:
            cursor = connection.cursor()
            if ls==0:
                if arg==None:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql,arg)
            if ls==1:
                cursor.executemany(sql,arg)
            if ret==2:
                answer=cursor.fetchall()
            if ret==1:
                answer=cursor.fetchone()
            connection.commit()
            error=0
        except pymysql.Error as e:
            if e.args[0]==0:
                log.error('Ошибка работы с БД: %s.sql: %s %s Пропускаю'%(e,sql,arg))
                error=0
                return
            if e.args[0]==1062:
                log.error('Дубликат в БД: %s. Пропускаю'%e)
                return 2            
            log.error('Ошибка работы с БД: %s.sql: %s'%(e,sql,arg))
            #connection.commit()
            time.sleep(1)
    connection.close()
    if ret==0: return 
    return answer

def checkdropchecker():
    sql="SELECT `unique` FROM `proxy`.`proxycheckers` WHERE (CURRENT_TIMESTAMP()-lastupdate)>6000;"
    answer=excecutemysql(0,2,sql)
    if answer!=None:
        coll=len(answer)
        log.info('Очищаю %s прокси демонов'%coll)
        while coll>=1:
            uniq=answer[coll-1]['unique']
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{uniq}';"
            excecutemysql(0,0,sql)
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{uniq}';"
            excecutemysql(0,0,sql)
            coll-=1
    return

class Societal(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("lim", type=int)
        params = parser.parse_args()
        sql="SELECT `ip`,`port` FROM `proxy`.`proxy` ORDER BY `status` DESC, `time` ASC LIMIT 100;"
        testbd=excecutemysql(0,2,sql)

        lim=params['lim']
        if (lim == 0)|(lim == 1)|(lim==None):
            ran=random.randint(0,len(testbd)-1)
            answrow=str(testbd[ran]['ip'])+':'+str(testbd[ran]['port'])
            return answrow, 200
        elif lim>100:
            lim=100
        # answer=''
        answer=[]
        maxbd=len(testbd)
        if lim>maxbd:
            lim=maxbd
        i=0
        while i<lim:
            answrow=str(testbd[i]['ip'])+':'+str(testbd[i]['port'])
            answer.append(answrow)
            i+=1
        return answer, 200
    

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("ip")
        parser.add_argument("port", type=int)
        params = parser.parse_args()
        ip=params['ip']
        port=params['port']
        sql='INSERT IGNORE INTO `proxy`.`proxy` (`ip`, `port`) VALUES (%s, %s);'
        excecutemysql(0,0,sql,(ip,port))
        quote = {
            "ip": params["ip"],
            "port": params["port"]
        }
        return quote, 201

class Checker(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("unique")
        parser.add_argument("reg", type=int)
        parser.add_argument("pass")
        parser.add_argument("ip")
        params = parser.parse_args()
        checkdropchecker()
        if (params['unique']!=None) and (params['reg']!=None) and (params['ip']!=None):
            if (params['reg']==0)and(params['pass']!=None):
                password=params['pass']
                sql=f"SELECT COUNT(*) FROM `proxy`.`proxycheckers` WHERE `unique`='{params['unique']}' AND `pass`='{password}';"
                sqlansw=excecutemysql(0,1,sql)
                if (sqlansw['COUNT(*)']==1):
                    hash=get_random_string(10)
                    sql=f"UPDATE `proxy`.`proxycheckers` SET `hash`='{hash}' WHERE `unique`='{params['unique']}';"
                    excecutemysql(0,0,sql)
                    sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{params['unique']}';"
                    excecutemysql(0,0,sql)
                    sql=f"UPDATE `proxy`.`proxy` SET `unique`='{params['unique']}' WHERE `error`=0 AND `del`=0 AND `unique` IS NULL ORDER BY `proverki` ASC LIMIT 100;"
                    excecutemysql(0,0,sql)
                    sql=f"SELECT `ip`,`port` FROM `proxy`.`proxy` WHERE `unique`='{params['unique']}';"
                    answer=excecutemysql(0,2,sql)
                    answer.append(password)
                    return answer, 200
                else:
                    answrow="Неверный уникальный ключ или пароль"
                    return answrow, 403
            elif (params['reg']==1):
                password=get_random_string(10)
                sql=f"INSERT into `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{params['ip']}','{params['unique']}','{password}');"
                excecutemysql(0,0,sql)
                sql=f"UPDATE `proxy`.`proxy` SET `unique`='{params['unique']}' WHERE `error`=0 AND `del`=0 AND `unique` IS NULL ORDER BY `proverki` ASC LIMIT 10;"
                excecutemysql(0,0,sql)
                sql=f"SELECT `ip`,`port` FROM `proxy`.`proxy` WHERE `unique`='{params['unique']}';"
                answer=excecutemysql(0,2,sql)
                answer.append(password)
                return answer, 200
        answrow="Доступ только для Чеккеров"
        return answrow, 403
    

    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("unique")
        parser.add_argument("pass")
        parser.add_argument("types")
        parser.add_argument("ip")
        parser.add_argument("port", type=int)
        parser.add_argument("type")
        parser.add_argument("time_response")
        parser.add_argument("anonymity")
        parser.add_argument("country_code")
        params = parser.parse_args()
        badsql="UPDATE `proxy`.`proxy` SET `proverki`=IF(`status`>=1,0,IF(ISNULL(`proverki`),1,`proverki`+1)),`status`=0,`unique`=NULL WHERE ip=%s AND port=%s;"
        errorsql="UPDATE `proxy`.`proxy` SET error=1,`unique`=NULL WHERE ip=%s AND port=%s;"
        goodsql='UPDATE `proxy`.`proxy` SET `proverki`=IF(`status`>=1,IF(ISNULL(`proverki`),1,`proverki`+1),`proverki`+1),`status`=1,`unique`=NULL,type="%s",time=%s,anonymity=%s,country_code=%s WHERE ip=%s AND port=%s;'
        if (params["unique"]!=None) and (params["pass"]!=None) and (params["types"]!=None) and (params["ip"]!=None) and (params["port"]!=None):
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxycheckers` WHERE `unique`='{params['unique']}' AND `pass`='{params['pass']}';"
            sqlansw=excecutemysql(0,1,sql)
            if (sqlansw['COUNT(*)']==1):
                sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `unique`='{params['unique']}' AND `ip`='{params['ip']}' AND `port`={params['port']};"
                sqlansw=excecutemysql(0,1,sql)
                if (sqlansw['COUNT(*)']==1):
                    if params["types"]=='bad':
                        excecutemysql(0,0,badsql,(params["ip"],params["port"]))
                        return params, 201
                    if params["types"]=='error':
                        excecutemysql(0,0,errorsql,(params["ip"],params["port"]))
                        return params, 201
                    if params["types"]=='good':
                        if (params['type']!=None) and (params["time_response"]!=None) and (params["anonymity"]!=None) and (params["country_code"]):
                            excecutemysql(0,0,goodsql,(params['type'],params["time_response"],params["anonymity"],params["country_code"],params["ip"],params["port"]))
                            return params, 201
        quote='ERROR Иди Нахуй'
        return quote, 404


    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument("unique")
        parser.add_argument("pass")
        params = parser.parse_args()
        if (params['unique']!=None) and (params['pass']!=None):
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxycheckers` WHERE `unique`='{params['unique']}' AND `pass`='{params['pass']}';"
            sqlansw=excecutemysql(0,1,sql)
            if (sqlansw['COUNT(*)']==1):
                sql="UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`=%s;"
                excecutemysql(0,0,sql,params['unique'])
                sql="DELETE FROM `proxy`.`proxycheckers` WHERE `unique`=%s;"
                excecutemysql(0,0,sql,params['unique'])                    
                return f"Proxy with id {params['unique']} is deleted.", 200
        answrow="Доступ только для Чеккеров"
        return answrow, 403


api.add_resource(Checker, "/checker","/checker/")
api.add_resource(Societal, "/","/proxy","/proxy/")
# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run(host='0.0.0.0')