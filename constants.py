""" 
All constants are maintained in this sscript  

"""

ANAPLAN_USR = "Enter anaplan username"
ANAPLAN_PASS = "Enter anaplan password"
SLACK_WEBHOOK = "Enter slack webhook URL here . you can get this frfo slack please refer to instructions document"
SQL_DBNAME = "This will be the db name this script will create enter in this format dbname.db"

'''
This flag controls the slack flag mode in latestrun table . You dont want script posting failed results again and again therefore evertime a post occurs database flag is updated
However during testing you would want posts to occur evertime you run the script . 
This flag controls that . If its set to true then post will occur everytime script runs if set to flase it will occur 1 time
'''
TESTING_MODE = "true or false"
                


sql_Create_Integration_Table = """ CREATE TABLE IF NOT EXISTs integration(
                                integrationId TEXT PRIMARY KEY,
                                name text
                                );"""

sql_Create_latestRun_Table = """ CREATE TABLE IF NOT EXISTs latestRun(
                                integrationId TEXT NOT Null,
                                startDate text NOT NULL,
                                endDate text NOT NULL,
                                triggeredBy text,
                                success INTEGER,
                                message TEXT,
                                executionErrorCode INTEGER,
                                senttoslackFlag INTEGER default 0,
                                FOREIGN KEY (integrationId) REFERENCES integration (integrationId),
                                PRIMARY KEY (integrationId,startDate,endDate)
                                );"""
