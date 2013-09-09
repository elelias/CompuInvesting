
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


def Compute(close_norm,allocations):
    #normalized value of portfolio
    np_alloc=np.array(allocations)
    valuePortfolio=np.dot(close_norm,np_alloc)
    print 'valuePortolio = ',valuePortfolio
    #print 'normalized valuePortfolio ',valuePortfolio
    
    #daily returns of the PF
    daily_Portfolio=valuePortfolio.copy()
    tsu.returnize0(daily_Portfolio)
    print 'valuePortolio afer returnize= ',valuePortfolio    

    #calculate the quantities
    avg_P=np.average(daily_Portfolio) 
    sigma_P=np.std(daily_Portfolio) 
    sharpe_P=np.sqrt(252)*avg_P/sigma_P    
    cum_P=valuePortfolio[valuePortfolio.size -1]

    return sigma_P,avg_P,sharpe_P,cum_P




def GetNormalizedReturn(dt_start,dt_end, symbols,c_dataobj):
    #
    #

    #
    # Keys to be read from the data, it is good to read everything in one go.
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']

    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Timestamps and symbols are the ones that were specified before.
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    
    #normalized returns data frame
    df_rets=d_data['close'].copy()

    close=df_rets.values
    #normalized returns
    close_norm=close/close[0,:]

    #print 'close norm = ',close_norm.shape

    return close_norm


def simulate(dt_start,dt_end, symbols, allocations):


    #==========check allocations:
    sum_alloc=0
    for all in allocations:
        sum_alloc+=all
    #
    if sum_alloc != 1.0:
        print 'the allocations are wrong!'
        sys.exit(1)

    if len(allocations)!=len(symbols):
        print 'the sizes are different!'
        sys.exit(1)

    #=========construct the portfolio
    portfolio=zip(symbols,allocations)
    print 'portfolio = ',portfolio

    #check for bad symbols
    #
    c_dataobj=da.DataAccess('Yahoo')
    ls_all_syms = c_dataobj.get_all_symbols()
    # Bad symbols are symbols present in portfolio but not in all syms
    ls_bad_syms = list(set(symbols) - set(ls_all_syms))
    if len(ls_bad_syms) != 0:
        print "Portfolio contains bad symbols : ", ls_bad_syms
        sys.exit(1)
    #
    #
    
    
    close_norm=GetNormalizedReturn(dt_start,dt_end, symbols,c_dataobj)

    #optimize!
    sharpe_max=-1
    step=0.1
    for a in range(0,11):
        for b in range (0,11-a):
            for c in range(0,11-a-b):
                d=10-a-b-c
                alloc_a=a*step
                alloc_b=b*step
                alloc_c=c*step
                alloc_d=d*step
                allocations=[alloc_a,alloc_b,alloc_c,alloc_d]
                vol,daily,sharpe,cumul=Compute(close_norm,allocations)
                #print 'sharpe =',sharpe
                if sharpe>sharpe_max:
                    sharpe_max=sharpe
                    best_alloc=allocations
                #print alloc_a,alloc_b,alloc_c,alloc_d
                #raw_input('hey')
                #
            #
        #
    #
    print 'the best sharpe is = ',sharpe_max
    print 'with the allocation =',best_alloc

#                vol,daily,sharpe,cumul=Compute(close_norm,allocations)
    
    
    #return vol,daily,sharpe,cumul



if __name__=='__main__':
    
    # List of symbols
    ls_symbols=['BRCM', 'TXN', 'IBM', 'HNZ'] 
    #ls_symbols=['C', 'GS', 'IBM', 'HNZ'] 
    #ls_symbols=['BRCM', 'TXN', 'IBM', 'HNZ'] 
    #ls_symbols=['GOOG', 'AAPL', 'GLD', 'XOM']
    #ls_symbols=['AXP', 'HPQ', 'IBM', 'HNZ']
    #ls_symbols=['AAPL', 'GLD', 'GOOG', 'XOM']
    #ls_symbols = ["AAPL", "GLD", "GOOG", "$SPX", "XOM"]

    # Start and End date of the charts
    dt_start = dt.datetime(2010, 1, 1)
    dt_end = dt.datetime(2010, 12, 31)    
    ls_allocations=(0.4,0.4,0.0,0.2)
    #vol,daily,sharpe,cumul=simulate(dt_start,dt_end,ls_symbols,ls_allocations)
    simulate(dt_start,dt_end,ls_symbols,ls_allocations)

    #print 'volatility= ',vol
    #print 'avg daily ret =',daily
    #print 'sharpe ratio = ',sharpe
    #print 'cumulative return =',cumul



