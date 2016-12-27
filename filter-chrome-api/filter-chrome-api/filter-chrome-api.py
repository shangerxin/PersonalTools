import os
import sys
from pprint import pprint as pp
import re
import urllib2
import HTMLParser
import bs4
import msvcrt

jsFiles = []
chromeAPIs = set()
#{apiName:[apiFunc0, apiFunc1,...], ...}
chromeAPIMap = {}
chromeExtPath = r'F:\tclite\Extension'
webExtCheckerUrl = 'https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Browser_support_for_JavaScript_APIs'
currentFirefoxVersion = 48.0

if not os.path.exists(chromeExtPath):
    print('extension %s path not exist' % chromeExtPath)
    while(not msvcrt.kbhit()):pass
    sys.exit(0)

# get all the js files from extension directory 
for root, dirs, files in os.walk(chromeExtPath):
    for file in files:
        if file.endswith('.js'):
            fullpath = '%s\\%s' % (root, file)
            jsFiles.append(fullpath)

# filter all the used chrome APIs from the js files and add to a APIs set for the file
def filterAPI(jsPath):
    APIs = set()
    for line in open(jsPath, 'r').readlines():
        if line.find('chrome.') != -1:
            if re.match('\s*//.*', line):
                continue

            m = re.findall('chrome\.[\w\.]+', line)
            for item in m:
                unmatch = re.findall('\w+chrome\.[\w\.]+', line)
                if not unmatch or not [True for chrome_inword in unmatch if chrome_inword.find(item) != -1]:
                    APIs.add(item.strip())

    return APIs

# filter all the js files and get an used APIs set
for jsFile in jsFiles:
    chromeAPIs |= filterAPI(jsFile)


# get all the used functions for each chrome API
for api in chromeAPIs:
    codes = api.split('.')
    if len(codes) > 2:
        apiName = codes[1]
        apiFunc = codes[2]
        if chromeAPIMap.has_key(apiName):
            chromeAPIMap[apiName].append(apiFunc)
        else:
            chromeAPIMap[apiName] = [apiFunc]
            

# the sequence is defiend based on the table of the firefox documentation webpage, the first column is empty
# for the API function names
browsers = ['', 'chrome', 'edge', 'firefox', 'firefox-mobile', 'opera']

# {apiName:{funcName:[chrome, edge, firefox, firefox-mobile, opera]}, ...}
supportedMap = {}   
rep = urllib2.urlopen(webExtCheckerUrl)

def isVersionNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getSupportResultInfo(resultText):
    if resultText and resultText != 'No':
        resultText = resultText.replace('*', '')
        if isVersionNumber(resultText) and float(resultText) > currentFirefoxVersion:
            return 'Yes (%s)' % resultText
        else:
            return 'Yes'
    else:
        return 'No'

if rep.getcode() == 200:
    # filter supported information from Firefox web document page
    html = rep.read()
    soup = bs4.BeautifulSoup(html, 'html.parser')
    for apiName in soup.find_all('h2'):
        if apiName.attrs.has_key('id') and apiName['id'] == apiName.string:
            supportedMap[apiName.text] = {}
    
    for apiTable in soup.find_all('table', {'class':'webext-summary-compat-table'}):
        #previous tag is the chrome API name
        preTag = apiTable.previous_sibling 
        curApi = supportedMap[preTag.text]
        for tr in apiTable.find_all('tr'):
            for index, td in enumerate(tr.find_all('td')):
                if index == 0:
                    #API function name
                    curFunc = curApi[td.a.code.text] = [] 
                else:
                    #add brower name, browser support result for each function
                    assert(td.text)
                    curFunc.append((browsers[index], td.text)) 

    # compre the APIs which are used in extension with the web document APIs to get the final result
    usedApiCheckResult = {k:{} for k in chromeAPIMap.keys()}
    #only remain the firefox res[index][result] the index is the browsers index-1
    firefoxIndex = browsers.index('firefox') - 1
    for apiName, funcs in chromeAPIMap.items():
        for apiFunc in funcs:
            if supportedMap.has_key(apiName) and supportedMap[apiName].has_key(apiFunc):
                res = supportedMap[apiName][apiFunc]              
                usedApiCheckResult[apiName][apiFunc] = getSupportResultInfo(res[firefoxIndex][1]) 
            else:
                usedApiCheckResult[apiName][apiFunc] = 'NO INFO!'

    # print output
    for apiName, funcResult in usedApiCheckResult.items():
        for apiFunc, result in funcResult.items():
            print('{2:<20}chrome.{0}.{1}'.format(apiName, apiFunc, result))

else:
    print("Can't access the browser support page %s" % webExtCheckerUrl)

