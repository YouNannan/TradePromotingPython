'''
Created on 2018年9月27日

@author: You Nannan
'''
import unittest
import futuretrade
import futurelogger
import datetime
import futurestrategy
import futurecommodity


class Test(unittest.TestCase):


    '''需要开启futuretrade.isHaveToCloseTransTest来配合测试
    def testName01(self):
        
        ft = futuretrade.Transaction("AP1810", 
                                     datetime.datetime(2018, 5, 7),
                                     7861.0, futuretrade.DIRECTION_LONG)
        
        tr = futuretrade.TradeCenter(datetime.datetime(2018, 1, 18),
                                     datetime.datetime(2018, 9, 28),
                                     600,
                                     1.0)
        
        theDateList = [datetime.datetime(2018, 5, 6),
                       datetime.datetime(2018, 5, 7),
                       datetime.datetime(2018, 5, 8),
                       datetime.datetime(2018, 5, 24),
                       datetime.datetime(2018, 7, 5),
                       datetime.datetime(2018, 7, 6),
                       datetime.datetime(2018, 7, 7),
                       datetime.datetime(2018, 7, 8),
                       datetime.datetime(2018, 7, 15),
                       datetime.datetime(2018, 7, 16),
                       datetime.datetime(2018, 7, 17),]
        for i in range(len(theDateList)):
            result = tr.isHaveToCloseTransTest(theDateList[i], "AP1810", 9219.0, ft)
            print(str(theDateList[i]) + ":" + str(result))
            
        priceList = [8630,8640,8650,8660,
                     7060,7070,7080,7090]
        for i in range(len(priceList)):
            result = tr.isHaveToCloseTransTest(
                       datetime.datetime(2018, 5, 24), "AP1810", priceList[i], ft)
            print(str(priceList[i]) + ":" + str(result))
        
    '''
    
    def testName02(self):
        
        '''
        futurecommodity.setDataDirAfterVerified()
        tc = futuretrade.TradeCenter(datetime.datetime(2008, 1, 1),
                                     datetime.datetime(2019, 1, 1))
        for commodityName in futurecommodity.getCommodityList():
            tc.addCommodity(commodityName)
        theStrategy = futurestrategy.SimpleChannelCloseStrategy(20)#.MaChannelStrategy(3, 18)
        tc.setStrategy(theStrategy)
        transactionDict = tc.trade()
        profitSumTotal = 0.0
        transCount = 0
        for commodity in transactionDict.keys():
            profitSumCommodity = 0.0
            if len(transactionDict[commodity]) == 0:
                continue
            for theTrans in transactionDict[commodity]:
                profitSumCommodity += theTrans.getProfitRate()
                profitSumTotal += theTrans.getProfitRate()
            futurelogger.log(commodity + ":" + str(len(transactionDict[commodity]))
                + " transactions, average profit rate = "
                + format(profitSumCommodity / len(transactionDict[commodity]),
                         "0.4f"))
            transCount += len(transactionDict[commodity])
        
        futurelogger.log("Total:" + str(transCount)
                + " transactions, average profit rate = "
                + format(profitSumTotal / transCount, "0.4f"))
        #futurelogger.log(repr(transactionDict))
        '''
        
            
            

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()