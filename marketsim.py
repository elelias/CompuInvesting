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

def parseArgs(args):

    startingCash=args[1]
    orderFile=args[2]
    valuesFile=args[3]
    benchmarkSym=args[4]

    return startingCash,orderFile,valuesFile,benchmarkSym

def getDataFromYahoo():

    c_dataobj=da.DataAccess('Yahoo')
    ls_all_syms = c_dataobj.get_all_symbols()    


def loadData(ls_keys,symbols,dt_start,dt_end):

    c_dataobj=da.DataAccess('Yahoo')
    ls_all_syms = c_dataobj.get_all_symbols()    
    # We need closing prices so the timestamp should be hours=16.
    dt_timeofday = dt.timedelta(hours=16)

    # Get a list of trading days between the start and the end.
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)

    # Timestamps and symbols are the ones that were specified before.
    #print 'the symbols!',symbols
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_rets=d_data['close'].copy()
    #df_rets['normclose']=d_data['close']/d_data.iget(0)['close']
    return df_rets


def getValuePortfolio(date,portfolio,df_data,outfile):

    outformat='%Y-%m-%d-%H'
    valuePortfolio=0.0
    outfile.write('\n')
    outfile.write('======VALUE OF STOCKS at '+str(date.strftime(outformat))+'======'+'\n')
    for isym,units in portfolio.iteritems():
        priceStock=float(df_data.ix[date][isym])
        valueStock=units*priceStock
        outfile.write('     there are '+str(units)+' units of stock '+str(isym)+' with a value of '+str(units)+'*'+str(priceStock)+' = '+str(valueStock)+'\n')
        valuePortfolio+=valueStock
    outfile.write('=====the value is '+str(valuePortfolio)+'\n')
    outfile.write('\n')
    return valuePortfolio

def processOrder(orderdf,dayData,portfolio,cashBalance,outfile):
    '''processes the buy and sell orders in one day'''

    actionSign={}
    actionSign['Buy']=1
    actionSign['Sell']=-1


    outformat='%Y-%m-%d-%H'
    for rows in orderdf.iterrows():
        row=rows[1]
        date=row['mydate']
        action=row['order']
        symbol=row['symbol']
        size=float(row['size'])
        price=dayData[symbol]
        #
        outfile.write('\n')
        outfile.write('NEW ORDER ARRIVED\n')
        outfile.write('     Today the date is '+str(date.strftime(outformat))+ ' and the CASH BALANCE is '+str(cashBalance)+'\n')
        if symbol in portfolio:
            portfolio[symbol]+=actionSign[action]*size
        else:
            portfolio[symbol]=actionSign[action]*size
        cashBalance-=actionSign[action]*size*price
        outfile.write( '     The order is to '+str(action)+' '+str(size)+' shares of '+str(symbol)+ ' at a current price of '+str(price)+'\n')
        outfile.write( '     the current CASH BALANCE after executing the order is '+str(cashBalance)+'\n')
        outfile.write('\n')
    return cashBalance



def AnalyzeStats(thelist,targetDate):
    totalValue=[]
    for tup in thelist:
        totalValue.append(tup[1]+tup[2])
        if targetDate==tup[0]:
            print  'the value at ',targetDate,' is ',tup[1]+tup[2]
    dailyPFValues=np.array(totalValue)
    dailyPFValues=dailyPFValues/dailyPFValues[0]
    totalreturn=dailyPFValues[-1]

    tsu.returnize0(dailyPFValues)

    avg_P=np.average(dailyPFValues)
    sigma_P=np.std(dailyPFValues)
    sharpe_P=np.sqrt(252)*avg_P/sigma_P        

    return avg_P,sigma_P,sharpe_P,totalreturn



def getOrders(orderFile):

    df_orders=pd.read_csv(orderFile,parse_dates=True, names=['year','month','day', 'symbol', 'order', 'size'], header=0 )
    df_orders['mydate']=df_orders.apply(lambda x:pd.datetime(x['year'],x['month'],x['day'],16,0),axis=1)    
    
    return df_orders


def marketSimulation(dt_start,dt_end,startingCash,benchmarkSym,df_orders):


    startingCash=float(startingCash)
    cashBalance=float(startingCash)

    benchmarkSym=str(benchmarkSym)
    benchmarkSymbols=[benchmarkSym]
    #print 'the sym = ',benchmarkSym


    #get the first and last dates:
    dt_start=df_orders['mydate'].iget(0)
    dt_end=df_orders['mydate'].iget(-1)
    dt_end = dt_end.replace(hour = 23)
    #
    #
    #symbols
    symbols=[]
    for rows in df_orders.iterrows():
        if not rows[1]['symbol'] in symbols:
            symbols.append(rows[1]['symbol'])
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']


    #
    df_data=loadData(ls_keys,symbols,dt_start,dt_end)


    allocations={}

    date=0
    olddate=0
    dailyPortfolio=[]
    df_sorted=df_orders.sort('mydate')

    #initialize allocations
    for sym in symbols:
        allocations[sym]=0

    #
    #benchmark stuff
    benchalloc={}
    benchalloc[benchmarkSym]=1.0
    df_bench_data=loadData(ls_keys,benchmarkSymbols,dt_start,dt_end)
    dailyBenchmarkPF=[]
    #
    #

    #LOOP OVER DATES
    ordersfile=open('ordersFile.txt','w')
    for ind in df_data.index:
        #
        newdf=df_sorted[df_sorted['mydate']==ind]
        if newdf.index.size > 0:
            dayData=df_data.ix[ind]
            cashBalance=processOrder(newdf,dayData,allocations,cashBalance,ordersfile)
        yesterday=ind
        valuePortfolioToday=getValuePortfolio(ind,allocations,df_data,ordersfile)
        dailyPortfolio.append((ind,cashBalance,valuePortfolioToday))        
        #get value of benchmark portfolio
        valueBenchToday=getValuePortfolio(ind,benchalloc,df_bench_data,ordersfile)
        dailyBenchmarkPF.append((ind,0,valueBenchToday))        
        
        ordersfile.write('=========TOTAL VALUE OF PORTFOLIO TODAY======\n')
        ordersfile.write('     '+str(cashBalance)+' + '+str(valuePortfolioToday)+' = '+str(cashBalance+valuePortfolioToday)+'\n')
        ordersfile.write('====================================================\n')
        
        
    #GET THE STATS

    targetDate=dt.datetime(2011,3,28,16,00)
    print 'targetDate =' ,targetDate

    avg_P,sigma_P,sharpe_P,totRet=AnalyzeStats(dailyPortfolio,targetDate)
    print 'sharpe ratio is ',sharpe_P    
    print 'standard deviation is ',sigma_P
    print 'average is ',avg_P
    print 'total return is ',totRet
    print ' '
    avg_P,sigma_P,sharpe_P,totRet=AnalyzeStats(dailyBenchmarkPF,targetDate)
    print 'sharpe ratio is ',sharpe_P    
    print 'standard deviation is ',sigma_P
    print 'average is ',avg_P
    print 'total return is ',totRet

  

if __name__=='__main__':

    startingCash,orderFile,valuesFile,benchmarkSym=parseArgs(sys.argv)


    df_orders=getOrders(orderFile)
    marketSimulation(startingCash,benchmarkSym,df_orders)
    #def marketsim(df_orders

