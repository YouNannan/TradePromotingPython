#coding:utf-8
'''
Created on 2018年9月27日
本文件提供Strategy类和它的子类，用来提供交易信号
Strategy类和它的子类应该是起到一个顾问的作用，提示Trade类今天应该采取什么动作，但是最终的交易的决定权仍然在Trade类中。

Strategy类：
    __init__(self, *theParams)：可以传入不定个数的参数
    getParam1():获取第一个参数的值
    getParam2():获取第二个参数的值
    signal(theKLineList):传入KLineList类型参数，返回交易信号列表，信号详情参见_signalSlice()的注释
    _prepareIndexList():纯虚，保护函数，返回用于在计算交易信号列表之前需要准备的indexList
    _signalSlice():纯虚，保护函数，计算某一根K线（或某个日期的指标）所指示的交易信号，子类必须重载
SimpleChannelStrategy类：简单的通道突破策略，仅有一个通道天数的参数param1
MaChannelStrategy类，均线通道突破策略，有两个参数，param1是均线天数，param2是通道天数

@author: You Nannan
'''

from abc import ABCMeta, abstractmethod
import futureindex
import futuretrade
import random

class Strategy(object):
    '''
    交易策略类，用于发出交易信号
    '''

    __metaclass__ = ABCMeta #必须先声明
    
    def __init__(self, *theParams):
        '''
        Constructor
        '''
        self.__params = list(theParams)
        
    def getParam1(self):
        if len(self.__params) < 1:
            return 0
        return self.__params[0]
    
    def setParam1(self, theValue):
        self.__params[0] = theValue
    
    def getParam2(self):
        if len(self.__params) < 2:
            return 0
        return self.__params[1]
    
    def setParam2(self, theValue):
        self.__params[1] = theValue
    
    
    def _getHiddenParam3(self):
        '''第三个参数不公开'''
        return self.__params[2]
    
    def getMaxParam(self):
        return max(self.__params)

    
    
    @abstractmethod #虚函数
    def signal(self, theKLineList, theKLineSub, theTransaction):
        '''根据当前掌握的K线信息和交易持仓情况，得到交易信号（Action类型）'''
        pass
        
    
    @abstractmethod #虚函数
    def prepareIndexList(self, theKLineList):
        '''在计算signal之前需要准备好Index的工作，都在本函数里完成'''
        pass
    
    
    
    
    
class Action(object):
    '''交易时应该采取的动作类型'''
    
    def __init__(self, theActionStr):
        '''构造函数需传入交易信号字串，解释如下：
            "long":表示需要买入，此信号表示强力看多，指示在当前三种持仓情况下的标准动作如下：
                _持多：无动作
                _无仓位：开多头
                _持空：平掉空头，并反手开多
            "pingkong":表示需要平空，此信号表示略微看多，指示在当前三种持仓情况下的标准动作如下：
                _持多：无动作
                _无仓位：无动作
                _持空：平掉空头
            "none":表示没有动作，此信号表示没有观察出多空走向，指示在当前三种持仓情况下的标准动作如下：
                _持多：无动作
                _无仓位：无动作
                _持空：无动作
            "pingduo":表示需要平多，此信号表示略微看空，指示在当前三种持仓情况下的标准动作如下：
                _持多：平掉多头
                _无仓位：无动作
                _持空：无动作
            "short":表示需要卖出，此信号表示强力看空，指示在当前三种持仓情况下的标准动作如下：
                _持多：平掉多头，并反手开空
                _无仓位：开空头
                _持空：无动作
        '''
        self.action = theActionStr
        
    def isLong(self):
        return self.action == "long"
    def isPingkong(self):
        return self.action == "pingkong"
    def isNone(self):
        return self.action == "none"
    def isPingduo(self):
        return self.action == "pingduo"
    def isShort(self):
        return self.action == "short"
    def getOpenDirection(self):
        if self.action == "long":# or self.action == "pingkong":
            return futuretrade.DIRECTION_LONG
        if self.action == "short":# or self.action == "pingduo":
            return futuretrade.DIRECTION_SHORT
        return None
            
    def __repr__(self):
        return self.action
    
    def __str__(self):
        return self.action
    
    def setLossPrice(self, thePrice):
        self.lossPrice = thePrice
        
    def getLossPrice(self):
        return self.lossPrice
    
    
    
class SimpleChannelCloseStrategy(Strategy):
    '''
    简单的通道突破交易策略类，仅包含一个通道天数参数param1,
    在向上突破通道时发出"long"信号，
    在向下突破通道时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.channelList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh = theIndexList[theSub][0]
        theLow = theIndexList[theSub][1]
        if theClose > theHigh:
            return Action("long")
        elif theClose < theLow:
            return Action("short")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.ChannelOfCloseIndex(self.getParam1())
        self.channelList = fici.cal(theKLineList, 1)
    
        
        

class MaChannelStrategy(Strategy):
    '''
    均线的通道突破交易策略类，包含两个参数：均线天数param1,和通道天数param2
    在向上突破通道时发出"long"信号，
    在向下突破通道时发出"short"信号，
    其他时候发"none"信号
    '''
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.maChannelList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")

        theMa = theIndexList[theSub][0]
        theHigh = theIndexList[theSub][1][0]
        theLow = theIndexList[theSub][1][1]
        if theMa > theHigh:
            return Action("long")
        elif theMa < theLow:
            return Action("short")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fimci = futureindex.MaChannelIndex(self.getParam1(), self.getParam2())
        self.maChannelList = fimci.cal(theKLineList)
    
        
        
  
        
        
        
class BabcockStrategy(Strategy):
    '''
    使用双通道的交易策略类，《高级技术分析》作者Babcock所推荐的一套交易方法，编号bs，
    包含两个通道天数参数：短通道param1,长通道param2
    Babcock(鲍伯郭克）的长期系统唯有当市场创130天的高价或低价时才会采取行动。
    这相当于六个月的期间。换言之，今天的高价高于过去130天的高价，或
    是今天的低价低于过去130天的低价。若是如此，则依下列步骤来操作此系统：
    1.等待至隔天收盘（创130天高价或低价的次日）
    2.测量过去20天最高价与最低价之间的价差。
    3.以第2步骤所计算之价差，加到今天的收盘价（创130天高价或低价的次日）。
    此即为买进点。
    4.以第2步骤所计算之价差，从今天的收盘价中扣除（创130元高价或低价的次
    日）。此即为卖出点。
    5.等待市场触及买进点或卖出点。如果交易首先触及买进点，则于当天收盘买
    进。以卖出点做为反转停损点。如果市场首先触及卖出点，则于当天收盘卖
    出。以买进点做为反转停损点。
    如果市场在触及上述买进点或卖出点之前，又创130天的新高价位，则重复上
    述第1、2、3、4的步骤。如果新的卖出点高于先前之卖出点，则以它来取代前
    者，如果新的买进点低于先前之买进点，则以它来取代先前者。否则便保留当时
    的买进点与卖出点。
    如果市场在触及上述买进点或卖出点之前，又创130天的新低价位，则重复上
    述第1、2、3、4的步骤。如果新的买进点低于先前之买谁点，则以它来取代先前
    者。如果新的卖出点高于先前之卖出点，则以它来取代先前者。否则便保留当时
    的买进点与卖出点。
    建立多头部位之后，如果市场再创130天新高价位，则重复上述第1、2、3、4
    的步骤。如果新的卖出点高于先前的卖出点，则以它取代前者。如果新的买进
    点，其价位与当时多头部位之进场点有所不同，则继续追踪买进价位，万一触及2,500
    美元的资金管理停损而出场，或反转为空头部位时，则上述价位将成为新的
    买进点。你绝对不会连续两次采用相同的买进点。这可能使你留滞场外而无买进
    点。在这种情况下，则追踪当时的卖出点，准备建立可能的空头部位，并等待市
    场变化以产生新的买进点。
    建立空头部位之后，如果市场再创130天新低价位，则重复上述第1、2、3、4
    的歩骤。如果新的买进点低于先前之买进点，则以它取代先前者。如果新的卖出
    点，其价位与当时空头部位之进场点有所不同，则继续追踪卖出价位，万一你触
    及2,500美元的资金管理停损而出场，或反转为多头部位时，则上述价位将成为新
    的卖出点。你绝对不会连续两次採用相同的卖出点。这可能使你留于场外而无卖
    出点。在这种情况下，则追踪当时的买进点，以准备建立可能的多头部位，并等
    待市场变化以产生新的卖出点。
    —旦建立部位，在该部位出现2,500美元亏损（不含佣金费用）的价位上，设
    定停损点。这种资金管理的停损点有其必要性，因为市场趋势如果产生变化，该
    系统并不保证可以产生相反的讯号。如果未设定停损，则可能造成龎大的损失。
    部位建立之后便继续持有该部位，直至停损点遭到触及，或产生相反部位之
    讯号为止。如果市场触及停损点，则出清当时的部位，并以当时的买进点和卖出
    点做为新的进场点。如果出现相反的进场讯号，则了结当时的部位，并依讯号建
    立新的部位。然后，以相反方向的进场点做为停损点与部位反转点，并设定新的
    2,500美元资金管理停损点。每当市场创130天之新高点或新低点，则重覆上述第
    1、2、3、4的步骤（在实际交易中>如果你持有即将到期之契约，则在该契约的
    第一通知日之前，将该契约展至未平仓契约最高的月份。这种做法并不适用于历
    史测试，因为我们採用连续性契约，而连续性契约没有到期的问题）。
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        '''实际执行策略时，做些许修改。首先，买入价和卖出价仅从近20日（param1）内开始计算，而不考虑太远的信息'''
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        buySellPrice = [-1.0, -1.0]
        startSub = self.__generateStartSub(theKLineList, theSub, theTransaction)
        if (theTransaction is None) or theTransaction.isClosed():
            #当前没有持仓
            for i in range(theSub, startSub, -1):
                buySellPrice = self.__stepOneTwoThreeFour(theKLineList, i, theTransaction, buySellPrice)
                if buySellPrice[0] > 0:
                    if theClose > buySellPrice[0] and theClose < buySellPrice[1]:
                        raise Exception("theClose > buySellPrice[0] and theClose < buySellPrice[1]")
                    if theClose > buySellPrice[0]:
                        return Action("long")
                    elif theClose < buySellPrice[1]:
                        return Action("short")
        elif theTransaction.isLong():
            #当前是多头
            if theTransaction.isOverLoss(theClose, self.stopLossRate):
                return Action("pingduo")
            for i in range(theSub, startSub, -1):
                buySellPrice = self.__stepOneTwoThreeFour(theKLineList, i, theTransaction, buySellPrice)
                if buySellPrice[0] > 0:
                    if theClose < buySellPrice[1]:
                        return Action("short")
        else:
            #当前是空头
            if theTransaction.isOverLoss(theClose, self.stopLossRate):
                return Action("pingkong")
            for i in range(theSub, startSub, -1):
                buySellPrice = self.__stepOneTwoThreeFour(theKLineList, i, theTransaction, buySellPrice)
                if buySellPrice[0] > 0:
                    if theClose > buySellPrice[0]:
                        return Action("long")
        return Action("none")
            
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.ChannelOfCloseIndex(self.getParam1())
        fici2 = futureindex.ChannelOfCloseIndex(self.getParam2())
        self.channelList1 = fici1.cal(theKLineList, 1)
        self.channelList2 = fici2.cal(theKLineList, 1)
        self.stopLossRate = self._getHiddenParam3() #第三个参数就是止损比例，即所谓的2500美元停损点的设置
    
    def __generateStartSub(self, theKLineList, theSub, theTransaction):
        '''决定第一个开始回溯130天的日期在K线图中的下标'''
        noSigCount = self.getMaxParam()
        if theSub > noSigCount + self.getParam1() * 2:
            startSub = theSub - self.getParam1() * 2
        else:
            startSub = noSigCount
            
        if theTransaction is None:
            return startSub
        else:
            if theTransaction.isClosed():
                theDate = theTransaction.closeTime
            else:
                theDate = theTransaction.openTime
            transSub = theKLineList.getSubscript(theDate)
            if transSub is None:
                return startSub
            return max(startSub, transSub)
        
    def __stepOneTwoThreeFour(self, theKLineList, theSub, theTransaction, theBuySellPrice):
        '''做Babcock策略中的第1,2,3,4步骤，返回[newBuyPrice, newSellPrice]'''
        theIndexList1 = self.channelList1 #短期通道指标
        theIndexList2 = self.channelList2 #长期通道指标
        theClose = theKLineList.getKLine(theSub).close()
        indexHigh1 = theIndexList1[theSub][0]
        indexLow1 = theIndexList1[theSub][1]
        indexHigh2 = theIndexList2[theSub][0]
        indexLow2 = theIndexList2[theSub][1]
        buyPrice = theBuySellPrice[0]
        sellPrice = theBuySellPrice[1]
        if theClose > indexHigh2 or theClose < indexLow2:
            indexHeight1 = indexHigh1 - indexLow1
            newBuyPrice = theClose + indexHeight1
            newSellPrice = theClose - indexHeight1
            if buyPrice < 0:
                buyPrice = newBuyPrice
                sellPrice = newSellPrice
            else:
                if newBuyPrice < buyPrice or (
                    (theTransaction is not None) and (not theTransaction.isClosed()) and theTransaction.isLong()):
                    buyPrice = newBuyPrice
                if newSellPrice > sellPrice or (
                    (theTransaction is not None) and (not theTransaction.isClosed()) and theTransaction.isShort()):
                    sellPrice = newSellPrice
        return [buyPrice, sellPrice]
                


class ChannelCloseExtraStrategy01(Strategy):
    '''
    通道突破，并附上额外条件的交易策略类，仅包含一个通道天数参数param1,
    在向上突破通道时发出"long"信号，
    在向下突破通道时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.channelList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh = theIndexList[theSub][0]
        theLow = theIndexList[theSub][1]
        
        #三天内有回调才开仓
        for i in range(1, 4):
            foreClose = theKLineList.getKLine(theSub - i).close()
            foreHigh = theIndexList[theSub - i][0]
            foreLow = theIndexList[theSub - i][1]
            if theClose < foreHigh and foreClose > foreHigh:
                return Action("long")
            elif theClose > foreLow and foreClose < foreLow:
                return Action("short")
        
        if theClose > theHigh:
            return Action("pingkong")
        elif theClose < theLow:
            return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.ChannelOfCloseIndex(self.getParam1())
        self.channelList = fici.cal(theKLineList, 1)
        

class ChannelCloseExtraStrategy02(Strategy):
    '''
    通道突破，并附上额外条件的交易策略类，仅包含通道天数参数param1,和短通道回调因子param2
    在向上突破通道时发出"long"信号，
    在向下突破通道时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList1 = self.channelList1
        theIndexList2 = self.channelList2
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh1 = theIndexList1[theSub][0]
        theLow1 = theIndexList1[theSub][1]
        theHigh2 = theIndexList2[theSub][0]
        theLow2 = theIndexList2[theSub][1]
        
        #三天内有回调才开仓
        for i in range(1, self._getHiddenParam3() + 1):
            foreClose = theKLineList.getKLine(theSub - i).close()
            foreHigh = theIndexList1[theSub - i][0]
            foreLow = theIndexList1[theSub - i][1]
            if theClose < foreHigh and foreClose > foreHigh:
                return Action("long")
            elif theClose > foreLow and foreClose < foreLow:
                return Action("short")
        
        #冲破三日高值就暂时平仓
        for i in range(1, self._getHiddenParam3() + 1):
            foreClose = theKLineList.getKLine(theSub - i).close()
            foreHeight2 = theHigh2 - theLow2
            if theClose > foreClose + foreHeight2 and (
                theTransaction is not None and theTransaction.isLong()):
                return Action("pingduo")
            elif theClose < foreClose - foreHeight2 and (
                theTransaction is not None and theTransaction.isShort()):
                return Action("pingkong")
        
            
        if theClose > theHigh1 and (
            theTransaction is not None and theTransaction.isShort()):
            return Action("pingkong")
        elif theClose < theLow1 and (
            theTransaction is not None and theTransaction.isLong()):
            return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.ChannelOfCloseIndex(self.getParam1())
        fici2 = futureindex.ChannelOfCloseIndex(self.getParam2())
        self.channelList1 = fici1.cal(theKLineList, 1)
        self.channelList2 = fici2.cal(theKLineList, 1)
        
        
class ChannelCloseExtraStrategy03(Strategy):
    '''
    海龟交易法的交易策略类，仅包含一个长通道天数参数param1（用于开仓）,和短通道天数参数param2(用于平仓)
    在向上突破通道时发出"long"信号，
    在向下突破通道时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList1 = self.channelList1
        theIndexList2 = self.channelList2
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh1 = theIndexList1[theSub][0]
        theLow1 = theIndexList1[theSub][1]
        theHigh2 = theIndexList2[theSub][0]
        theLow2 = theIndexList2[theSub][1]
        
        
        if theClose > theHigh1:
            return Action("long")
        elif theClose < theLow1:
            return Action("short")
        elif theClose > theHigh2:
            return Action("pingkong")
        elif theClose < theLow2:
            return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.ChannelOfCloseIndex(self.getParam1())
        fici2 = futureindex.ChannelOfCloseIndex(self.getParam2())
        self.channelList1 = fici1.cal(theKLineList, 1)
        self.channelList2 = fici2.cal(theKLineList, 1)
        
        
        
class ChannelCloseExtraStrategy04(Strategy):
    '''
    通道突破交易策略类04，包含一个短日期参数param1，和一个长日期参数param2，具体策略如下：
    
    (1)区间：无动作（无持仓）；无动作（持多仓）；平空（持空仓）
    ------------------high2
    (2)区间：开空（无持仓）；平多反手（持多仓）；无（持空仓）
    ------------------high1
    (3)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------均线
    (4)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------low1
    (5)区间：开多（无持仓）；无（持多仓）；平空反手（持空仓）
    ------------------low2
    (6)区间：无动作（无持仓）；平多（持多仓）；无（持空仓）
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):        
        noSigCount = self.getMaxParam() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh1 = self.channelList1[theSub][0]
        theLow1 = self.channelList1[theSub][1]
        theHigh2 = self.channelList2[theSub][0]
        theLow2 = self.channelList2[theSub][1]
        
        if theClose >= theHigh2:
            return Action("pingkong")
        elif theClose <= theLow2:
            return Action("pingduo")
        elif theClose > theHigh1 and theClose < theHigh2:
            return Action("short")
        elif theClose < theLow1 and theClose > theLow2:
            return Action("long")
            
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好2个通道'''
        fi1 = futureindex.ExpectedIndex(self.getParam1())
        fi2 = futureindex.ExpectedIndex(self.getParam2())
        self.channelList1 = fi1.cal(theKLineList, 1)   
        self.channelList2 = fi2.cal(theKLineList, 1)
        
        
            
class RsiStrategy(Strategy):
    '''
    Rsi超买超卖摸顶抄底的交易策略类，包含一个Rsi指标天数参数param1,和相对超买超卖水平线param2，还有一个隐藏参数止损价
    在超卖时发出"long"信号，
    在超买时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.rsiList
        theCriticalLine = self.getParam2()
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if theIndexList[theSub] > 50 + theCriticalLine:
            return Action("short")
        elif theIndexList[theSub] < 50 - theCriticalLine:
            return Action("long")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.RsiIndex(self.getParam1())
        self.rsiList = fici.cal(theKLineList, 0)

         
class RsiStrategy02(Strategy):
    '''
    Rsi的趋势跟随交易策略类，包含一个Rsi指标天数参数param1,和相对超买超卖水平线param2
    在rsi高过超买水平线时发出"long"信号，
    在rsi低于超卖水平线时发出"short"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.rsiList
        theCriticalLine = self.getParam2()
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if theIndexList[theSub] > 50 + theCriticalLine:
            return Action("long")
        elif theIndexList[theSub] < 50 - theCriticalLine:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.RsiIndex(self.getParam1())
        self.rsiList = fici.cal(theKLineList, 0)
          
          
class RsiStrategy03(Strategy):
    '''
    Rsi的趋势跟随交易策略类，包含一个Rsi指标天数参数param1,和相对超买超卖水平线param2
    在rsi高过超买水平线时发出"long"信号，
    在rsi低于超卖水平线时发出"short"信号，
    在rsi处于50~超买水平线时发"pingkong"信号，
    在rsi处于超卖水平线~50时发"pingduo"信号，
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.rsiList
        theCriticalLine = self.getParam2()
        noSigCount = self.getMaxParam() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if theIndexList[theSub] > 50 + theCriticalLine:
            return Action("long")
        elif theIndexList[theSub] < 50 - theCriticalLine:
            return Action("short")
        elif theIndexList[theSub] > 50:
            return Action("pingkong")
        elif theIndexList[theSub] < 50:
            return Action("pingduo")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.RsiIndex(self.getParam1())
        self.rsiList = fici.cal(theKLineList, 0)     
    
   
class ChannelRsiStrategy(Strategy):
    '''
    通道突破交易策略类，在开仓时考虑Rsi水平，包含一个通道天数(rsi共用)参数param1,和rsi水平param2
    在向上突破通道时，如果rsi低于50+param2，则发出"long"信号，否则发出"pingkong"信号
    在向下突破通道时，如果rsi高于50-param2，则发出"short"信号，否则发出"pingduo"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList1 = self.channelList
        theIndexList2 = self.rsiList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh = theIndexList1[theSub][0]
        theLow = theIndexList1[theSub][1]
        if theClose > theHigh:
            if theIndexList2[theSub] <= 50 + self.getParam2():
                return Action("long")
            else:
                return Action("pingkong")
        elif theClose < theLow:
            if theIndexList2[theSub] >= 50 - self.getParam2():
                return Action("short")
            else:
                return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.ChannelOfCloseIndex(self.getParam1())
        fici2 = futureindex.RsiIndex(self.getParam1())
        self.channelList = fici1.cal(theKLineList, 1)
        self.rsiList = fici2.cal(theKLineList, 0)
        
           
class ChannelRsiStrategy02(Strategy):
    '''
    通道突破交易策略类，在开仓时考虑Rsi水平，包含一个通道天数(rsi共用)参数param1,和rsi水平param2
    在向上突破通道时，如果rsi低于50+param2，则发出"long"信号，否则发出"pingkong"信号
    在向下突破通道时，如果rsi高于50-param2，则发出"short"信号，否则发出"pingduo"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList1 = self.channelList
        theIndexList2 = self.rsiList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh = theIndexList1[theSub][0]
        theLow = theIndexList1[theSub][1]
        if theClose > theHigh:
            if theIndexList2[theSub] > 50 + self.getParam2():
                return Action("long")
            else:
                return Action("pingkong")
        elif theClose < theLow:
            if theIndexList2[theSub] < 50 - self.getParam2():
                return Action("short")
            else:
                return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.ChannelOfCloseIndex(self.getParam1())
        fici2 = futureindex.RsiIndex(self.getParam1())
        self.channelList = fici1.cal(theKLineList, 1)
        self.rsiList = fici2.cal(theKLineList, 0)
        
        
        
        
        
                    
class RandomStrategy01(Strategy):
    '''
    用作对比测试的随机开仓策略，包含一个开仓概率参数param1,和止损倍数参数param2
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = 20 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        if (theTransaction is not None) and theTransaction.isLong():
            #当前是多头
            if theTransaction.isOverLoss(theClose, self.stopLossRate):
                return Action("pingduo")
        elif (theTransaction is not None) and theTransaction.isShort():
            #当前是空头
            if theTransaction.isOverLoss(theClose, self.stopLossRate):
                return Action("pingkong")
        if (theTransaction is None):
            judge = random.randint(1,100)
            if judge > 100 - self.openRate:
                return Action("long")
            elif judge <= self.openRate:
                return Action("short")
            else:
                return Action("none")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''啥指标都不用准备'''
        self.openRate = self.getParam1() #第三个参数就是止损比例
        self.stopLossRate = float(self.getParam2()) #第三个参数就是止损比例
        
        
                          
class MacdStrategy01(Strategy):
    '''
    用macd指标来交易
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = 27 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theMacd = self.macdList[theSub][2]
        if (theTransaction is not None) and theTransaction.isLong():
            #当前是多头
            if theMacd < 0:
                return Action("pingduo")
        elif (theTransaction is not None) and theTransaction.isShort():
            #当前是空头
            if theMacd > 0:
                return Action("pingkong")
            
        theDiff = self.macdList[theSub][0]
        if theTransaction is None:
            if theDiff > 0 and theMacd > 0:
                return Action("long")
            elif theDiff < 0 and theMacd < 0:
                return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''准备一套标准12,26,9的macd指标就好'''
        fi = futureindex.MacdIndex(12,26,9)
        self.macdList = fi.cal(theKLineList)



class ChannelMacdStrategy(Strategy):
    '''
    通道突破交易策略类，在开仓时考虑macd（使用默认参数12,26,9）的diff水平，包含一个通道天数参数param1
    在向上突破通道时，如果diff > 0，则发出"long"信号，否则发出"pingkong"信号
    在向下突破通道时，如果diff < 0，则发出"short"信号，否则发出"pingduo"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.channelList
        noSigCount = self.getMaxParam() #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theHigh = theIndexList[theSub][0]
        theLow = theIndexList[theSub][1]
        theDiff = self.macdList[theSub][0]
        if theClose > theHigh:
            if theDiff > 0:
                return Action("long")
            else:
                return Action("pingkong")
        elif theClose < theLow:
            if theDiff < 0:
                return Action("short")
            else:
                return Action("pingduo")
        else:
            return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        ficc = futureindex.ChannelOfCloseIndex(self.getParam1())
        self.channelList = ficc.cal(theKLineList, 1)
        fi = futureindex.MacdIndex(12,26,9)
        self.macdList = fi.cal(theKLineList)
        
        
     
class BollStrategy(Strategy):
    '''
    Boll通道突破交易策略类，包含一个通道天数参数param1，和一个标准差水平参数param2
    在向上突破Boll通道上轨时,发出"long"信号
    在向下突破Boll通道下轨时，发出"short"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theEx = self.expectedList[theSub][0]
        theSdx = self.expectedList[theSub][1]
        theHigh = theEx + theSdx * self.getParam2() / 10
        theLow = theEx - theSdx * self.getParam2() / 10
        if theClose > theHigh:
            return Action("long")
        elif theClose < theLow:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fi = futureindex.ExpectedIndex(self.getParam1())
        self.expectedList = fi.cal(theKLineList, 1)
        
        

     
class BollStrategy02(Strategy):
    '''
    Boll通道突破交易策略类02，包含一个标准差水平参数param1，和一个标准差水平参数param2，具体策略如下：
    
    (1)区间：无动作（无持仓）；平多（持多仓）；无动作（持空仓）
    ------------------high2
    (2)区间：开多（无持仓）；无动作（持多仓）；平空反手（持空仓）
    ------------------high1
    (3)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------均线
    (4)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------low1
    (5)区间：开空（无持仓）；平多反手（持多仓）；无动作（持空仓）
    ------------------low2
    (6)区间：无动作（无持仓）；无动作（持多仓）；平空（持空仓）
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        if self.getParam1() >= self.getParam2():#param1必须小于param2
            return Action("none")
        
        noSigCount = 27 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theEx = self.expectedList[theSub][0]
        theSdx = self.expectedList[theSub][1]
        theHigh1 = theEx + theSdx * self.getParam1() / 10
        theLow1 = theEx - theSdx * self.getParam1() / 10
        theHigh2 = theEx + theSdx * self.getParam2() / 10
        theLow2 = theEx - theSdx * self.getParam2() / 10
        
        if theClose > theHigh2:
            return Action("pingduo")
        elif theClose < theLow2:
            return Action("pingkong")
        elif theClose > theHigh1 and theClose < theHigh2:
            return Action("long")
        elif theClose < theLow1 and theClose > theLow2:
            return Action("short")
            
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好26日布林通道'''
        fi = futureindex.ExpectedIndex(26)
        self.expectedList = fi.cal(theKLineList, 1)           
        
        
class BollStrategy03(Strategy):
    '''
    Boll通道突破交易策略类03，包含一个标准差水平参数param1，和一个标准差水平参数param2，具体策略如下：
    
    (1)区间：无动作（无持仓）；无动作（持多仓）；平空（持空仓）
    ------------------high2
    (2)区间：开空（无持仓）；平多反手（持多仓）；无（持空仓）
    ------------------high1
    (3)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------均线
    (4)区间：无动作（无持仓）；无动作（持多仓）；无动作（持空仓）
    ------------------low1
    (5)区间：开多（无持仓）；无（持多仓）；平空反手（持空仓）
    ------------------low2
    (6)区间：无动作（无持仓）；平多（持多仓）；无（持空仓）
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):        
        noSigCount = 21 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theEx1 = self.expectedList1[theSub][0]
        theSdx1 = self.expectedList1[theSub][1]
        theEx2 = self.expectedList2[theSub][0]
        theSdx2 = self.expectedList2[theSub][1]
        theHigh1 = theEx1 + theSdx1 * self.getParam1() / 10
        theLow1 = theEx1 - theSdx1 * self.getParam1() / 10
        theHigh2 = theEx2 + theSdx2 * self.getParam2() / 10
        theLow2 = theEx2 - theSdx2 * self.getParam2() / 10
        
        if theClose >= theHigh2:
            return Action("pingkong")
        elif theClose <= theLow2:
            return Action("pingduo")
        elif theClose > theHigh1 and theClose < theHigh2:
            return Action("short")
        elif theClose < theLow1 and theClose > theLow2:
            return Action("long")
            
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好5日，20日布林通道'''
        fi1 = futureindex.ExpectedIndex(5)
        fi2 = futureindex.ExpectedIndex(20)
        self.expectedList1 = fi1.cal(theKLineList, 1)   
        self.expectedList2 = fi2.cal(theKLineList, 1)        
        

     
class BollPromotingStrategy(Strategy):
    '''
    Boll通道突破交易策略类的一个变种，将一起考虑开盘价、最高价、最低价、收盘价，并且收盘价作为重要价位将会加权作为双份来计算，
    包含一个通道天数参数param1，和一个标准差水平参数param2
    在向上突破Boll通道上轨时,发出"long"信号
    在向下突破Boll通道下轨时，发出"short"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theEx = self.expectedList[theSub][0]
        theSdx = self.expectedList[theSub][1]
        theHigh = theEx + theSdx * self.getParam2() / 10
        theLow = theEx - theSdx * self.getParam2() / 10
        if theClose > theHigh:
            return Action("long")
        elif theClose < theLow:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fi = futureindex.ExpectedPromotingIndex(self.getParam1())
        self.expectedList = fi.cal(theKLineList, 1)



class ChannelAndBollStrategy(Strategy):
    '''
    简单通道突破结合Boll通道突破交易策略类，包含一个简单通道天数参数param1，和一个Boll通道天数参数param2
    在向上突破简单通道，且同时突破Boll通道上轨时,发出"long"信号
    在向下突破简单通道，且同时突破Boll通道下轨时，发出"short"信号
 
    其他时候发"none"信号
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = self.getMaxParam() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        theClose = theKLineList.getKLine(theSub).close()
        theChannelHigh = self.channelList[theSub][0]
        theChannelLow = self.channelList[theSub][1]
        theEx = self.expectedList[theSub][0]
        theSdx = self.expectedList[theSub][1]
        theExpectedHigh = theEx + theSdx * self._getHiddenParam3() / 10
        theExpectedLow = theEx - theSdx * self._getHiddenParam3() / 10
        if theClose > theChannelHigh and theClose > theExpectedHigh:
            return Action("long")
        elif theClose < theChannelLow and theClose < theExpectedLow:
            return Action("short")
        elif theClose > theChannelHigh:
            return Action("pingkong")
        elif theClose < theChannelLow:
            return Action("pingduo")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fi = futureindex.ChannelOfCloseIndex(self.getParam1())
        self.channelList = fi.cal(theKLineList, 1)   
        fi = futureindex.ExpectedIndex(self.getParam2())
        self.expectedList = fi.cal(theKLineList, 1)   
        
        
        
        
        
        
        
        
        
    
class SimpleKLineStrategy01(Strategy):
    '''
    简单的红绿K线交易策略类，仅包含一个通道天数参数param1, 和需要超过（含）半数多少根的参数param2
    交易方式类似RsiStrategy02
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.attackList
        exceedNum = self.getParam2()
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if theIndexList[theSub][0] >= self.getParam1() / 2 + exceedNum:
            return Action("long")
        elif theIndexList[theSub][1] >= self.getParam1() / 2 + exceedNum:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.AttackIndex01(self.getParam1())
        self.attackList = fici.cal(theKLineList, 0)
        

class SimpleKLineStrategy02(Strategy):
    '''
    简单的红绿K线交易策略类，仅包含一个通道天数参数param1, 和多空攻击力水平的参数param2
    交易方式类似RsiStrategy02
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        theIndexList = self.attackList
        exceedLine = self.getParam2()
        noSigCount = self.getParam1() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if theIndexList[theSub] > 50 + exceedLine:
            return Action("long")
        elif theIndexList[theSub] < 50 - exceedLine:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici = futureindex.AttackIndex02(self.getParam1())
        self.attackList = fici.cal(theKLineList, 0)
        
        
        
class MaCrossStrategy01(Strategy):
    '''
    短长期均线金叉死叉交易策略类，包含一个短期均线日期参数param1, 和长期均线日期参数param2
    '''
    
    def signal(self, theKLineList, theSub, theTransaction):
        noSigCount = self.getParam2() + 1 #禁止交易的前期时间
        if theSub < noSigCount:
            return Action("none")
        
        if self.maList1[theSub] > self.maList2[theSub] and self.maList1[theSub - 1] <= self.maList2[theSub - 1]:
            return Action("long")
        elif self.maList1[theSub] < self.maList2[theSub] and self.maList1[theSub - 1] >= self.maList2[theSub - 1]:
            return Action("short")
        return Action("none")
    
    def prepareIndexList(self, theKLineList):
        '''需要预先准备好channelList'''
        fici1 = futureindex.MaIndex(self.getParam1())
        fici2 = futureindex.MaIndex(self.getParam2())
        self.maList1 = fici1.cal(theKLineList, 0)
        self.maList2 = fici2.cal(theKLineList, 0)
        
        
        
        
    