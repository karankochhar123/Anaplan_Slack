'''
This file contains all the functions required by main program

'''
import constants as cons
import requests
import json
from base64 import b64encode
import sqlite3
from sqlite3 import Error

""" Function to authenticate ( Basic ) and getting token value  """

def getToken():
    username = cons.ANAPLAN_USR
    password = cons.ANAPLAN_PASS
    
    header_string = { 'Authorization':'Basic ' + b64encode((username + ":" + password).encode('utf-8')).decode('utf-8') }
    anaplan_url='https://auth.anaplan.com/token/authenticate'

    print('->Getting Token.....')

    r=requests.post(anaplan_url, headers=header_string)

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error: " + str(e))
        exit()

    print("->Token generated")
    resp_dict = json.loads(r.text)
    return resp_dict['tokenInfo']['tokenValue']
    
""" Function to get integrations  """

def getIntegrations(t):

    print('->Getting cloudworks integartions....')
    url = 'https://api.cloudworks.anaplan.com/1/0/integrations'
    header = {'Authorization': 'AnaplanAuthToken ' + t,'Content-Type': 'application/json'}
    r=requests.get(url,headers=header)
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error: " + str(e))
        exit()

    return r.json()

""" Function to create DB connection """

def createDBconnection(database):
    print('->Initialising database...')
    conn = None
    try:
        conn = sqlite3.connect(database)
    except Error as e:
        print(e)
    print('->Databse initialised,connection esatblished')
    return conn

""" Function to create table  """

def create_table(conn, create_table_sql):
    
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
    
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")

    print('->Table created if doesnt exist')

""" Function to insert into tables """

def insertintoIntegration(conn,data):

    sql = ''' INSERT OR REPLACE INTO integration(integrationId,name)
              VALUES(?,?) '''

    try:
        c = conn.cursor()
        c.execute(sql,data)
        conn.commit()
        print('->Records updated in integration table')
        return c.lastrowid
    except Error as e:
        print(e)

def insertintolatestrun(conn,data):

    sql = ''' INSERT OR IGNORE INTO latestrun(integrationid,startDate,endDate,triggeredBy,success,message,executionErrorCode)
              VALUES(?,?,?,?,?,?,?) '''

    try:
        c = conn.cursor()
        c.execute(sql,data)
        print('->Records updated in Latest run table')
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(e)

 
""" Function to update slack flag"""

def updateslackflag(conn):
    c=conn.cursor()
    c.execute('''update latestRun set senttoslackFlag = 1 where senttoslackFlag =0''')
    print("->Rows updated")
    conn.commit()

def resetslackflag_testing(conn):
    c=conn.cursor()
    c.execute("update latestRun set senttoslackFlag = 0")
    print("->Rows updated")
    conn.commit()

""" Function to form slack message and post  """

def postSlackMessage(conn):
    
    c = conn.cursor()
    
    result = c.execute('select integration.name,success,message from latestRun inner join integration on integration.integrationId=latestrun.integrationId where senttoslackFlag = 0')
    
         
    payload = {'blocks':[]}
    tmplist = []

    for r in result.fetchall():
        print(r[0])
        temp = {}
        content = {}
        temp  = {
                            "type" : "section",
                            "text" : ""
            }
        content['type']='mrkdwn'
        content['text'] = "INT *{name}* generated *{status}* with message *{message}*.".format(name=r[0],status = ("warning :Warning:" if r[1] == 1 else "error :X:"),message=r[2])
        temp['text'] = content
        tmplist.append(temp)

    payload['blocks'] = tmplist 
    
    r=requests.post(cons.SLACK_WEBHOOK,json.dumps(payload))
    
    return r.status_code