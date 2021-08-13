'''
This is the main file which runs and calls all functions.
All functions are defined in functions.py
All constants are specified in constants.py

'''

import constants as cons
import functions as anaplan
import schedule
import time

#This function contains the flow logic . It calls functions from function.py in order highlighted below
def run():
    
    """  
    Create and initialise sqlite  database . Please note that SQLlite database is only for 
    This version of the script . In production environment you can use whatever database 
    
    """

    conn = anaplan.createDBconnection(cons.SQL_DBNAME)

    """ 
    Below creates 2 tabels in your sql lite databse 
    Integartion table holds integration ID and Name 
    lastest run table holds latest run related to the integartions  
    
    """

    if conn is not None:
        # create projects table
        print('->Creating table integration....')
        anaplan.create_table(conn, cons.sql_Create_Integration_Table)

        print('->Creating table latest result...')
        anaplan.create_table(conn,cons.sql_Create_latestRun_Table)

    else:
        print("Error! cannot create the database connection.")

    """ Get Anaplan Token """

    token = anaplan.getToken()
    
    """ Get integartions from cloudworks API """

    integrations = anaplan.getIntegrations(token)
   

    """ 

    Below Code filters the latest result and add records to integration table and latest run table 
    
    """

    integrations = [a for a in integrations['integrations'] if a['latestRun']['executionErrorCode'] != None]
    

    
    for i in integrations :
        print('->Saving results to Integrations table')
        anaplan.insertintoIntegration(conn,(i['integrationId'],i['name']))

        print('->Saving results to Latest run table')
        anaplan.insertintolatestrun(conn,(i['integrationId'],i['latestRun']['startDate'],
                                                    i['latestRun']['endDate'],i['latestRun']['triggeredBy'],
                                                    i['latestRun']['success'],i['latestRun']['message'],
                                                    i['latestRun']['executionErrorCode']))

    
    """ below code posts message to Slack """
    status = anaplan.postSlackMessage(conn)
    
    """ If message is posted and successful  """
    if status == 200:
        print('->Updating table')
        anaplan.updateslackflag(conn)
        print('\n---end---')
    else:
        print('->Nothing new to post \n-- end---')

    """ 
    Below function resets the slack flag to 0 
    This can be used while testing scripts testing the script
    Flag to turn on and off is manintained in constant script

    """
    if cons.TESTING_MODE == True:
        print('->Testing mode on')
        anaplan.resetslackflag_testing(conn)

#Main function call
if __name__ == '__main__':
    
    run()