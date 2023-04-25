import io
import os
import random
import re
import shutil
import string
import sys
import time
import traceback

import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(os.path.join(os.path.abspath(os.path.join(os.getcwd(), "..")), 'common'))


class WebDriverUtil:
    @staticmethod
    def openWebDriver(policyId, chrome_options=None):
        executable_path = WebDriverUtil.getChromeDriverExePath(policyId)
        if chrome_options is None:
            chrome_options = Options()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument('lang=zh-CN,zh,zh-TW,en-US,en')
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36')
            # chrome_options.add_extension('../Chrome/extension/chrome_plugin.crx')
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-blink-features")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            # executable_path = ChromeDriverManager().install()
            # print(executable_path)
        driver = webdriver.Chrome(executable_path=executable_path, options=chrome_options)
        with open('../../Chrome/js/stealth.min.js') as f:
            js = f.read()
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument", {"source": js}
            )
        return driver

    @staticmethod
    def closeWebDriver(policyId, driver):
        process_name = f'{policyId}_CHROMEDRIVER'
        if driver is not None:
            driver.close()
            driver.quit()
        pid = -1
        for proc in psutil.process_iter():
            if process_name in proc.name():
                pid = proc.pid
        if pid != -1:
            os.system(f"kill -9 {pid}")

    @staticmethod
    def getDefaultUntilFunc(keywords):
        def __waitUntilFunc(driver):
            html = driver.execute_script("return document.documentElement.outerHTML")
            # print(html)
            if keywords in html:
                return True
            else:
                return False

        return __waitUntilFunc

    @staticmethod
    def waitWebDriver(driver, waitTime=30, waitUntil=None):
        if driver is not None and waitUntil is not None:
            try:
                WebDriverWait(driver=driver, timeout=waitTime).until(method=waitUntil)
            except:
                traceback.print_exc()

    @staticmethod
    def getChromeDriverExePath(policyId):
        initDir = '../../Chrome'
        initPath = f'{initDir}/init/chromedriver'
        exePath = f'{initDir}/derivation/{policyId}_CHROMEDRIVER'
        if not os.path.exists(exePath):
            shutil.copyfile(initPath, exePath)
            os.chmod(exePath, 0o755)
            WebDriverUtil.patch_webdriver(policyId)
        return exePath

    @staticmethod
    def gen_random_cdc():
        cdc = random.choices(string.ascii_lowercase, k=26)
        cdc[-6:-4] = map(str.upper, cdc[-6:-4])
        cdc[2] = cdc[0]
        cdc[3] = "_"
        return "".join(cdc).encode()

    @staticmethod
    def patch_webdriver(policyId):
        linect = 0
        replacement = WebDriverUtil.gen_random_cdc()
        initDir = '../../Chrome'
        exePath = f'{initDir}/derivation/{policyId}_CHROMEDRIVER'
        with io.open(exePath, "r+b") as fh:
            for line in iter(lambda: fh.readline(), b""):
                if b"cdc_" in line:
                    fh.seek(-len(line), 1)
                    newline = re.sub(b"cdc_.{22}", replacement, line)
                    fh.write(newline)
                    linect += 1
            return linect

    @staticmethod
    def test_url():
        urls = [
            'http://www.fangdi.com.cn/new_house/new_house.html', 'http://zjt.hubei.gov.cn/',
            'http://epub.sipo.gov.cn/',
            'http://jg.hbcic.net.cn/web/XmManage/XmxxSearch.aspx?lb=0',
            'http://cdst.chengdu.gov.cn/cdkxjsj/c108728/part_list_more.shtml',
            'http://cbss.10010.com/essframe', 'http://218.205.252.11:18060/npage/sagt/login/login.jsp',
            'http://www.fangdi.com.cn/new_house/new_house_list.html?districtID=2385fa574f10a564',
            'http://pss-system.cnipa.gov.cn/sipopublicsearch/portal/uilogin-forwardLogin.shtml',
            'http://jg.hbcic.net.cn/web/XmManage/XmxxSearch.aspx?lb=0',
            'http://www.snj.gov.cn/',
            'http://jg.hbcic.net.cn/web/QyManage/QyList.aspx?qylx=3',
            'http://scu.edu.cn/',
            'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id=692293',
            'http://cpquery.sipo.gov.cn/',
            'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id=692293',
            'http://xypt.mwr.gov.cn/UnitCreInfo/listCydwPage.do?TYPE=1&yzmCode=',
            'https://www.nmpa.gov.cn/xxgk/fgwj/gzwj/gzwjyp/20200805091518116.html',
            'https://www.nmpa.gov.cn/',
            'https://pmos.sc.sgcc.com.cn/pmos/index/login.jsp?redirecturl=http%3A%2F%2Fpmos.sc.sgcc.com.cn%3A80%2F&y7bRbP=qGrnqqqplplplplplpyOPx3dQYu8V0ZhSgAJlagrBHEqqrl',
            'http://www.chinaunicombidding.cn/jsp/cnceb/web/info1/infoList_all.jsp?notice=&time1=&time2=&province=&city=',
            'http://www.chinaunicombidding.cn/jsp/cnceb/web/index_parent.jsp',
            'http://gs.amac.org.cn/amac-infodisc/res/pof/person/personList.html?userId=33',
            'https://b2b.10086.cn/b2b/main/listVendorNotice.html?noticeType=2#this',
            'https://b2b.10086.cn/b2b/main/viewNoticeContent.html?noticeBean.id=690187',
            'http://www.snj.gov.cn/zwgk/xxgkml/zfcg/zbgg/202008/t20200818_2805696.html',
            'http://www.sipo.gov.cn/xwfb/index.htm',
            'http://43.248.49.97/',
            'http://www.customs.gov.cn/',
            'http://www.nhc.gov.cn/',
            'http://www.fangdi.com.cn/'
        ]
        driver = WebDriverUtil.openWebDriver(policyId="HEIMAOTOUSU")
        driver.set_page_load_timeout(5)  # 页面加载超时时间
        driver.set_script_timeout(5)  # 页面js加载超时时间
        for url in urls:
            try:
                driver.get(url)
                time.sleep(5)
                html = driver.execute_script("return document.documentElement.outerHTML")
                if len(html) < 200:
                    print(url, html)
            except:
                pass
        WebDriverUtil.closeWebDriver(policyId="HEIMAOTOUSU", driver=driver)


if __name__ == '__main__':
    driver: WebDriver = WebDriverUtil.openWebDriver(policyId="HEIMAOTOUSU")
    waitUntilFunc = WebDriverUtil.getDefaultUntilFunc("公告详情")
    # driver.get('https://www.baidu.com/')
    # driver.get('https://nowsecure.nl/')
    # driver.get('http://sthj.gansu.gov.cn/sthj/c114875/list_2.shtml')
    # driver.get('http://www.nhc.gov.cn/wjw/xwdt/list_5.shtml')
    # driver.get('https://www.nmpa.gov.cn/xxgk/fxjzh/ypfxjch/index_3.html')
    # driver.get('https://www.nmpa.gov.cn/datasearch/home-index.html')
    # driver.get('https://www.samr.gov.cn/fldys/tzgg/xzcf/index_3.html')
    driver.get('https://www.samr.gov.cn/fldys/tzgg/xzcf/202206/t20220609_347672.html')
    # driver.get('http://yjt.hubei.gov.cn/fbjd/tzgg/index.shtml')
    for i in range(20):
        try:
            WebDriverUtil.waitWebDriver(driver, waitUntil=waitUntilFunc)
            while True:
                html = driver.execute_script("return document.documentElement.outerHTML")
                if '正在加载信息...' in html:
                    print('正在加载信息...')
                    time.sleep(1)
                else:
                    button = driver.find_element(By.XPATH, '//*[@id="pages"]/table/tbody/tr/td[8]/a/span/span[2]')
                    button.click()
                    button.send_keys()
                    button.clear()
                    time.sleep(2)
        except:
            pass
    WebDriverUtil.closeWebDriver(policyId="HEIMAOTOUSU", driver=driver)
