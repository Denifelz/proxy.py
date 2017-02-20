# -*- coding: utf-8 -*-

import urllib2
import urllib
import traceback
import os
import re
import sys
import cookielib
import time
import random
from StringIO import StringIO
import gzip
import logging
import threading
import shutil

logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf-8')
if "" != os.path.dirname(sys.argv[0]):
    os.chdir(os.path.dirname(sys.argv[0]) + os.sep) 
    
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def __init__(self):
        self._reHost = 'http[s]*://([^/]+)'

    def http_error_302(self, req, fp, code, msg, headers):
        logger.debug(headers.getheader('Location'))
        new_host = re.match(self._reHost, headers.getheader('Location'))
        if new_host:
            req.add_header("Host", new_host.groups()[0])
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        return result
    
class FlushRank():
    def __init__(self):
        self.cookies = cookielib.LWPCookieJar()
        handlers = [
            urllib2.HTTPHandler(),
            urllib2.HTTPSHandler(),
            urllib2.HTTPCookieProcessor(self.cookies),
            SmartRedirectHandler
            ]
        self.opener = urllib2.build_opener(*handlers)
    
    def getCookieString(self):
        cookieString = ""
        for cookie in self.cookies:
            value = '%s=%s; '%(cookie.name, cookie.value)
            cookieString += value
        return cookieString
    
    def handleRank(self, headStr):
        try:     
            ua, cookieStr = headStr.split('\r\n')
            data_map = {
                'op': 'videoshare',
                'logid': '670898'
            }
            
            postdata = urllib.urlencode(data_map)  
            i = 0
            while True:
                time.sleep(random.randint(50, 60))
                head = {
                    'Host':'xdr.m2plus2000.com',           
                    "User-Agent":ua,
                    'Accept':'application/json, text/javascript, */*; q=0.01',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Accept-Language': 'zh-CN,en-US;q=0.8',
                    'Accept-Encoding':'gzip, deflate',
                    'Origin': 'http://xdr.m2plus2000.com',
                    'Referer': 'http://xdr.m2plus2000.com/xdr/index.php?logid=670898&from=singlemessage&isappinstalled=0&state=STATE',
                    "Cookie": cookieStr,
                }           
                loginUrl = 'http://xdr.m2plus2000.com/xdr/api/ajax.php'
                req = urllib2.Request(url = loginUrl, data = postdata, headers = head)
                response = self.opener.open(req)
                pageData = ''
                if response.info()['content-encoding'] == 'gzip':
                    buf = StringIO(response.read())
                    f = gzip.GzipFile(fileobj=buf)
                    pageData = f.read()
                logger.info("header is %s, return:%s, i:%d" % (headStr, pageData, i))
                if pageData.find("rank") == -1:
                    if pageData.find('"status":0') != -1:
                        continue
                    elif pageData.find('MYSQL Query Error') != -1:
                        break
                else:
                    i += 1
        except:
            logger.debug(traceback.format_exc())
            
class WxTask(threading.Thread):
    def __init__(self, strArgs = ""):
        threading.Thread.__init__(self)
        self.strArgs = strArgs
        
    def run(self):
        try:
            flush = FlushRank()
            flush.handleRank(self.strArgs)
        except:
            logger.debug(traceback.format_exc())    
            
def main(): 
    try:
        bakPath = 'backup'
        logging.basicConfig(level=getattr(logging, 'DEBUG'), format='%(asctime)s - %(levelname)s - pid:%(process)d - %(message)s')
        
        while True:
            for root, directories, files in os.walk('./result'):
                for filename in files:
                    if filename.endswith('.txt'):
                        filepath = os.path.join(root, filename)   
                        with open(filepath, 'rb') as f:
                            headStr = f.read()
                        threadItem = WxTask(headStr)
                        threadItem.start()
                        #os.remove(filepath)
                        if not os.path.exists(bakPath):
                            os.makedirs(bakPath) 
                        shutil.move(filepath, os.path.join(bakPath, filename))
            time.sleep(30)
            logger.info("count thread : %d" % threading.active_count())
    except:
        logger.debug(traceback.format_exc())    

if __name__ == '__main__':
    main()
