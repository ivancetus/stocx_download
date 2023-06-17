import os
import random
import re
import time

from PyQt5.QtCore import QThread, pyqtSignal
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class DownloadThread(QThread):
    callback = pyqtSignal(object)
    finished = pyqtSignal(object)

    def __init__(self, browser, checked, path):
        super().__init__(None)
        self.browser = browser
        self.checked = checked
        self.path = path
        self.title = ''

    @staticmethod
    def increment_filename(f):
        fnew = f
        root, ext = os.path.splitext(f)
        i = 1
        while os.path.exists(fnew):
            i += 1
            fnew = '%s_%i%s' % (root, i, ext)
        return fnew

    def download(self, url):
        self.browser.get(url)
        try:
            WebDriverWait(self.browser, 20, 5).until(ec.presence_of_element_located((By.TAG_NAME, 'div')))
            s = BeautifulSoup(self.browser.page_source, 'lxml')
            keywords = s.find('h1').text
            get_title = re.search("(?<=《).*(?=》)", keywords).group(0)
            get_author = re.search("(?<=作者：).*", keywords).group(0)
            # handle illegal characters (when used as parts of file names)
            title = get_title.replace("\\", "").replace("/", "_").replace(":", "_").replace("*", "") \
                .replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
            author = get_author.replace("\\", "").replace("/", "_").replace(":", "_").replace("*", "") \
                .replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "")
            # put all pages into dict, key: value => page number: url
            pages = {}
            for page in s.find_all('option'):
                pages[page.text] = f'https://www.sto.cx/{page["value"]}'
            # if same file name exist, make new one then add _number before extension name
            filename = self.increment_filename(os.path.join(self.path, f'{title}_by_{author}.txt'))
            count = 0
            for key in pages.keys():
                count += 1
                self.browser.get(pages[key])
                try:
                    WebDriverWait(self.browser, 20, 5).until(ec.presence_of_element_located((By.TAG_NAME, 'div')))
                    soup = BeautifulSoup(self.browser.page_source, "lxml")
                    content = soup.find(id='BookContent')
                    word_list = content.get_text("\n", strip=True).splitlines(keepends=True)
                    big_word_list = '\n'.join(word_list)
                    self.callback.emit(f'正在下載{self.title}, 處理中({count}/{len(pages)}) {pages[key]} ...')
                    with open(filename, 'a', encoding="utf-8") as f:
                        f.write(big_word_list)
                    time.sleep(random.randint(5, 8) + random.random())
                except Exception as e:
                    with open('log.txt', 'w', encoding="utf-8") as f:
                        f.write(str(e))
                    return False
            return True
        except Exception as e:
            with open('log.txt', 'w', encoding="utf-8") as f:
                f.write(str(e))
            return False

    def run(self):
        for i, chk in enumerate(self.checked):
            self.title = chk.split(' url=')[0]
            url = chk.split(' url=')[1]
            if not self.download(url):
                self.finished.emit('下載時, 錯誤發生')
                break
            else:
                self.callback.emit(f'{self.title} 下載完成({i+1}/{len(self.checked)})...')
                time.sleep(5)
                if i+1 != len(self.checked):
                    self.callback.emit('準備開始下載下一個項目...')
                else:
                    self.finished.emit('下載完畢')
