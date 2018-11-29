#coding:utf-8
'''
Created on 2018年9月26日

@author: You Nannan
'''
import unittest
import futureindex
import futuretools
import futurecommodity
import futurelogger


class Test(unittest.TestCase):


    def testName01(self):
        '''
        theKLineList = futurecommodity.getContractKLineList("AP0909")
        closeList = theKLineList.getCloseList()
        
        fiMa = futureindex.MaIndex(3)
        fiC = futureindex.ChannelOfCloseIndex(3)
        
        
        print(closeList)
        ma = fiMa.cal(theKLineList)
        print(ma)
        c = fiC.cal(theKLineList)
        print(c)
        '''
        
    
    def testName02(self):
        '''
        theKLineList = futurecommodity.getContractKLineList("AP0909")
        #closeList = theKLineList.getCloseList()
        
        fiClose = futureindex.CloseIndex()
        fiMa = futureindex.MaIndex(3)
        fiC = futureindex.ChannelOfCloseIndex(3)
        
        closeList = fiClose.cal(theKLineList)
        futurelogger.log(closeList)
        ma = fiMa.cal(theKLineList)
        futurelogger.log(ma)
        c = fiC.cal(theKLineList)
        futurelogger.log(c)
        combineList = futureindex.combineIndexLists([closeList, ma, c])
        futurelogger.log(combineList)
        '''

    def testName03(self):
        '''
        theKLineList = futurecommodity.getContractKLineList("AP1901")
        
        fimci = futureindex.MaChannelIndex(3, 18)
        
        mciList = fimci.cal(theKLineList)
        
        timeList = theKLineList.getTimeList()
        closeList = theKLineList.getCloseList()
        combineList = futureindex.combineIndexLists([timeList, closeList, mciList])
        futurelogger.log(mciList)
        futurelogger.log(combineList)
        futurelogger.log("\n")
        '''
        
    def test04(self):
        '''测试rsi指标'''
        futurecommodity.setDataDirAfterVerified()
        theKLineList = futurecommodity.getContractKLineList("AP1901", True)
        
        futurelogger.log(theKLineList)
        fiRsi6 = futureindex.RsiIndex(6)
        futurelogger.log(fiRsi6.cal(theKLineList))
        fiRsi12 = futureindex.RsiIndex(3)
        futurelogger.log(fiRsi12.cal(theKLineList))
        fiRsi24 = futureindex.RsiIndex(24)
        futurelogger.log(fiRsi24.cal(theKLineList))
        
        
    def test05(self):
        '''测试macd指标'''
        futurecommodity.setDataDirAfterVerified()
        theKLineList = futurecommodity.getContractKLineList("AP1901", True)
        
        futurelogger.log(theKLineList)
        fiMacd = futureindex.MacdIndex(12,26,9)
        futurelogger.log(fiMacd.cal(theKLineList))
        
    def test06(self):
        '''测试ExpectedIndex数学期望方差指标'''
        futurecommodity.setDataDirAfterVerified()
        theKLineList = futurecommodity.getContractKLineList("AP1901", True)
        
        futurelogger.log(theKLineList)
        fiMacd = futureindex.ExpectedIndex(26)
        futurelogger.log(fiMacd.cal(theKLineList))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()