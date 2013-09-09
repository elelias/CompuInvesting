#maketsim.py
#function for the first quizz:
import sys

# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import copy
from simulate import *
from eventProfiler import *
from marketsim import *



def AddOrder(num,date,symbol,action,size,dfOrders):

    '''builds an order, which is a series object'''
    
    #if an event is found, buy 100 shares 
    # sell them after 5 days
    series=pd.Series([symbol,action,size,date],index=['symbol','order','size','mydate'] ,name=num)
    newdict={}
    newdict['symbol']=pd.Series(symbol,index=[num])
    newdict['order']=pd.Series(action,index=[num])
    newdict['size']=pd.Series(size,index=[num])
    newdict['mydate']=pd.Series(date,index=[num])
    newFrame=pd.DataFrame(newdict)
            
    #print 'the series is ',series
    
    dfOrders=dfOrders.append(newFrame)
    #print dfOrders
    #raw_input('')    
    return dfOrders
    #pass

def initializeOrders():
    
    #df=pd.DataFrame(columns=['symbol','order','size','mydate'])
    myd={}
    myd['symbol']=pd.Series([0],index=[0])
    myd['order']=pd.Series('nothing',index=[0])
    myd['size']=pd.Series([0],index=[0])    
    myd['mydate']=pd.Series(dt.datetime(1981,2,1),index=[0])
    df=pd.DataFrame(myd)
    return df

def getOrdersFromStrategy(dt_start,dt_end):

    '''applies a strategy'''
    

    ls_name='sp5002012'
    StockQuantity=100

    #INITIALIZE THE ORDERS DATA FRAME
    dfOrders=initializeOrders()
    #
    #
    #print 'before getEvents'
    #GET THE EVENTS
    dfEvents,d_data=getEvents(dt_start,dt_end,ls_name)

    
    #valid trading days
    dt_timeofday = dt.timedelta(hours=16)
    listdays = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    #
    #
    #CONSTRUCT THE ORDERS WHEN AN EVENT IS FOUND
    nfound=0
    orderNum=0
    print 'before loop'
    for idx,series in dfEvents.iterrows():
        for sym,value in series.iteritems():
            #print 'progress? ',idx,sym,value
            if value==1:
                nfound+=1
                #
                #
                #==BUILD THE ORDERS
                orderNum+=1
                dfOrders=AddOrder(orderNum,idx,sym,'Buy',StockQuantity,dfOrders)
                #
                #
                #sellDate=idx+dt.timedelta(5)
                #count five days
                for ind,date in enumerate(listdays):
                    if date==idx:
                        
                        if ind+6<=len(listdays):
                            sellDate=listdays[ind+5]

                        else :
                            sellDate=dt_end
                        #
                    #
                #
                #
                
                orderNum+=1
                dfOrders=AddOrder(orderNum,sellDate,sym,'Sell',StockQuantity,dfOrders)


    dfOrders=dfOrders[1:]
    dfSorted=dfOrders.sort('mydate')
    return dfOrders



    #print 'here I find ',nfound
if __name__=='__main__':


    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    dfOrders=getOrdersFromStrategy(dt_start,dt_end)
    #print 'head' 
    #print dfOrders.head()
    
    startingCash=50000
    benchmarkSym='$SPX'
    marketSimulation(dt_start,dt_end,startingCash,benchmarkSym,dfOrders)
