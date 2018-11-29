#coding:utf-8
'''
Created on 2018年9月23日

@author: You Nannan
'''
import unittest
import datetime

class Test(unittest.TestCase):


    def testName(self):
        #print(type(datetime.datetime.strptime('2003-03-17', "%Y-%m-%d")))
        #print(datetime.datetime.strptime('2003-03-17', "%Y-%m-%d"))
        theDate01 = datetime.datetime.strptime('2003-03-17', "%Y-%m-%d")
        theDate02 = datetime.datetime.strptime('2003-03-16', "%Y-%m-%d")
        theDate02 += datetime.timedelta(days=1)
        if theDate01 > theDate02 :
            print("theDate01 > theDate02")
        elif theDate01 == theDate02 :
            print("theDate01 == theDate02")
        else:
            print("theDate01 < theDate02")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()