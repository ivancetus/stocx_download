import random
import re
import time
import urllib.parse
from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class SearchThread(QThread):
    callback = pyqtSignal(object)
    search_result = pyqtSignal(object)

    def __init__(self, browser, input_text, search_mode):
        super().__init__(None)
        self.browser = browser
        self.input_text = input_text
        self.search_mode = search_mode

    def run(self):
        max_retry = 3
        retry = 0
        links = {}

        query = urllib.parse.quote(self.input_text)
        if self.search_mode == 'Author':
            self.browser.get(f"https://www.sto.cx/sba.aspx?k={query}&c=0")
        elif self.search_mode == 'Novel':
            self.browser.get(f"https://www.sto.cx/sbn.aspx?k={query}&c=0")

        while max_retry > retry:
            try:
                WebDriverWait(self.browser, 20, 5).until(ec.presence_of_element_located((By.TAG_NAME, 'div')))
                soup = BeautifulSoup(self.browser.page_source, "lxml")
                results = int(soup.find('span', string=re.compile("^相關結果共|^相关结果共")).text.split()[1])
                if results == 0:
                    self.search_result.emit('找不到結果, 請確認是否輸入錯誤')
                    break
                # {(href: title), }
                a_tags = soup.find_all('a', href=re.compile("^/book"))
                for a in a_tags:
                    url = f'https://www.sto.cx{a["href"]}'
                    if self.search_mode == 'Author':
                        links.update({url: f'{a["title"]} url={url}'})
                    elif self.search_mode == 'Novel':
                        links.update({url: f'{a.text} url={url}'})
                    self.search_result.emit(f'({len(links)}/{results}) 正在處理...')
                next_page = soup.find('a', string=re.compile("^下一頁|^下壹頁"))
                if next_page.get('disabled'):
                    self.search_result.emit(f'共 {len(links)} 筆資料')
                    break
                next_page_link = f'https://www.sto.cx/{next_page.get("href")}'
                self.browser.get(next_page_link)
                time.sleep(random.randint(5, 8) + random.random())
            except Exception as e:
                self.search_result.emit('錯誤發生', e)
                retry += 1
                continue
        self.callback.emit(links)
