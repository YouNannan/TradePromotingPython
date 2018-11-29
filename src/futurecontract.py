#coding:utf-8
'''
Created on 2018年9月24日
有两个类
一。KLine类，基本的单根K线，包含如下方法：
    time():返回该K线timedate类型的时间，目前精确到days，不含小时分钟信息
    timeString():返回该K线的"%Y%m%d"格式的时间字串，如20180921
    open():返回float类型的开盘价
    high():返回float类型的最高价
    low():返回float类型的最低价
    close():返回float类型的收盘价
    vol():返回int类型的成交量
    

二。KLineList类，K线列表，包含一组K线，包含如下方法：
    getBeginTime():返回该K线列表中第一根K线的datetime类型的时间
    getEndTime():返回该K线列表中最后一根K线的datetime类型的时间
    getLen():返回该K线列表的K线数目，int类型
    getTimeList():返回该K线列表包含的所有日期的列表，list类型
    getCloseList():返回该K线列表包含的所有收盘价的列表，list类型
    getList():返回该K线列表包含的所有K线的列表，list类型
    getKLine(i):返回第i根K线，KLine类型
    getSubscript(theTime):返回时间为theTime的K线在列表中的下标，int类型，如果没找到就返回None
    isLimitUp(i):返回第i根K线是否收盘时涨停，True涨停，False没有
    isLimitDown(i):返回第i根K线是否收盘时跌停，True跌停，False没有
@author: You Nannan
'''

import datetime



class KLineList(object):
    '''
    K线列表，包含一组K线
    '''
    __LIMIT_JUDGE_WAVE = 0.03 #涨跌停判断幅度，大于此幅度即认为涨跌停

    def __init__(self, theList):
        '''
        theList就是直接从数据文件中读出的二维列表
        '''
        self.__list =[]
        for i in range(len(theList)):
            
            self.__list.append(KLine(theList[i]))
            
    def __repr__(self):
        return repr(self.__list)
    
    def __str__(self):
        return str(self.__list)
    
    def checkAndCorrectData(self, contractName):
        theInfo = {}
        klineBeDeleted = []
        for kline in self.__list:
            theYear = int(kline.timeString()[0:4])
            #theMonth = int(kline.timeString()[5:7])
            #contractYear = int(contractName[-4:-2])
            #contractMonth = int(contractName[-2:])
            if theYear > 2030 or theYear < 1980:
                theInfo[str(kline)] = "@01@此K线的年份超出了！"
                continue
            theYear = int(kline.timeString()[2:4])
            #if theYear == contractYear and theMonth == contractMonth:
                #最后交割月，一切皆有可能
                #continue
            if (kline.open() <= 0.0 
                or kline.high() <= 0.0 
                or kline.low() <= 0.0
                or kline.close() <= 0.0 
                #or kline.vol() <= 0
                ):
                theInfo[str(kline)] = "@02@此K线中出现了零或负值！验证后的K线图将不含此根K线"
                klineBeDeleted.append(kline)
                continue
            if (kline.open() > kline.high() or kline.open() < kline.low()
                or kline.close() > kline.high() or kline.close() < kline.low()
                or kline.high() < kline.low()):
                #theInfo[str(kline)] = "@03@此K线数据大小不规整！"
                continue
            
        for kline in klineBeDeleted:
            self.__list.remove(kline)
            
        lastKline = self.__list[0]
        for kline in self.__list:
            if (kline.open() > lastKline.close() * 1.3 
                or kline.open() < lastKline.close() * 0.7
                or kline.high() > lastKline.close() * 1.3 
                or kline.high() < lastKline.close() * 0.7
                or kline.low() > lastKline.close() * 1.3 
                or kline.low() < lastKline.close() * 0.7
                or kline.close() > lastKline.close() * 1.3 
                or kline.close() < lastKline.close() * 0.7):
                if str(kline) not in theInfo.keys():
                    theInfo[str(kline)] = "@04@此K线数据相比上根跳动超过30%！上根：" + str(lastKline)
            lastKline = kline
        return theInfo
            
    
    def getBeginTime(self):
        return self.__list[0].time()
    
    def getEndTime(self):
        return self.__list[-1].time()

    def getLen(self):
        return len(self.__list)
    
    def getTimeList(self):
        timeList = []
        for i in range(self.getLen()):
            timeList.append(self.__list[i].time())
        return timeList
        
    def getCloseList(self):
        closeList = []
        for i in range(self.getLen()):
            closeList.append(self.__list[i].close())
        return closeList
    
    def getList(self):
        return self.__list
    
    def getKLine(self, i):
        '''获取第i根K线'''
        return self.__list[i]
    
    def getSubscript(self, theTime):
        '''获取K线列表中某个时间的K线在列表中的下标，比如
            theTime == getBeginTime()的话，那么getSubscript(theTime)就返回下标0
            return None if theTime didn't find
        '''
        if theTime < self.getBeginTime() or theTime > self.getEndTime():
            return None
        for i in range(self.getLen()):
            if(self.getKLine(i).time() == theTime):
                return i
        return None
        
    
    def isLimitUp(self, i):
        '''第i根K线是否收于涨停，返回True表示涨停，False表示没有涨停'''
        if i == 0:
            return False
        if (self.__list[i].close() == self.__list[i].high()):
            lastAverage = (self.__list[i-1].open() + self.__list[i-1].high()
                           + self.__list[i-1].low() + self.__list[i-1].close()) / 4
            if self.__list[i].close() > (lastAverage * (1 + KLineList.__LIMIT_JUDGE_WAVE)):
                return True
        return False
            
    def isLimitDown(self, i):
        '''第i根K线是否收于跌停，返回True表示跌停，False表示没有跌停'''
        if i == 0:
            return False
        if (self.__list[i].close() == self.__list[i].low()):
            lastAverage = (self.__list[i-1].open() + self.__list[i-1].high()
                           + self.__list[i-1].low() + self.__list[i-1].close()) / 4
            if self.__list[i].close() < (lastAverage * (1 - KLineList.__LIMIT_JUDGE_WAVE)):
                return True
        return False




class KLine(object):
    '''
    K线，单根
    '''


    def __init__(self, theList):
        '''
        theList即[时间,开盘价,最高价,最低价,收盘价,成交量]的一维列表
        '''
        self.__time = datetime.datetime.strptime(theList[0], "%Y-%m-%d")
        self.__open = eval(theList[1])
        self.__high = eval(theList[2])
        self.__low = eval(theList[3])
        self.__close = eval(theList[4])
        self.__vol = eval(theList[5])
      
    def __repr__(self):
        theString = []
        theString.append(self.timeString())
        theString.append(format(self.open(), '0.3f'))
        theString.append(format(self.high(), '0.3f'))
        theString.append(format(self.low(), '0.3f'))
        theString.append(format(self.close(), '0.3f'))
        theString.append(repr(self.vol()))
        return repr(theString)
    def __str__(self):
        return self.__repr__()
    
    
    def time(self):
        '''返回datetime类型的时间'''
        return self.__time
    
    def timeString(self):
        '''返回%Y%m%d格式的日期字符串'''
        return self.__time.strftime("%Y-%m-%d")
    
    def open(self):
        return self.__open
    
    def high(self):
        return self.__high
    
    def low(self):
        return self.__low
    
    def close(self):
        return self.__close
    
    def vol(self):
        return self.__vol
    
        