#coding:utf-8
'''
Created on 2018年9月24日

@author: You Nannan
'''
import unittest
import futurecontract
import futurecommodity
import futurelogger
import datetime


class Test(unittest.TestCase):


    def test01(self):
        pass
        '''
        kLine = futurecontract.KLine(eval("['2003-03-17', '2550.000', '2560.000', '2550.000', '2560.000', '42']"))
        
        print(type(kLine.time()))
        print(type(kLine.timeString()))
        print(kLine.timeString())
        print(type(kLine.open()))
        print(kLine.open())
        print(type(kLine.high()))
        print(kLine.high())
        print(type(kLine.low()))
        print(kLine.low())
        print(type(kLine.close()))
        print(kLine.close())
        print(type(kLine.vol()))
        print(kLine.vol())'''

    def test02(self):
        '''
        kList = futurecommodity.getContractKLineList("AP1901")
        for i in range(len(theList)):
            theList[i].append(kList.isLimitUp(i))
            theList[i].append(kList.isLimitDown(i))
        futurelogger.log(theList)
        '''
        
    def test03(self):
        kList = futurecommodity.getContractKLineList("AP1901")
        theDate01 = datetime.datetime.strptime('2018-09-16', "%Y-%m-%d")
        theDate02 = datetime.datetime.strptime('2018-09-21', "%Y-%m-%d")
        sub01 = kList.getSubscript(theDate01)
        sub02 = kList.getSubscript(theDate02)
        if sub01 is None:
            print("sub01 is None")
        else:
            print("sub01 time:" + kList.getKLine(sub01).timeString())
        if sub02 is None:
            print("sub02 is None")
        else:
            print("sub02 time:" + kList.getKLine(sub02).timeString())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()