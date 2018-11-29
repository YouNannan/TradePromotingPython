#coding:utf-8
'''
Created on 2018年9月23日
本模块只有四个函数是比较有用的：
1. getCommodityList() :
        从文件__DATA_COMMODITY_CODE_FILENAME中读取所有商品代码
        
2. getMainContractDict() :
        从文件__DATA_MAIN_CONTRACT_FILENAME中读取所有主力合约代码
        
3. getMainContractName(commodityCode, date):
        找到指定商品在指定日期的主力合约名称并返回
        
4. getContractKLineList(contractName, isReadFileDirectly = False):
        获取指定合约名的K线数据，默认使用预读缓存技术__preReadAllMainContractFromFile()，
        若isReadFileDirectly为True则会直接从文件读取
        
5. __getCommodityDataToDict(commodityCode, contractNameList = None):
        从数据文件里读取某商品的详细数据信息，并返回其{合约名:K线列表数据}字典，不使用预读缓存，会直接从文件读取
        
6. updateAllDayKLine() :
        从新浪接口获取所有存在的商品的K线图数据，按品种保存到__DATA_DIR中，耗时较长，慎用
        
7. checkAllDayKLine():
        检查所有K线的合法性，可接在updateAllDayKLine之后立即调用为佳，本函数耗时较长，慎用
        
8. updateAllAvailableCommodityCode() :
        从新浪接口检测获取所有存在的商品代码，并写入__DATA_COMMODITY_FILENAME，耗时较长，非出现新品种的情况下不要使用
        
9. updateMainContractDict() :
        扫描所有合约数据文件，生成主力合约信息，并写入__DATA_MAIN_CONTRACT_FILENAME，虽然不是网络函数，但也耗时较长。
        耗时较长，大概一个月用一次就够了
        
@author: You Nannan
'''
import futuretools
import urllib.request
import datetime
import futurelogger
import os
import futurecontract

#新浪数据源地址，后接M0809字样来获取日线信息
__DATA_SOURCE_URL = "http://stock2.finance.sina.com.cn/futures/api/json.php/IndexService.getInnerFuturesDailyKLine?symbol="

#期货数据开始规整的年份和月份
__BEGIN_YEAR = 2008
__BEGIN_MONTH = 9

#存放数据的根目录
__data_dir = "../data"
#用内存磁盘来加速访问
__MEM_ACCELERATE_SWITCHER = True
__MEM_ACCELERATE_FOLDER = "A:/verified"
def __getDataDir():
    global __data_dir
    return __data_dir
def setDataDirBeforeVerified():
    global __data_dir
    __data_dir = "../data"
def setDataDirAfterVerified():
    global __data_dir
    if __MEM_ACCELERATE_SWITCHER and os.path.exists(__MEM_ACCELERATE_FOLDER):
        __data_dir = __MEM_ACCELERATE_FOLDER
    else:
        __data_dir = "../data/verified"
    
    
__DATA_COMMODITY_CODE_FILENAME = "../data/commodityInfo.txt"
__DATA_MAIN_CONTRACT_FILENAME = "../data/mainContractInfo.txt"

__MIN_VOL_IN_MAIN_CONTRACT = 10000 #能成为主力合约所要求的最小成交量

__MANUAL_MODIFIED_CONTRACT_TUPLE = ("CS1709", "CS1801", "CS1805",
                                    "CU1501", "CU1505",
                                    "P1101",
                                    "ZN1406", "ZN1407", "ZN1408", "ZN1409", "ZN1410", "ZN1411", "ZN1412",
                                    "ZN1501", "ZN1502", "ZN1503", "ZN1504", "ZN1505", "ZN1506")

__commodityList = None
def getCommodityList():
    '''从文件__DATA_COMMODITY_CODE_FILENAME中读取所有商品代码'''
    global __commodityList
    if __commodityList is None:
        commodityList = futuretools.readListFromFile(__DATA_COMMODITY_CODE_FILENAME)
    return commodityList

__mainContractDict = None
def getMainContractDict():
    '''从文件__DATA_MAIN_CONTRACT_FILENAME中读取所有主力合约代码'''
    global __mainContractDict
    if __mainContractDict is None:
        __mainContractDict = futuretools.readListFromFile(__DATA_MAIN_CONTRACT_FILENAME)
    return __mainContractDict

def getMainContractName(commodityCode, date):
    '''找到指定商品在指定日期的主力合约名称并返回'''
    for contractName in getMainContractDict()[commodityCode]:
        beginDate = getMainContractDict()[commodityCode][contractName][0]
        endDate = getMainContractDict()[commodityCode][contractName][1]
        if date >= beginDate and date < endDate:
            return contractName
    return None


__mainContractData = None
def __preReadAllMainContractFromFile():
    global __mainContractData
    __mainContractData = {}
    for commodityCode in getMainContractDict().keys():
        for contractName in getMainContractDict()[commodityCode].keys():
            thePath = __getCommodityDataDir(commodityCode) + "/" + contractName + ".txt"
            theContractRaw = futuretools.readListFromFile(thePath)
            theContract = futurecontract.KLineList(theContractRaw)
            __mainContractData[contractName] = theContract

            


        
        
    
def getContractKLineList(contractName, isReadFileDirectly = False):
    global __mainContractData
    '''获取指定合约名的K线数据'''
    if ((isReadFileDirectly is True) or 
        ((__mainContractData is not None)
         and (contractName not in __mainContractData.keys()))):
        commodityCode = contractName[0:-4]
        path = __getCommodityDataDir(commodityCode) + "/" + contractName + ".txt"
        theContractRaw = futuretools.readListFromFile(path)
        theContract = futurecontract.KLineList(theContractRaw)
        return theContract
    else:
        if __mainContractData is None:
            __preReadAllMainContractFromFile()
        return __mainContractData[contractName]
    
def __getCommodityDataToDict(commodityCode, contractNameList = None):
    '''获取某个品种的合约数据信息，如果contractNameList不为None，仅返回指定列表中的合约信息，
    如果contractNameList为None，就返回该品种的所有合约数据信息
    '''
    rootdir = __getCommodityDataDir(commodityCode)
    if contractNameList is None:
        fileList = os.listdir(rootdir)
    else:
        fileList = []
        for contractName in contractNameList:
            fileList.append(contractName + ".txt")
    theContractDict = {}
    for i in range(0,len(fileList)):
        path = os.path.join(rootdir,fileList[i])
        if os.path.isfile(path):
            theContract = getContractKLineList(fileList[i][0:-4], True)
            theContractDict[fileList[i][0:fileList[i].find('.')]] = theContract
    return theContractDict
 
def updateAllDayKLine():
    '''从新浪接口获取所有存在的商品的K线图数据，按品种保存到__DATA_DIR中，耗时较长，慎用'''
    futurelogger.log("开始从新浪网更新最新的商品K线数据，updateAllDayKLine() begins.")
    commodityList = getCommodityList()
    for commodityCode in commodityList:
        __establishCommodityDataFromInternet(commodityCode)
    futurelogger.log("从新浪网更新最新的商品K线数据完毕，updateAllDayKLine() ends.")

def updateAllAvailableCommodityCode():
    '''从新浪接口检测获取所有存在的商品代码，并写入__DATA_COMMODITY_FILENAME，耗时较长，非出现新品种的情况下不要使用'''
    futurelogger.log("开始从新浪网更新最新的商品代码，updateAllAvailableCommodityCode() begins.")
    ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    theList = []
    for commodityCode in ALPHABET:
        if __isCommodityExist(commodityCode):
            theList.append(commodityCode)
        for commodityCode2 in ALPHABET:
            if __isCommodityExist(commodityCode + commodityCode2):
                theList.append(commodityCode + commodityCode2)
    futuretools.writeListToFile(__DATA_COMMODITY_CODE_FILENAME, theList)
    futurelogger.log("从新浪网更新最新的商品代码完毕，updateAllAvailableCommodityCode() ends.")
    
def updateMainContractDict():
    '''扫描所有合约数据文件，生成主力合约信息，并写入__DATA_MAIN_CONTRACT_FILENAME，虽然不是网络函数，但也耗时较长'''
    futurelogger.log("开始扫描所有K线数据文件并生成主力合约数据文件，updateMainContractDict() begins.")
    commodityList = getCommodityList()
    mainContractDict = {}#存放主力合约的字典
    for commodityCode in commodityList:#遍历所有品种
        #现将该品种的所有合约数据一次性读入到theContractDict
        theContractDict = __getCommodityDataToDict(commodityCode)
        
        #按照时间遍历theContractDict中的所有合约,找出主力合约
        beginDate = datetime.datetime(__BEGIN_YEAR, 1, 1)
        endDate = datetime.datetime(__getNowYear(), __getNowMonth(), 28)
        theDaysList = futuretools.getDaysList(beginDate, endDate)
        mainContractInTheCommodity = {}
        lastContractName = None
        for theDate in theDaysList:
            contractVolDict = {}
            #读出该品种所有合约在当天的成交量
            for theContractName in theContractDict.keys():
                sub = theContractDict[theContractName].getSubscript(theDate)
                if sub is None:
                    continue
                contractVolDict[theContractName] = theContractDict[theContractName].getKLine(
                    sub).vol()
            #若在该品种所有合约中未找到该日期，则略过
            if len(contractVolDict) == 0:
                continue
            #找出成交量最大的合约，加到mainContractDict[commodityCode]中
            maxVol = __MIN_VOL_IN_MAIN_CONTRACT
            maxVolContractName = ""
            for theContractName in contractVolDict.keys():
                if maxVol < contractVolDict[theContractName]:
                    maxVol = contractVolDict[theContractName]
                    maxVolContractName = theContractName
            if maxVol == __MIN_VOL_IN_MAIN_CONTRACT: #当天成交量太小的话不算数
                continue
            #把主力合约的时间也记上
            if maxVolContractName not in mainContractInTheCommodity.keys():
                mainContractInTheCommodity[maxVolContractName] = [theDate, theDate]
                if lastContractName is not None:
                    theLastContractBeginDate = mainContractInTheCommodity[
                        lastContractName][0]
                    mainContractInTheCommodity[lastContractName] = [
                        theLastContractBeginDate, theDate]
                lastContractName = maxVolContractName
        theLastContractBeginDate = mainContractInTheCommodity[lastContractName][0]
        mainContractInTheCommodity[lastContractName] = [theLastContractBeginDate, endDate]
            
        mainContractDict[commodityCode] = mainContractInTheCommodity
    
    futuretools.writeListToFile(__DATA_MAIN_CONTRACT_FILENAME, mainContractDict)
    futurelogger.log("扫描所有K线数据文件并生成主力合约数据文件完毕，updateMainContractDict() ends.")
            
   
def checkAllDayKLine():
    '''检查所有K线的合法性，可接在updateAllDayKLine之后立即调用为佳，本函数耗时较长，慎用'''
    futurelogger.log("开始检查所有K线数据文件的合法性并将校正过的数据放入verified文件夹，checkAllDayKLine() begins.")
    infoDict = {}
    for commodityCode in getCommodityList():
        #仅检查主力合约
        dataDict = __getCommodityDataToDict(commodityCode, 
                                          getMainContractDict()[commodityCode].keys())
        for contractName in dataDict.keys():
            kLineList = dataDict[contractName]
            info = kLineList.checkAndCorrectData(contractName)
            infoDict[contractName] = info
            
            setDataDirAfterVerified()
            commodityDir = __getDataDir() + "/" + commodityCode
            futuretools.mkdirIfNotExist(commodityDir)
            futuretools.writeListToFile(commodityDir + "/" + contractName 
                                        + ".txt", kLineList)
            setDataDirBeforeVerified()
            
    futuretools.writeListToFile("../checkReport.txt", infoDict)
    setDataDirAfterVerified()
    futurelogger.log("检查所有K线数据文件的合法性并将校正过的数据放入verified文件夹完毕，checkAllDayKLine() ends.")

    
            
    
    
def __getCommodityDataDir(commodityCode):
    return __getDataDir() + "/" + commodityCode

def __isCommodityExist(commodityCode):
    '''从新浪接口或知commodityCode是否存在'''
    commodityCode = commodityCode.upper()
    for yearAndMonth in __getThisYearDateList():
        theUrl = __DATA_SOURCE_URL + commodityCode + yearAndMonth
        theList = __readList2FromInternet(theUrl)
        if theList is not None:
            break
    if theList is None:
        return False
    else:
        return True
    
def __establishCommodityDataFromInternet(commodityCode):
    '''从新浪接口获取所有商品信息，耗时较长，慎用'''
    commodityCode = commodityCode.upper()
    for yearAndMonth in __getAvailableDateList():
        contractCode = commodityCode + yearAndMonth
        if contractCode in __MANUAL_MODIFIED_CONTRACT_TUPLE:#手动修改的合约不更新
            continue
        theUrl = __DATA_SOURCE_URL + contractCode
        theList = __readList2FromInternet(theUrl)
        if theList is None:
            continue
        commodityDir = __getDataDir() + "/" + commodityCode
        futuretools.mkdirIfNotExist(commodityDir)
        futuretools.writeListToFile(commodityDir + "/" + commodityCode + yearAndMonth + ".txt", theList)
        
            


def __readList2FromInternet(theUrl):
    '''从新浪数据接口读入日线图，如果内部数据能够解析成list则返回list类型结果，如果含null数据则直接返回None'''
    req=urllib.request.Request(theUrl)
    resp=urllib.request.urlopen(req)
    data=resp.read().decode('utf-8')
    if data == "null":
        return None
    try:
        theList = eval(data)
    except NameError:
        futurelogger.log("在解析以下url时发生了NameError异常，不能返回list类型，直接返回None：" + theUrl)
        futurelogger.log("原型string如下：" + data + "\n")
        return None
    else:
        return theList

def __getNowYear():
    nowDate = datetime.datetime.now()
    yearAndMonth = nowDate.strftime("%Y%m")
    return int(yearAndMonth[0:4])

def __getNowMonth():
    nowDate = datetime.datetime.now()
    yearAndMonth = nowDate.strftime("%Y%m")
    return int(yearAndMonth[4:6])
    
def __getAvailableDateList():
    '''获取从有效合约（如默认是0809）直到最新合约（如2008）的年月字串列表'''
    beginDate = datetime.datetime(__BEGIN_YEAR, __BEGIN_MONTH, 1)
    endDate = datetime.datetime(__getNowYear() + 2, __getNowMonth(), 1)
    return __getDateList(beginDate, endDate)

def __getThisYearDateList():
    '''获取从本月交割合约（如默认是1809）直到整一年后的合约（如1908）的年月字串列表'''
    beginDate = datetime.datetime(__getNowYear(), __getNowMonth(), 1)
    endDate = datetime.datetime(__getNowYear() + 1, __getNowMonth(), 1)
    return __getDateList(beginDate, endDate)
    
def __getDateList(beginDate, endDate):
    '''获取半闭半开区间[beginDate,endDate)内的连续年月字串列表，如__getDateList("0809","0811")的结果是["0809","0810"]'''
    iDate = beginDate
    theList = []
    while endDate > iDate :
        yearAndMonth = iDate.strftime("%Y%m")
        theList.append(yearAndMonth[2:])
        theYear = int(yearAndMonth[0:4])
        theMonth = int(yearAndMonth[4:6])
        if theMonth == 12:
            theYear += 1
            theMonth = 1
        else :
            theMonth += 1
        iDate = datetime.datetime(theYear, theMonth, 1)
    return theList
