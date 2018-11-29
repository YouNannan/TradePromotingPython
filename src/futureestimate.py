'''
Created on 2018年10月2日

@author: You Nannan
'''


import futuretrade
import datetime
import futurecommodity
import futuretools
import math

__RESULT_DIR = "../result"

__GEOMETRIC_POSITION = (0.01, 0.02, 0.03, 0.04, 0.05)
__DEFAULT_COST = 0.03#滑点和佣金

def reportAnnually01(beginYear, endYear, strategy, 
                     commodityList = futurecommodity.getCommodityList(), #交易的商品代码列表，默认为所有商品
                     isAnnualNeeded = True, #是否需要生成分年度的子报告文件
                     isTransactionDetailAdded = False, #是否需要在每份年度子报告末尾附上每笔交易记录，需要isAnnualNeeded同时开启方有效
                     maxHoldDays = 60, maxLossRate = 10000.0):
    futurecommodity.setDataDirAfterVerified()
    if commodityList is None:
        commodityList = futurecommodity.getCommodityList()
    
    endDate = datetime.datetime(endYear, 1, 1)
    finalProfit = 0.0
    finalDuration = 0
    finalCount = 0
    finalInfo = ""
    profitPerCommodityDict = {}#存放各品种毛利的字典
    durationSumPerCommodityDict = {}#存放各品种持仓日期的字典
    transCountPerCommodityDict = {}#存放各品种持仓日期的字典
    for commodity in commodityList:
        profitPerCommodityDict[commodity] = 0.0
        durationSumPerCommodityDict[commodity] = 0.0
        transCountPerCommodityDict[commodity] = 0
    
    #用于计算收益的几何级数
    geometricProfitDict = []
    geometricProfitDict.append({})
    geometricProfitDict.append(0)
    for position in __GEOMETRIC_POSITION:
        geometricProfitDict[0][position] = [1.0, 1.0]
        
    while beginYear < endYear:
        beginDate = datetime.datetime(beginYear, 1, 1)
        endDate = datetime.datetime(beginYear + 1, 1, 1)
        tc = futuretrade.TradeCenter(beginDate, endDate, maxHoldDays, maxLossRate)#有1.0止损
        for commodity in commodityList:
            tc.addCommodity(commodity)
        tc.setStrategy(strategy)
        transactionDict = tc.trade()
        profitSumTotal = 0.0
        durationSumTotal = 0
        transCount = 0
        resultInfo = ""
        for commodity in transactionDict.keys():
            profitSumCommodity = 0.0
            durationSumCommodity = 0
            if len(transactionDict[commodity]) == 0:
                continue
            for theTrans in transactionDict[commodity]:
                profitSumCommodity += theTrans.getProfitRate()
                durationSumCommodity += theTrans.getDuration()
            count = len(transactionDict[commodity])
            profitSumTotal += profitSumCommodity
            durationSumTotal += durationSumCommodity
            profitPerCommodityDict[commodity] += profitSumCommodity
            durationSumPerCommodityDict[commodity] += durationSumCommodity
            transCountPerCommodityDict[commodity] += count
            resultInfo += __formatInfo(commodity, profitSumCommodity, durationSumCommodity, count)
            transCount += count
            
        geometricProfitDict[1] += 1
        if transCount == 0:
            beginYear += 1
            continue
        
        tempInfo = __formatInfo("汇总", profitSumTotal, durationSumTotal, transCount)
        resultInfo += "\n" + tempInfo
        finalInfo += str(beginYear) + "年度" + tempInfo
        finalProfit += profitSumTotal
        finalDuration += durationSumTotal
        finalCount += transCount
        for position in __GEOMETRIC_POSITION:
            grossTemp = 1 + profitSumTotal * position
            netTemp = 1 + (profitSumTotal - __DEFAULT_COST * transCount) * position
            if grossTemp < 0.0:
                grossTemp = 0.0
            if netTemp < 0.0:
                netTemp = 0.0
            geometricProfitDict[0][position][0] *= grossTemp
            geometricProfitDict[0][position][1] *= netTemp
        if isAnnualNeeded is True:
            if isTransactionDetailAdded is True:
                resultInfo += "\n详细交易记录附表：\n" + __formatDict(transactionDict)
            futuretools.writeListToFile(__RESULT_DIR + "/" + str(beginYear) + "年度报告.txt",
                                     resultInfo, False)
        
        beginYear += 1
    
    filename = (__RESULT_DIR + "/" + futuretools.getClassName(strategy) + "_"
                                + format(strategy.getParam1(),"0>2d") + "_"
                                + format(strategy.getParam2(),"0>2d"))
    if maxLossRate < 10.0:
        filename += "_" + format(maxLossRate, "0.1f") + "止损"
    else:
        filename += "_无止损"
    
    tempInfo = "全交易周期" + __formatInfo("汇总", finalProfit, finalDuration, finalCount, __DEFAULT_COST, geometricProfitDict)
    finalInfo += "\n" + tempInfo + "\n\n[各品种详情]：\n"
    for commodity in commodityList:
        finalInfo += __formatInfo(commodity, profitPerCommodityDict[commodity],
                                  durationSumPerCommodityDict[commodity],
                                  transCountPerCommodityDict[commodity])
    returnInfo = format(filename[filename.rfind("/") + 1:], "<45") + tempInfo
    filename += "_汇总报告.txt"
    futuretools.writeListToFile(filename, finalInfo, False)
    return returnInfo
    
def reportParamAnalysis(beginYear, endYear, strategy,
                        commodityList, #交易的商品代码列表，默认为所有商品
                        param1Begin, param1End, param1Step = 1,
                        param2Begin = 0, param2End = 1, param2Step = 1,
                        maxHoldDays = 60, maxLossRate = 10000.0
                     ):
    '''生成参数分析报告'''
    resultInfo = ""
    for theParam1 in range(param1Begin, param1End, param1Step):
        strategy.setParam1(theParam1)
        if strategy.getParam2() == 0:
            annuallyInfo = reportAnnually01(beginYear, endYear, strategy, 
                commodityList, False, False,
                maxHoldDays, maxLossRate)
            resultInfo += annuallyInfo
            continue
            
        for theParam2 in range(param2Begin, param2End, param2Step):
            strategy.setParam2(theParam2)
            annuallyInfo = reportAnnually01(beginYear, endYear, strategy, 
                commodityList, False, False,
                maxHoldDays, maxLossRate)
            resultInfo += annuallyInfo
            
    filename = __RESULT_DIR + "/" + futuretools.getClassName(strategy)
    if maxLossRate < 10.0:
        filename += "_" + format(maxLossRate, "0.1f") + "止损"
    else:
        filename += "_无止损"
    filename += "_参数分析报告.txt"
    futuretools.writeListToFile(filename, resultInfo, False)

'''   
def reportCommodityFeature01(beginYear, endYear,
                     commodityList = futurecommodity.getCommodityList()):
    futurecommodity.setDataDirAfterVerified()
    if commodityList is None:
        commodityList = futurecommodity.getCommodityList()
    beginDate = datetime.datetime(beginYear, 1, 1)
    endDate = datetime.datetime(endYear, 1, 1)
'''

def __formatDict(transactionDict):
    resultString = ""
    for commodityCode in transactionDict.keys():
        resultString += commodityCode + " 共 " + str(len(transactionDict[commodityCode])) + " 笔交易:\n"
        for transaction in transactionDict[commodityCode]:
            resultString += str(transaction) + "\n"
        resultString += "\n"
    return resultString
        
def __formatInfo(theHeadStr, theGrossProfit, theDurationSum, theCount, theCost = __DEFAULT_COST, theGeometricProfitDict = None):
    if theCount == 0:
        averageGrossProfit = 0.0
        averageDuration = 0.0
    else:
        averageGrossProfit = theGrossProfit / theCount
        averageDuration = float(theDurationSum) / theCount
    averageNetProfit = averageGrossProfit - theCost
    netProfit = averageNetProfit * theCount
    geometricInfo = ""
    if theGeometricProfitDict is not None:
        geometricInfo = "\n资金几何级数：\n"
        for position in __GEOMETRIC_POSITION:
            geometricInfo += ("仓位" + format(position, "0.2f")
                              + "， 总资金(按毛利计算):" + format(format(theGeometricProfitDict[0][position][0], ".4f"),">9")
                              + "，年度化收益率(毛利)" + format(format(100 * (math.pow(theGeometricProfitDict[0][position][0]
                                                                  , 1.0 / theGeometricProfitDict[1]) - 1), ".2f"),">5")
                              + "%  ； 总资金(按净利计算):" + format(format(theGeometricProfitDict[0][position][1], ".4f"),">9")
                              + "，年度化收益率(净利)" + format(format(100 * (math.pow(theGeometricProfitDict[0][position][1]
                                                                  , 1.0 / theGeometricProfitDict[1]) - 1), ".2f"),">5") + "%\n")
        
    theInfo = (format(theHeadStr, ">2") + ": " + format(theCount, ">4d")
            + " 笔交易, 总毛利:" + format(format(theGrossProfit, ".4f"),">9")
            + ", 平均每笔毛利: = " + format(format(averageGrossProfit, ".4f"),">7")
            + ", 平均持仓天数: = " + format(format(averageDuration, ".2f"),">5") + "天"
            + ", 每笔扣除" + format(theCost, ".2f") + "交易费用后平均净利:"
            + format(format(averageNetProfit, ".4f"),">7")
            + ", 总净利: = " + format(format(netProfit, "0.4f"),">9")
            + geometricInfo + "\n")
    return theInfo
    
