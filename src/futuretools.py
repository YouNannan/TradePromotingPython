#coding:utf-8
'''
Created on 2018年9月23日


@author: You Nannan
'''

import os
import datetime
import math



def mkdirIfNotExist(theDir):
    folder = os.path.exists(theDir)
    if not folder:
        os.makedirs(theDir)
        
def readListFromFile(filename):
    '''从filename中读取列表或字典'''
    with open(filename) as file_object:
        theListStr = file_object.read()
    return eval(theListStr)

def writeListToFile(filename, theList, isRepr = True):
    '''向filename中写入列表或字典'''
    with open(filename, "w") as file_object:
        if isRepr is True:
            file_object.write(repr(theList))
        else:
            file_object.write(str(theList))

         
def getDaysList(beginDate, endDate):
    '''获取从[beginDate,endDate)中的所有日期列表'''
    theDaysList = []
    iDate = beginDate
    while iDate < endDate:
        theDaysList.append(iDate)
        iDate += datetime.timedelta(days=1)
    return theDaysList

def getClassName(theValue):
    theClassName = str(type(theValue))[8:-2]
    theClassName = theClassName[theClassName.rfind(".") + 1:]
    return theClassName


def getExpectedStandard(theList):
    '''计算theList样本序列的期望和标准差，此处的标准差是总体标准差，不是样本标准差'''
    theCount = len(theList)
    if theCount < 1:
        return None
    if theCount == 1:
        return [theList[0], 0.0]
    
    theSum = 0.0
    for i in range(theCount):
        theSum += theList[i]
    theExpected = theSum / theCount
    theSum = 0.0
    for i in range(theCount):
        theSum += (theList[i] - theExpected)**2
    theStandard = math.sqrt(theSum / (theCount - 1)) #这里的标准差是总体标准差，而不是样本标准差，所以除以(theCount - 1)而不是除以theCount
    return [theExpected, theStandard]



