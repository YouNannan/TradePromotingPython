#coding:utf-8
'''
Created on 2018年9月23日

@author: You Nannan
对外仅开放log()这一个函数，用于记录日志信息。
日志文件保存在工程根目录下的FutureLog.log中，如果需要修改日志文件路径，请修改__LOG_FILE_LOCATION参数
'''

import logging


__LOG_NAME = "FutureLog"
__LOG_FILE_LOCATION = '''../FutureLog.log'''
__LOGGING_LEVEL = logging.DEBUG

__logger = logging.getLogger(__LOG_NAME)
__isReady = False


def __prepare():
    global __logger
    __logger.setLevel(__LOGGING_LEVEL)
    
    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler(__LOG_FILE_LOCATION)
    fh.setLevel(__LOGGING_LEVEL)
    
    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    
    # 给logger添加handler
    __logger.addHandler(fh)
    
    
    
def log(info):
    global __isReady
    global __logger
    if __isReady is False:
        __prepare()
        __isReady = True
    
    # 记录一条日志
    __logger.info(info)
    