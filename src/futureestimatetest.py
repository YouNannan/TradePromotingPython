'''
Created on 2018年10月2日

@author: You Nannan
'''
import unittest
import futureestimate
import futurestrategy
import futurelogger
from futurestrategy import RandomStrategy01


MY_COMMODITY_LIST = ["AG","AL","AP","AU","B","BU",
            "C","CF","CS","CU","CY","FB","FU",
            "HC","I","J","JM","JR","L",
            "LR","MA","NI","P","PB","PP",
            "RB","RM","RS","RU","SC","SF",
            "SM","SN","SR","TA","V","WR",
            "ZC","ZN",]
    
class Test(unittest.TestCase):


    def test01(self):
        
        theStrategy = (futurestrategy.#SimpleChannelCloseStrategy(20))
                                    #MaChannelStrategy(3, 18))
                                    #BabcockStrategy(18, 100 , 2.0))
                                    #ChannelCloseExtraStrategy01(20))
                                    #ChannelCloseExtraStrategy02(20, 10, 3))
                                    #ChannelCloseExtraStrategy03(50, 10))
                                    #ChannelCloseExtraStrategy04(5, 20))
                                    #RsiStrategy(5, 37 , 2.0))
                                    #RsiStrategy02(7, 25))
                                    #RsiStrategy03(7, 25))
                                    #SimpleKLineStrategy01(16, 3))
                                    SimpleKLineStrategy02(9, 13))
                                    #RandomStrategy01(10, 2))
                                    #MacdStrategy01())
                                    #ChannelMacdStrategy(20))
                                    #BollStrategy(26,20))
                                    #BollStrategy02(20,30))
                                    #BollStrategy03(35,10))
                                    #BollPromotingStrategy(26,20))
                                    #ChannelAndBollStrategy(20, 26, 20))
                                    #ChannelRsiStrategy(18, 16))
                                    #ChannelRsiStrategy02(18, 16))
        futureestimate.reportAnnually01(2009, 2019, theStrategy, None, True, True, 60, 0.5)
        '''
        theStr = futureestimate.reportAnnually01(2008, 2019, theStrategy, 
            ["CU","AG","RB","RU","FU",
             "A","M","Y","C","J","L","JD","I",
             "WH","SR","CF","TA","FG","AP",], True,True)
        futurelogger.log(theStr)
        '''
        #futureestimate.reportAnnually01(2013, 2014, theStrategy, ["JD"], True, True)
        
    def test02(self):
        theStrategy = (futurestrategy.#SimpleChannelCloseStrategy(20))
                                    MaCrossStrategy01(10,20))
                                    #MaChannelStrategy(3, 18))
                                    #BabcockStrategy(18, 100 , 2.0))
                                    #ChannelCloseExtraStrategy01(20))
                                    #ChannelCloseExtraStrategy02(20, 10, 3))
                                    #ChannelCloseExtraStrategy03(20, 10))
                                    #ChannelCloseExtraStrategy04(5, 20))
                                    #RsiStrategy(12, 20))
                                    #RsiStrategy02(5, 37))
                                    #RsiStrategy03(7, 25))
                                    #SimpleKLineStrategy01(20, 20))
                                    #SimpleKLineStrategy02(12, 11))
                                    #RandomStrategy01(10, 2))
                                    #ChannelMacdStrategy(20))
                                    #BollStrategy(26,20))
                                    #BollStrategy02(20,30))
                                    #BollStrategy03(30,20))
                                    #BollPromotingStrategy(26,20))
                                    #ChannelAndBollStrategy(20, 26, 20))
                                    #ChannelRsiStrategy02(20, 20)))
        futureestimate.reportParamAnalysis(2008, 2017, theStrategy,
                        None, #交易的商品代码列表，默认为所有商品
                        5, 15, 1
                        ,16, 50, 2
                        ,60, 0.5
                     )

    def test03(self):
        pass
        #theStrategy = futurestrategy.TwoChannelStrategy01(18,30)
                                    #MaChannelStrategy(3, 18)
        #futureestimate.reportAnnually01(2008, 2019, theStrategy)#
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test01']
    unittest.main()