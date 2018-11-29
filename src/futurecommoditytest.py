#coding:utf-8
'''
Created on 2018年9月23日

@author: You Nannan
'''
import unittest
import futurecommodity
import futurecontract
import futuretools


class Test(unittest.TestCase):


    def testEstablishCommodityDataFromInternet(self):
        #futurecommodity.updateAllAvailableCommodityCode()#这个很少用
        #futurecommodity.updateAllDayKLine()
        #futurecommodity.updateMainContractDict()#这个一个月用一次
        
        futurecommodity.checkAllDayKLine()
        
        '''
        kLineList = futurecommodity.getContractKLineList("AL1810")
        futurecommodity.setDataDirAfterVerified()
        path = "../data/verified/AL/AL1810.txt"
        futuretools.writeListToFile(path, kLineList)
        
        theContractRaw = futuretools.readListFromFile(path)
        theContract = futurecontract.KLineList(theContractRaw)
        futuretools.writeListToFile("../data/verified/AL/AL1810_2.txt", theContract)
        '''
        
        
        '''
        mcd = futurecommodity.getMainContractDict()
        mcdLen = len(mcd)
        futurelogger.log(mcdLen)
        contractCount = 0
        for commodityName in mcd.keys():
            contractCount += len(mcd[commodityName])
            theInfo = commodityName + "(" + repr(
                len(mcd[commodityName])) + "):" + repr(mcd[commodityName])
            futurelogger.log(theInfo)
        futurelogger.log(contractCount)
        '''
        
    def test02(self):
        pass
        #kLineList = futurecommodity.getContractKLineList("J1901")
        #futurelogger.log(kLineList)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testEstablishCommodityDataFromInternet']
    unittest.main()