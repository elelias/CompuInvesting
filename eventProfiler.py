'''
(c) 2011, 2012 Georgia Tech Research Corporation
This source code is released under the New BSD license.  Please see
http://wiki.quantsoftware.org/index.php?title=QSTK_License
for license details.

Created on January, 23, 2013

@author: Sourabh Bajaj
@contact: sourabhbajaj@gatech.edu
@summary: Event Profiler Tutorial
'''

import sys
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

"""
Accepts a list of symbols along with start and end date
Returns the Event Matrix which is a pandas Datamatrix
Event matrix has the following structure :
    |IBM |GOOG|XOM |MSFT| GS | JP |
(d1)|nan |nan | 1  |nan |nan | 1  |
(d2)|nan | 1  |nan |nan |nan |nan |
(d3)| 1  |nan | 1  |nan | 1  |nan |
(d4)|nan |  1 |nan | 1  |nan |nan |
...................................
...................................
Also, d1 = start date
nan = no information about any event.
1 = status bit(positively confirms the event occurence)
"""


def findEvents(ls_symbols, d_data):
    ''' Finding the event dataframe '''
    df_close = d_data['actual_close']
    ts_market = df_close['SPY']

    print "Finding Events"

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    
    n_eventsfound=0

    print 'the last date in the loop is ',ldt_timestamps[-1]

    for i in range(1, len(ldt_timestamps)):
        if ldt_timestamps[i]> dt.datetime(2009, 12, 15, 16, 0):
            print 'today we are trading ',ldt_timestamps[i]
        for s_sym in ls_symbols:
            


            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            f_marketprice_today = ts_market.ix[ldt_timestamps[i]]
            f_marketprice_yest = ts_market.ix[ldt_timestamps[i - 1]]
            f_symreturn_today = (f_symprice_today / f_symprice_yest) - 1
            f_marketreturn_today = (f_marketprice_today / f_marketprice_yest) - 1

            # Event is found if the price is below 5$ and the day before was above>5
            if ldt_timestamps[i]==dt.datetime(2009, 12, 28, 16, 0):
                pass
                #print 'in ',s_sym
                #print f_symprice_today, f_symprice_yest
            if f_symprice_today< 10 and f_symprice_yest >=10:
                #print 'found an event! '
                
            #if f_symreturn_today <= -0.03 and f_marketreturn_today >= 0.02:
                df_events[s_sym].ix[ldt_timestamps[i]] = 1
                #print 'the event was found on date ',ldt_timestamps[i], 'with ',f_symprice_today,f_symprice_yest,s_sym
                #create an order
                #createOrder(s_sym,ldt_timestamps[i])
                
                n_eventsfound+=1
                
            else:
                df_events[s_sym].ix[ldt_timestamps[i]] = 0
            #
            #
            #
            # Event is found if the symbol is down more then 3% while the
            # market is up more then 2%
            #
            #    df_events[s_sym].ix[ldt_timestamps[i]] = 1

    print 'I found ',n_eventsfound, ' events'
    return df_events



def getData(dt_start,dt_end,ls_name):
    # 1st Jan,2008 to 31st Dec, 2009.
    #dt_start = dt.datetime(2008, 1, 1)
    #dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')

    #
    #ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols = dataobj.get_symbols_from_list(ls_name)
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    #remove nan
    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method = 'ffill')
        d_data[s_key] = d_data[s_key].fillna(method = 'bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)



    return d_data,ls_symbols



def getEvents(dt_start,dt_end,ls_name):
    d_data,ls_symbols=getData(dt_start,dt_end,ls_name)
    print 'got the data'
    df_events = findEvents(ls_symbols, d_data)        
    print 'got the events'
    return df_events,d_data

if __name__ == '__main__':


    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)

    typedata=sys.argv[1]
    if typedata=='2008':
        ls_name='sp5002008'
    elif typedata=='2012':
        ls_name='sp5002012'
    else:
        print 'unknown data'

    df_events,d_data =getEvents(dt_start,dt_end,ls_name)

       
    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,s_filename=ls_name+'.pdf', b_market_neutral=True, b_errorbars=True,s_market_sym='SPY')
    print "Creating Study"
    print df_events.head()
