#coding:utf-8
'''
Created on 2018年9月27日

@author: You Nannan
'''
import unittest
import futureindex
import futuretools
import futurecommodity
import futurelogger
import futurestrategy


class Test(unittest.TestCase):


    def testName(self):
        theKLineList = futurecommodity.getContractKLineList("AP1901")
        
        #scs = futurestrategy.SimpleChannelCloseStrategy(20)
        mcs = futurestrategy.MaChannelStrategy(3, 18)
        signalList = mcs.signal(theKLineList)
        combineList = futureindex.combineIndexLists([theKLineList.getTimeList(), signalList])
        futurelogger.log(combineList)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()