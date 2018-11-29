'''
Created on 2018年9月27日



@author: You Nannan
'''
import futurecommodity
import futuretools
import datetime
import futurestrategy





class TradeCenter(object):
    '''
    用来进行具体交易的类，其中有很多参数可以配置
    '''
    
    __DEFAULT_MAX_HOLD_DAYS = 60 #默认最高的持仓天数,是正常过的天数，不是交易日天数
    __DEFAULT_MAX_ACCEPTABLE_LOSS = 10000.0 #默认最高允许的亏损值，即默认不止损
    __MIN_TRADE_VOL = 10000 #能够开仓的合约的要求最小成交量
    #__DEFAULT_IS_YICANGHUANYUE = False #默认不移仓换月，在主力合约切换时，直接平掉老合约，不开新合约

    def __init__(self, theBeginDate, theEndDate,
                 theMaxHoldDays = __DEFAULT_MAX_HOLD_DAYS, 
                 theMaxAcceptableLoss = __DEFAULT_MAX_ACCEPTABLE_LOSS):
        #,theIsYicanghuanyue = __DEFAULT_IS_YICANGHUANYUE):
        '''在[beginDate,endDate)之间的时间段交易，
        maxHoldDays是最高的持仓天数，持仓超过此值将会自动平仓
        maxAcceptableLoss是可以接受的最高亏损值（用于和Transaction.getProfitRate()相比较）
        '''
        self.beginDate = theBeginDate
        self.endDate = theEndDate
        self.__commodityCodeList = []
        self.maxHoldDays = theMaxHoldDays
        self.maxAcceptableLoss = theMaxAcceptableLoss
        #self.isYicanghuanyue = theIsYicanghuanyue
        
    def setCommodity(self, theCommodityCode):
        '''设置要交易的商品，如果传入空串""，则表示要交易全部的商品'''
        if len(theCommodityCode) > 0:
            self.__commodityCodeList = []
            self.__commodityCodeList.append(theCommodityCode)
        else:
            self.__commodityCodeList = futurecommodity.getCommodityList()
            
    def addCommodity(self, theCommodityCode):
        self.__commodityCodeList.append(theCommodityCode)
        
    def setStrategy(self, theStrategy):
        self.__strategy = theStrategy
        
    
    def __isTransOverLoss(self, thePrice, transaction):
        '''如果超过止损价则返回[True, info]'''
        if transaction is None:
            return [False, "/"]
        if transaction.isOverLoss(thePrice, self.maxAcceptableLoss):
            if transaction.isLong():
                maxLossPrice = transaction.openPrice - self.maxAcceptableLoss * (
                    transaction.openPrice / transaction.lever)
                theInfo = "跌破止损价(" + str(maxLossPrice) + "),强制平仓"
            else:
                maxLossPrice = transaction.openPrice + self.maxAcceptableLoss * (
                    transaction.openPrice / transaction.lever)
                theInfo = "涨破止损价(" + str(maxLossPrice) + "),强制平仓"
            return [True, theInfo]
        else:
            return [False, "/"]
            
        
    def __isTransOverDays(self, theDate, transaction):
        '''如果超过持仓天数则返回[True, info](达到第maxHoldDays天的当天并不视为超出)'''
        if transaction is None:
            return [False, "/"]
        if transaction.openTime + datetime.timedelta(days=self.maxHoldDays) < theDate:
            return [True, "超过最大持仓天数(" + str(self.maxHoldDays) + "天),强制平仓"]
        else:
            return [False, "/"]
        
        
    def __isTransNotMainContract(self, theContractName, theDate):
        '''如果该合约不是主力合约则返回[True, info]'''
        mainContractName = futurecommodity.getMainContractName(
                        theContractName[0:-4], theDate)
        if mainContractName != theContractName:
            return [True, "主力合约已经换为" + str(mainContractName) + ",强制平仓"]
        else:
            return [False, "/"]
         
    def __isContractNearExpire(self, theContractName, theDate):
        '''如果该合约快到期（如J1805在进入1804月份时就算快到期）则返回[True, info]'''
        yearAndMonth = theDate.strftime("%Y%m")
        dateYear = int(yearAndMonth[2:4])
        dateMonth = int(yearAndMonth[4:6])
        contractYear = int(theContractName[-4:-2])
        contractMonth = int(theContractName[-2:])
        if (dateYear * 12 + dateMonth + 1) >= (contractYear * 12 + contractMonth):
            return [True, "该合约" + theContractName + "快到期啦，强制平仓"]
        else:
            return [False, "/"]
    
    def __isHaveToCloseTrans(self, theDate, theContractName, thePrice, transaction):
        '''综合__isTransOverDays，__isTransOverLoss和__isTransNotMainContract，
        如果有一个返回True，则返回True
        '''
        result1 = self.__isTransOverLoss(thePrice, transaction)
        result2 = self.__isTransOverDays(theDate, transaction)
        result3 = self.__isTransNotMainContract(theContractName, theDate)
        result4 = self.__isContractNearExpire(theContractName, theDate)
        if result1[0]:
            return result1
        elif result2[0]:
            return result2
        elif result3[0]:
            return result3
        elif result4[0]:
            return result4
        else:
            return [False, "/"]
    
    def __isAbleToTrade(self, isOpen, direction, kLineList, i):
        '''KLineList的第i根K线是否满足交易条件，返回True表示可以交易，False表示不可以
        isOpen表示是否为开仓操作（开仓为True,平仓为False），direction表示是多仓还是空仓
        '''
        if isOpen is True:
            if kLineList.getKLine(i).vol() < TradeCenter.__MIN_TRADE_VOL:
                return False
            if direction == DIRECTION_LONG:
                if kLineList.isLimitUp(i):
                    return False
                else:
                    return True
            else:
                if kLineList.isLimitDown(i):
                    return False
                else:
                    return True
                
        else:
            if direction == DIRECTION_LONG:
                if kLineList.isLimitDown(i):
                    return False
                else:
                    return True
            else:
                if kLineList.isLimitUp(i):
                    return False
                else:
                    return True
            
    
    '''#用于测试futuretradetest.testName01
    def isHaveToCloseTransTest(self, theDate, theContractName, thePrice, transaction):
        return self.__isHaveToCloseTrans(theDate, theContractName, thePrice, transaction)
    '''
               
               
    def trade(self):
        '''根据指定的时间、品种、交易策略，返回生成的交易记录字典'''
        transactionDict = {}
        for theCommodityCode in self.__commodityCodeList:
            theTransList = []
            dateList = futuretools.getDaysList(self.beginDate, self.endDate)
            contractName = futurecommodity.getMainContractName(
                theCommodityCode, dateList[0])
            if contractName is None:
                #如果在dateList[0]时没有一个主力合约，那么就要往后找到一个有主力合约的日子
                for theDate in dateList:
                    contractName = futurecommodity.getMainContractName(
                        theCommodityCode, theDate)
                    if contractName is not None:
                        break
                if contractName is None:
                    transactionDict[theCommodityCode] = []
                    continue
                dateList = futuretools.getDaysList(theDate, self.endDate)
                    
            theKLineList = futurecommodity.getContractKLineList(contractName)
            self.__strategy.prepareIndexList(theKLineList)
            transaction = None
            for theDate in dateList:
                if (transaction is None) and (contractName != futurecommodity.
                                getMainContractName(theCommodityCode, theDate)):
                    #如果主力合约换掉了，那么要重新刷新信号量
                    contractNameNext = futurecommodity.getMainContractName(
                        theCommodityCode, theDate)
                    if contractNameNext is None:
                        continue
                    contractName = contractNameNext
                    theKLineList = futurecommodity.getContractKLineList(contractName)
                    self.__strategy.prepareIndexList(theKLineList)
                    
                sub = theKLineList.getSubscript(theDate)
                if sub is None:
                    continue
                else:
                    lastSub = sub
                
                isHaveToCloseTrans = self.__isHaveToCloseTrans(theDate, contractName,
                    theKLineList.getKLine(sub).close(), transaction)
                if (transaction is not None) and (isHaveToCloseTrans[0]):
                    #如果因交易设置原因必须平仓则平仓
                    if self.__isAbleToTrade(False, transaction.getDirection(), theKLineList, sub):
                        transaction.close(theDate, theKLineList.getKLine(sub).close(),
                                          isHaveToCloseTrans[1])
                        theTransList.append(transaction)
                        transaction = None
                
                if (contractName != futurecommodity.getMainContractName(
                    theCommodityCode, theDate)) and (transaction is None):
                    #如果主力合约换掉了，那么要重新刷新信号量
                    contractName = futurecommodity.getMainContractName(
                        theCommodityCode, theDate)
                    theKLineList = futurecommodity.getContractKLineList(contractName)
                    self.__strategy.prepareIndexList(theKLineList)
                    sub = theKLineList.getSubscript(theDate)
                    if sub is None:
                        continue
                    else:
                        lastSub = sub
                
                if transaction is None:
                    #如果当前没有仓位
                    if self.__isContractNearExpire(contractName, theDate)[0]:
                        continue
                    tradeSignal = self.__strategy.signal(theKLineList, sub, transaction)
                    if tradeSignal.isLong() or tradeSignal.isShort():
                        if self.__isAbleToTrade(True, tradeSignal.getOpenDirection(), theKLineList, sub):
                            transaction = Transaction(contractName, theDate, 
                                    theKLineList.getKLine(sub).close(), tradeSignal)
                elif transaction.isLong():
                    #如果当前是多头
                    tradeSignal = self.__strategy.signal(theKLineList, sub, transaction)
                    if tradeSignal.isShort():
                        if self.__isAbleToTrade(False, DIRECTION_LONG, theKLineList, sub):
                            transaction.close(theDate, theKLineList.getKLine(sub).close(),
                                        "空头信号，平多仓")
                            theTransList.append(transaction)
                            if self.__isContractNearExpire(contractName, theDate
                                                        )[0] is False:
                                transaction = Transaction(contractName, theDate, 
                                        theKLineList.getKLine(sub).close(), tradeSignal)
                    elif tradeSignal.isPingduo():
                        if self.__isAbleToTrade(False, DIRECTION_LONG, theKLineList, sub):
                            transaction.close(theDate, theKLineList.getKLine(sub).close(),
                                        "平多信号，平多仓")
                            theTransList.append(transaction)
                            transaction = None
                else:
                    #如果当前是空头
                    tradeSignal = self.__strategy.signal(theKLineList, sub, transaction)
                    if tradeSignal.isLong():
                        if self.__isAbleToTrade(False, DIRECTION_SHORT, theKLineList, sub):
                            transaction.close(theDate, theKLineList.getKLine(sub).close(),
                                        "多头信号，平空仓")
                            theTransList.append(transaction)
                            if self.__isContractNearExpire(contractName, theDate
                                                        )[0] is False:
                                transaction = Transaction(contractName, theDate, 
                                        theKLineList.getKLine(sub).close(), tradeSignal)
                    elif tradeSignal.isPingkong():
                        if self.__isAbleToTrade(False, DIRECTION_SHORT, theKLineList, sub):
                            transaction.close(theDate, theKLineList.getKLine(sub).close(),
                                        "平空信号，平空仓")
                            theTransList.append(transaction)
                            transaction = None
            
            if transaction is not None:
                transaction.close(theKLineList.getKLine(
                    lastSub).time(), theKLineList.getKLine(
                    lastSub).close(),"已到交易时段的最后一天，平仓了结")
                theTransList.append(transaction)
            transactionDict[theCommodityCode] = theTransList
        return transactionDict
    
        
    


















DIRECTION_LONG = 1 #开多的方向
DIRECTION_SHORT = -1 #开空的方向

class Transaction(object):
    '''
    用于记录一笔交易的类，公共成员如下：
    self.contractName:交易的合约名
    self.openTime：开仓日期
    self.openPrice:开仓价
    self.closeTime：平仓日期
    self.closePrice:平仓价
    self.action:开仓动作，包含开仓方向和止损价的信息
    self.level:杠杆倍数
    '''
    __DEFAULT_LEVER = 10 #杠杆默认为10

    def __init__(self, theContractName,
                 theOpenTime, theOpenPrice, theAction,
                 theLever = __DEFAULT_LEVER):
        '''
        Constructor
        '''
        self.contractName = theContractName
        self.openTime = theOpenTime
        self.openPrice = theOpenPrice
        self.maxProfitPrice = theOpenPrice
        self.action = theAction
        self.lever = theLever
        self.closePrice = -1.0
        self.info = "/"
        
    def __repr__(self):
        theString = []
        theString.append(self.contractName)
        theString.append(self.openTime.strftime("%Y-%m-%d"))
        theString.append(self.openPrice)
        theString.append(self.closeTime.strftime("%Y-%m-%d"))
        theString.append(self.closePrice)
        theString.append(self.getDirectionChineseString())
        #theString.append(self.lever) #杠杆没人在意，不用输出了，改为输出持仓天数
        theString.append((self.closeTime - self.openTime).days)
        theString.append(self.info)
        theString.append(float(format(self.getProfitRate(), ".4f")))
        return repr(theString)
    def __str__(self):
        return self.__repr__()
        
    def close(self, theCloseTime, theClosePrice, theInfo):
        self.closeTime = theCloseTime
        self.closePrice = theClosePrice
        self.info = theInfo
        
    def isClosed(self):
        '''返回该交易是否关闭了，True为已关闭，False为没有'''
        if self.closePrice < 0:
            return False
        else:
            return True
        
    def getDirection(self):
        return self.action.getOpenDirection()
    def getDirectionChineseString(self):
        if self.isLong():
            return "多单"
        elif self.isShort():
            return "空单"
        else:
            raise Exception("有个单子既不是多也不是空！")
    def getLossPrice(self):
        return self.action.getLossPrice()
    def isLong(self):
        '''是多头就返回True，否则(空头)返回False'''
        return self.getDirection() == DIRECTION_LONG
    def isShort(self):
        '''是空头就返回True，否则(多头)返回False'''
        return self.getDirection() == DIRECTION_SHORT
    
    def isOverLoss(self, price, lossRate):
        '''当前价格是否突破了止损价(请注意，此处采用移动止损),lossRate是个正数'''
        if self.isLong() and price > self.maxProfitPrice:
            self.maxProfitPrice = price
        elif self.isShort() and price < self.maxProfitPrice:
            self.maxProfitPrice = price 
        
        theProfit = ((price - self.maxProfitPrice)
                 * self.getDirection() * self.lever / self.maxProfitPrice)
        if theProfit < -lossRate:
            return True
        else:
            return False
        
        
    def getProfitRate(self):
        '''以开仓价为分母来计算单笔利润率，与杠杆率theLever有关，
        此处不考虑单笔扣除的手续费加滑点，
        若交易未关闭则返回None
        '''
        if self.isClosed() is False:
            return None
        return ((self.closePrice - self.openPrice)
                 * self.getDirection() * self.lever / self.openPrice)
                 
                 
    def getDuration(self):
        '''返回持仓天数（实际日，而不是交易日）'''
        if self.isClosed() is False:
            return None
        return (self.closeTime - self.openTime).days
    
        

        
        
        