#coding:utf-8
'''
Created on 2018年9月23日

@author: You Nannan
'''
import unittest
import futurelogger


class Test(unittest.TestCase):



    def testLog(self):
        futurelogger.log("futurelogger测试用例01")


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()