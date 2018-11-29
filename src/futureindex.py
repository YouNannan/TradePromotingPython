#coding:utf-8
'''
Created on 2018年9月26日
本文件提供Index类和它的子类，用来计算指标，另外还提供一个工具函数combineIndexLists来为策略类提供入口参数
Index父类：
    __init__(param1=1,param2=1)：可以最多传入2个参数
    getParam1():获取第一个参数的值
    getParam2():获取第二个参数的值
    cal(theKLineList):用于计算对应于theKLineList的指标，入参是KLineList类型，返回指标列表
    _calSlice(theListSlice):纯虚，且为保护函数，用于子类改写具体的指标生成方法
CloseIndex类：很简单的获取收盘价的指标类
MaIndex类：有一个参数param1，获取均线指标
ChannelIndex类：有一个参数param1,获取通道高低值的指标
MaChannelIndex类：有两个参数，参数param1是均线天数，参数param2是通道天数。本类cal返回的值较复杂，格式为
    [[ma,[maHigh,maLow]], [ma,[maHigh,maLow]], ...]
    
工具函数combineIndexLists(theIndexLists)：用于将theIndexLists转置，即一维和二维互换

@author: You Nannan
'''
from abc import ABCMeta, abstractmethod
import math
import futuretools

class Index(object):
    '''
    指标类,最多包含param1和param2两个参数
    '''
    
    __metaclass__ = ABCMeta #必须先声明
    
    def __init__(self, *theParams):
        '''
        Constructor
        '''
        self.__params = theParams
        
    def getParam1(self):
        return self.__params[0]
    
    def getParam2(self):
        return self.__params[1]
        
    def getParam3(self):
        return self.__params[2]
 
    @abstractmethod #虚函数，保护函数
    def cal(self, theKLineList, theRefDays):
        '''计算指标，返回计算出的指标列表，
        theRefDays就是往前推多少天，例如：theRefDays为0表示返回的指标是当天的值，为1表示返回的指标是昨天的值
        '''
        pass
    
    @staticmethod  
    def _reffer(theList, theRefDays):
        '''将theList以回溯theRefDays天的形式返回，类似博易大师里的REF函数，
            theRefDays就是往前推多少天，例如：theRefDays为0表示返回的指标是当天的值，为1表示返回的指标是昨天的值
        '''
        if theRefDays <= 0:
            return theList
        preList = []
        for i in range(theRefDays):
            preList.append(theList[i-i])
        resultList = preList + theList[0:-theRefDays]
        return resultList
    
    

def combineIndexLists(theIndexLists):
    combineList = []
    for i in range(len(theIndexLists[0])):
        combineList.append([])
        for j in range(len(theIndexLists)):
            combineList[i].append(theIndexLists[j][i])
    return combineList

    

class CloseIndex(Index):
    '''
    当日收盘价指标类，无参数，就是简单的以当日收盘价作为指标
    '''
    def cal(self, theKLineList, theRefDays = 0):
        return Index._reffer(theKLineList.getCloseList(), theRefDays)
        



class MaIndex(Index):
    '''
    过去N日均线指标类，仅包含一个参数：均线日长param1,
    '''
    
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    
    def __calSlice(self, theListSlice):
        '''计算均线指标，返回计算出的均线指标值'''
        theSum = 0.0
        for i in range(len(theListSlice)):
            if i >= self.getParam1():
                return theSum / self.getParam1()
            theSum += theListSlice[i].close()
        return theSum / len(theListSlice)
             



class ChannelOfCloseIndex(Index):
    '''
    过去N日通道指标类（不考虑盘中最高最低价，仅考虑收盘价），仅包含一个参数：通道日长param1,
    '''
        
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    def __calSlice(self, theListSlice):
        '''计算通道指标，返回计算出的通道指标对[high,low]'''
        theHigh = theListSlice[0].close()
        theLow = theListSlice[0].close()
        for i in range(len(theListSlice)):
            if i >= self.getParam1():
                break
            if theListSlice[i].close() > theHigh:
                theHigh = theListSlice[i].close()
            if theListSlice[i].close() < theLow:
                theLow = theListSlice[i].close()
        return [theHigh, theLow]
          

class ChannelOfMaxIndex(Index):
    '''
    过去N日通道指标类（包含盘中最高最低价），仅包含一个参数：通道日长param1,
    '''
        
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    def __calSlice(self, theListSlice):
        '''计算通道指标，返回计算出的通道指标对[high,low]'''
        theHigh = theListSlice[0].high()
        theLow = theListSlice[0].low()
        for i in range(len(theListSlice)):
            if i >= self.getParam1():
                break
            if theListSlice[i].high() > theHigh:
                theHigh = theListSlice[i].high()
            if theListSlice[i].low() < theLow:
                theLow = theListSlice[i].low()
        return [theHigh, theLow]
    

class MaChannelIndex(Index):
    '''
    过去N日均线通道指标类，包含两个参数：均线日长param1,通道日长param2
    '''
    def cal(self, theKLineList, theRefDays = 0):
        fimi = MaIndex(self.getParam1())
        maList = fimi.cal(theKLineList)
        indexList = []
        #将maList和通道列表都加到indexList中
        for i in range(theKLineList.getLen()):
            indexList.append([])
            indexList[i].append(maList[i])
            if i == 0:
                indexList[i].append(self.__calSlice(maList[0:1]))
            elif i < self.getParam2():
                indexList[i].append(self.__calSlice(maList[0:i]))
            else:
                indexList[i].append(self.__calSlice(maList[i - self.getParam2() : i]))
        return Index._reffer(indexList, theRefDays)
    
    def __calSlice(self, theListSlice):
        '''注意，本函数中的theListSlice含义与其他兄弟类中的含义不一样，这里不是KLineList的切片，而是maList的切片'''
        theHigh = theListSlice[0]
        theLow = theListSlice[0]
        for i in range(len(theListSlice)):
            if i >= self.getParam2():
                break
            if theListSlice[i] > theHigh:
                theHigh = theListSlice[i]
            if theListSlice[i] < theLow:
                theLow = theListSlice[i]
        return [theHigh, theLow]
    
    

class RsiIndex(Index):
    '''
    过去N日RSI指标类，仅包含一个参数：日长param1,
    '''
    
    def cal(self, theKLineList, theRefDays = 0):
        indexList = [0.0]
        theUpSma = 0.0
        theTotalSma = 0.0
        closeList = theKLineList.getCloseList()
        for i in range(1, theKLineList.getLen()):
            if closeList[i] > closeList[i - 1]:
                theUp = closeList[i] - closeList[i - 1]
                theDown = 0.0
            else:
                theUp = 0.0
                theDown = closeList[i - 1] - closeList[i]
                
            if i == 1:
                temp = 1
            else:
                temp = self.getParam1()
            theUpSma = (theUp + (temp - 1) * theUpSma) / temp
            theTotalSma = (theUp + theDown + (temp - 1) * theTotalSma) / temp
            if theTotalSma == 0.0:
                rsi = 0.0
            else:
                rsi = 100 * theUpSma / theTotalSma
            indexList.append(rsi)
        return Index._reffer(indexList, theRefDays)
    
    
    
class MacdIndex(Index):
    '''
    MACD指标类，仅包含三个参数：短周期日长param1(一般为12),长周期日长param2(一般为26),最后的M日平均param3(一般为9)
    '''
    
    def cal(self, theKLineList, theRefDays = 0):
        '''theRefDays参数在macd指标中无效'''
        indexList = []
        closeList = theKLineList.getCloseList()
        theEma1 = closeList[0]
        theEma2 = closeList[0]
        theDiff = 0.0
        theDea = 0.0
        theMacd = 0.0
        indexList.append([0.0, 0.0, 0.0])
        for i in range(1, theKLineList.getLen()):
            theEma1 = (2 * closeList[i] + (self.getParam1() - 1) * theEma1) / (self.getParam1() + 1)
            theEma2 = (2 * closeList[i] + (self.getParam2() - 1) * theEma2) / (self.getParam2() + 1)
            theDiff = theEma1 - theEma2
            if i == 1:
                theDea = theDiff
                theMacd = 0.0
                indexList.append([theDiff, 0.0, 0.0])
            else:
                theDea = (2 * theDiff + (self.getParam3() - 1) * theDea) / (self.getParam3() + 1)
                theMacd = 2 * (theDiff - theDea)
                indexList.append([theDiff, theDea, theMacd])
        return indexList
    
    
    
class ExpectedIndex(Index):
    '''
    Boll通道用到的期望和标准差指标类，仅包含一个参数：周期日长param1
    '''
    
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    
    def __calSlice(self, theListSlice):
        '''计算收盘价序列期望和标准差'''
        theList = []
        theCount = min(len(theListSlice), self.getParam1())
        for i in range(theCount):
            theList.append(theListSlice[i].close())
        return futuretools.getExpectedStandard(theList)



class ExpectedPromotingIndex(Index):
    '''
    Boll通道变种，仅包含一个参数：周期日长param1
    此处和通常的布尔通道不同，此处将一起考虑开盘价、最高价、最低价、收盘价，并且收盘价作为重要价位将会加权作为双份来计算。
    '''
    
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    
    def __calSlice(self, theListSlice):
        '''计算收盘价序列期望和标准差'''
        theList = []
        theCount = min(len(theListSlice), self.getParam1())
        for i in range(theCount):
            theList.append(theListSlice[i].close())
            theList.append(theListSlice[i].close())
            theList.append(theListSlice[i].open())
            theList.append(theListSlice[i].high())
            theList.append(theListSlice[i].low())
        return futuretools.getExpectedStandard(theList)



class AttackIndex01(Index):
    '''
    简称AI01，过去N日K线中有多少红K线和多少根绿K线的数量指标，仅包含一个参数：通道日长param1,
    '''
        
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    def __calSlice(self, theListSlice):
        '''计算通道指标，返回计算出的通道指标对[high,low]'''
        theCount = min(len(theListSlice), self.getParam1())
        upCount = 0
        downCount = 0
        for i in range(theCount):
            if theListSlice[i].close() > theListSlice[i].open():
                upCount += 1
            if theListSlice[i].close() < theListSlice[i].open():
                downCount += 1
        return [upCount, downCount]


class AttackIndex02(Index):
    '''
    简称AI02,过去N日K线中向上攻击力与向下攻击力占比的指标，仅包含一个参数：通道日长param1,
    '''
        
    def cal(self, theKLineList, theRefDays = 0):
        indexList = []
        for i in range(theKLineList.getLen()):
            if i < self.getParam1():
                indexList.append(self.__calSlice(theKLineList.getList()[0:i + 1]))
            else:
                indexList.append(self.__calSlice(
                    theKLineList.getList()[i + 1 - self.getParam1() : i + 1]))
        return Index._reffer(indexList, theRefDays)
    
    def __calSlice(self, theListSlice):
        '''计算通道指标，返回计算出的通道指标对[high,low]'''
        theCount = min(len(theListSlice), self.getParam1())
        upAttackSum = 0.0
        downAttackSum = 0.0
        for i in range(theCount):
            if theListSlice[i].close() >= theListSlice[i].open():
                upAttack = theListSlice[i].high() - theListSlice[i].low()
                downAttack = upAttack + theListSlice[i].open() - theListSlice[i].close()
                if upAttack < 0 or downAttack < 0:#有时候会有傻逼数据
                    continue
                upAttackSum += upAttack
                downAttackSum += downAttack
            else:
                downAttack = theListSlice[i].high() - theListSlice[i].low()
                upAttack = downAttack - theListSlice[i].open() + theListSlice[i].close()
                if upAttack < 0 or downAttack < 0:#有时候会有傻逼数据
                    continue
                upAttackSum += upAttack
                downAttackSum += downAttack
        attackSum = upAttackSum + downAttackSum
        if attackSum <= 0:
            return 50.0
        return 100.0 * upAttackSum / attackSum
    
    
