import requests
import pymysql
import mysql
import time
import logging
import uuid
import string
import random


URLApi="http://127.0.0.1:5000/"


myuuid=uuid.uuid4()
log = logging.getLogger('Proxy_Api_Tester')
logging.basicConfig(level=logging.INFO, format='%(relativeCreated)6d %(message)s')
terror=0


def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # print random string
    return result_str


#### Функции mysql
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



class toster:
###################################################
##########Тестирование социального режима##########
###################################################
##################МЕТОД GET########################
###################################################
###Тестирование на получение прокси без аттрибута лимита
    def test_societalget1():
        api_get = URLApi
        response = requests.get(api_get)
        if (response.status_code==200):
            return True
        else: 
            return False


###Тестирование на получение прокси при "0" аттрибуте лимита 
    def test_societalget1_1():
        api_get = URLApi+"?lim=0"
        response = requests.get(api_get)
        if (response.status_code==200):
            return True
        else: 
            return False    


###Тестирование на получение прокси при "1" аттрибуте лимита    
    def test_societalget1_2():
        api_get = URLApi+"?lim=1"
        response = requests.get(api_get)
        if (response.status_code==200):
            return True
        else: 
            return False


###Тестирование на получение прокси при "None" аттрибуте лимита
    def test_societalget1_3():
        api_get = URLApi+"?lim=None"
        response = requests.get(api_get)
        if (response.status_code==400):
            return True
        else: 
            return False    


###Тестирование на получение большего количества прокси чем разрешено     
    def test_societalget2():
        api_get = URLApi+"?lim=200"
        response = requests.get(api_get)
        if (response.status_code==200) and (len(response.json())==100):
            return True
        else: 
            return False


###Тестирование на получение определённого числа прокси
    def test_societalget3(lim=10):
        api_get = URLApi+"?lim="+str(lim)
        response = requests.get(api_get)
        if (response.status_code==200) and (len(response.json())==lim):
            return True
        else: 
            return False


###################################################
##################МЕТОД POST#######################
###################################################
###Тестирование на добавление уникального прокси
    def test_societalpost1(ip='255.255.255.255',port=8080):
        sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
        answer=excecutemysql(0,1,sql)
        if answer['COUNT(*)']==0:
            api_get = URLApi+f"?ip={ip}&port={port}"
            response = requests.post(api_get)
            if (response.status_code==201):
                sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                answer=excecutemysql(0,1,sql)
                if answer['COUNT(*)']==1:
                    sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
                    excecutemysql(0,0,sql)
                    return True
                else:
                    return False
            else: 
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            api_get = URLApi+f"?ip={ip}&port={port}"
            response = requests.post(api_get)
            if (response.status_code==201):
                sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                answer=excecutemysql(0,1,sql)
                if answer['COUNT(*)']==1:
                    sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
                    excecutemysql(0,0,sql)
                    return True
                else:
                    return False


###Тестирование на добавление дубликата
    def test_societalpost2(ip='255.255.255.255',port=8080):
        sql=f"INSERT IGNORE INTO `proxy`.`proxy` (`ip`, `port`) VALUES ('{ip}',{port});"
        excecutemysql(0,0,sql)
        sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
        answer=excecutemysql(0,1,sql)
        if answer['COUNT(*)']==1:
            api_get = URLApi+f"?ip={ip}&port={port}"
            response = requests.post(api_get)
            if (response.status_code==201):
                sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                answer=excecutemysql(0,1,sql)
                if answer['COUNT(*)']==1:
                    sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
                    excecutemysql(0,0,sql)
                    return True
                else:
                    sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
                    excecutemysql(0,0,sql)
                    return False
            else:
                sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxy` WHERE  `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            return False


###################################################
##############Тестирование API Чекера##############
###################################################
##################МЕТОД GET########################
###################################################
###Тестирование на регистрацию чекера
    def test_checkerget1(ip='255.255.255.255'):
        api_get = URLApi + f'checker/?unique={myuuid}&ip={ip}&reg=1'
        response = requests.get(api_get)
        if response.status_code==200:
            lenresp=len(response.json())-1
            password=response.json()[lenresp]
            answer=response.json()
            del answer[lenresp]
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxycheckers` WHERE `ip`='{ip}' AND `unique`='{myuuid}';"
            sqlansw=excecutemysql(0,1,sql)
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `unique`='{myuuid}';"
            sqlansw2=excecutemysql(0,1,sql)
            if (len(answer)==10) and (sqlansw['COUNT(*)']==1) and (sqlansw2['COUNT(*)']==10):
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                return True
            else:
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            return False


###Тестирование на повторный вход чекера с паролем
    def test_checkerget2(ip='255.255.255.255'):
        password=get_random_string(10)
        sql=f"INSERT into `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        api_get = URLApi + f'checker/?unique={myuuid}&ip={ip}&pass={password}&reg=0'
        response = requests.get(api_get)
        if (response.status_code==200) and (len(response.json())==101):
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            return True
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            return False


###Тестирование на повторный вход чекера с неправильным паролем
    def test_checkerget3(ip='255.255.255.255'):
        password=get_random_string(10)
        sql=f"INSERT into `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        password=get_random_string(10)
        api_get = URLApi + f'checker/?unique={myuuid}&ip={ip}&pass={password}&reg=0'
        response = requests.get(api_get)
        if (response.status_code==403):
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            return True
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"UPDATE `proxy`.`proxy` SET `unique`=NULL WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            return False


###################################################
##################МЕТОД PUT#######################
###################################################
###Тестирование на отправку проверенного "bad" прокси
    def test_checkerput1(ip='255.255.255.255', port=8080):
        password=get_random_string(10)
        sql=f"INSERT IGNORE INTO `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        sql=f"INSERT IGNORE INTO `proxy`.`proxy` (`ip`,`port`,`unique`) VALUES ('{ip}',{port},'{myuuid}');"
        excecutemysql(0,0,sql)
        api_get = URLApi + f'checker/?unique={myuuid}&pass={password}&types=bad&ip={ip}&port={port}'
        response = requests.put(api_get)
        if (response.status_code==201):
            sql=f"SELECT `proverki`,`status`,`unique` FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            answ=excecutemysql(0,1,sql)
            if (answ['proverki']==1)and(answ['status']==0)and(answ['unique']==None):
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return True
            else:
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            return False


###Тестирование на отправку проверенного "error" прокси
    def test_checkerput2(ip='255.255.255.255', port=8080):
        password=get_random_string(10)
        sql=f"INSERT IGNORE INTO `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        sql=f"INSERT IGNORE INTO `proxy`.`proxy` (`ip`,`port`,`unique`) VALUES ('{ip}',{port},'{myuuid}');"
        excecutemysql(0,0,sql)
        api_get = URLApi + f'checker/?unique={myuuid}&pass={password}&types=error&ip={ip}&port={port}'
        response = requests.put(api_get)
        if (response.status_code==201):
            sql=f"SELECT `error`,`unique` FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            answ=excecutemysql(0,1,sql)
            if (answ['error']==1)and(answ['unique']==None):
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return True
            else:
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            return False


###Тестирование на отправку проверенного "good" прокси
    def test_checkerput3(ip='255.255.255.255', port=8080,typs=('socks4','socks5'),times=0.322,anonim='Anonymous',CCo='UA'):
        password=get_random_string(10)
        sql=f"INSERT IGNORE INTO `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        sql=f"INSERT IGNORE INTO `proxy`.`proxy` (`ip`,`port`,`unique`) VALUES ('{ip}',{port},'{myuuid}');"
        excecutemysql(0,0,sql)
        api_get = URLApi + f'checker/?unique={myuuid}&pass={password}&types=good&ip={ip}&port={port}&type={typs}&time_response={times}&anonymity={anonim}&country_code={CCo}'
        response = requests.put(api_get)
        if (response.status_code==201):
            sql=f"SELECT * FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            answ=excecutemysql(0,1,sql)
            if (answ['proverki']==None)and(answ['status']==1)and(answ['time']==times)and(answ['anonymity']==anonim)and(answ['country_code']==CCo)and(answ['error']==0)and(answ['unique']==None):
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return True
            else:
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            return False


###################################################
################МЕТОД DELETE#######################
###################################################
###Тестирование на удаление данных чекера
    def test_checkerdelete1(ip='255.255.255.255', port=8080):
        password=get_random_string(10)
        sql=f"INSERT IGNORE INTO `proxy`.`proxycheckers` (`ip`,`unique`,`pass`) VALUES ('{ip}','{myuuid}','{password}');"
        excecutemysql(0,0,sql)
        sql=f"INSERT IGNORE INTO `proxy`.`proxy` (`ip`,`port`,`unique`) VALUES ('{ip}',{port},'{myuuid}');"
        excecutemysql(0,0,sql)
        api_get = URLApi + f'checker/?unique={myuuid}&pass={password}'
        response = requests.delete(api_get)
        if (response.status_code==200):
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxy` WHERE `unique`='{myuuid}';"
            answ=excecutemysql(0,1,sql)
            sql=f"SELECT COUNT(*) FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            answ2=excecutemysql(0,1,sql)
            if (answ['COUNT(*)']==0)and(answ2['COUNT(*)']==0):
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return True
            else:
                sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
                excecutemysql(0,0,sql)
                sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
                excecutemysql(0,0,sql)
                return False
        else:
            sql=f"DELETE FROM `proxy`.`proxycheckers` WHERE `unique`='{myuuid}';"
            excecutemysql(0,0,sql)
            sql=f"DELETE FROM `proxy`.`proxy` WHERE `ip`='{ip}' AND `port`={port};"
            excecutemysql(0,0,sql)
            return False


###################################################
################Полная проверка####################
###################################################
    def runalltest():
        log.info('Тестирование социального режима...')
        log.info('Тестирование метода Get...')
        temp='Тестирование на получение прокси без аттрибута лимита'
        if toster.test_societalget1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на получение прокси при "0" аттрибуте лимита'
        if toster.test_societalget1_1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1 
        temp='Тестирование на получение прокси при "1" аттрибуте лимита'
        if toster.test_societalget1_2()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на получение прокси при "None" аттрибуте лимита'
        if toster.test_societalget1_3()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на получение большего количества прокси чем разрешено'
        if toster.test_societalget2()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на получение определённого числа прокси'
        if toster.test_societalget3()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        log.info('Тестирование метода Get: Пройдено')
        log.info('Тестирование метода Post...')
        temp='Тестирование на добавление уникального прокси'
        if toster.test_societalpost1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на добавление дубликата'
        if toster.test_societalpost2()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        log.info('Тестирование метода Post: Пройдено')
        log.info('Тестирование социального режима: Пройдено')
        log.info('Тестирование API чекера...')
        log.info('Тестирование метода Get...')
        temp='Тестирование на регистрацию чекера'
        if toster.test_checkerget1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на повторный вход чекера с паролем'
        if toster.test_checkerget2()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на повторный вход чекера с неправильным паролем'
        if toster.test_checkerget3()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        log.info('Тестирование метода Get: Пройдено')
        log.info('Тестирование метода Put...')
        temp='Тестирование на отправку проверенного "bad" прокси'
        if toster.test_checkerput1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на отправку проверенного "error" прокси'
        if toster.test_checkerput2()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        temp='Тестирование на отправку проверенного "good" прокси'
        if toster.test_checkerput3()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        log.info('Тестирование метода Put: Пройдено')
        log.info('Тестирование метода Delete...')
        temp='Тестирование на удаление данных чекера'
        if toster.test_checkerdelete1()==True:
            temp+=': Пройдено'
            log.info(temp)
        else:
            temp+=': Провалено'
            terror=1
            log.error(temp)
            return 1
        log.info('Тестирование метода Delete: Пройдено')
        log.info('Тестирование API чекера: Пройдено')
        log.info('API Успешно протестировано')
        return 0


if __name__ == '__main__':
    if toster.runalltest()==1:
        raise SystemExit(1)
    else: exit(0)