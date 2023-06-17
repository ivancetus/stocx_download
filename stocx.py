import json
import os.path
import sys
import ctypes
import platform

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QCheckBox, QListWidgetItem, QFileDialog
from BrowserThread import BrowserThread
from DownloadThread import DownloadThread
from SearchThread import SearchThread
from img_handling.pic_string import favicon_ico
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.checkOs = self.win_or_mac()
        if os.path.exists("path.json"):
            with open("path.json", 'r') as f:
                self.path = json.load(f)
        else:
            if self.checkOs == 'Windows':
                self.path = "c:\\novel_tmp"
            elif self.checkOs == 'Darwin':
                self.path = "/Users"
            else:
                self.lblStatus.setText("不支援的作業系統, 無法確保正常執行")
        self.lblPath.setText(self.path)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.disable_gui()
        # BrowserThread
        self.browserThread = BrowserThread(self.path)
        self.browserThread.callback.connect(self.browser_thread_callback)
        self.browserThread.start()

        self.btnSearch.clicked.connect(self.btn_search_clicked)
        self.btnDownload.clicked.connect(self.btn_download_clicked)
        self.btnPath.clicked.connect(self.btn_path_clicked)
        # press Enter to search
        self.txtInput.installEventFilter(self)

    def btn_search_clicked(self):
        self.listWidget.clear()
        self.input_text = self.txtInput.text()
        self.search_mode = ''
        if self.input_text == '':
            dialog = QMessageBox()
            dialog.setWindowTitle('思兔閱讀下載')
            dialog.setText("請輸入作者 / 作品")
            dialog.exec()
            return
        if self.rbtnAuthor.isChecked():
            self.search_mode = 'Author'
        elif self.rbtnNovel.isChecked():
            self.search_mode = 'Novel'
        self.lblStatus.setText('搜尋中...')
        self.disable_gui()
        # SearchThread
        self.searchThread = SearchThread(self.browser, self.input_text, self.search_mode)
        self.searchThread.callback.connect(self.search_thread_callback)
        self.searchThread.search_result.connect(self.search_thread_result)
        self.searchThread.start()

    def btn_download_clicked(self):
        count = self.listWidget.count()
        if count < 1:
            dialog = QMessageBox()
            dialog.setWindowTitle("思兔閱讀下載")
            dialog.setText("請輸入作者 / 作品")
            dialog.exec()
            return
        boxes = [self.listWidget.itemWidget(self.listWidget.item(i)) for i in range(count)]
        checked = []
        for box in boxes:
            if box.isChecked():
                checked.append(box.text())
        self.disable_gui()
        # DownloadThread
        self.downloadThread = DownloadThread(self.browser, checked, self.path)
        self.downloadThread.callback.connect(self.download_thread_callback)
        self.downloadThread.finished.connect(self.download_thread_finished)
        self.downloadThread.start()

    def btn_path_clicked(self):
        path = QFileDialog.getExistingDirectory()
        if path != '':
            # if file cannot be saved, try different path slashes
            if self.checkOs == 'Windows':
                self.path = path.replace("/", "\\")
            elif self.checkOs == 'Darwin':
                self.path = path
            with open("path.json", 'w') as f:
                json.dump(self.path, f)
            self.lblPath.setText(self.path)

    def browser_thread_callback(self, browser):
        self.browser = browser
        self.enable_gui()

    def search_thread_result(self, msg):
        self.lblStatus.setText(msg)

    def search_thread_callback(self, links):
        self.enable_gui()
        self.setStyleSheet('''
            QCheckBox::indicator{
                width: 18px;
                height: 18px;
            }
        ''')
        if links is not None:
            for key in links.keys():
                item = QListWidgetItem()
                self.listWidget.addItem(item)
                box = QCheckBox(links[key])
                self.listWidget.setItemWidget(item, box)

    def download_thread_callback(self, msg):
        self.lblStatus.setText(msg)

    def download_thread_finished(self, msg):
        self.lblStatus.setText(msg)
        self.enable_gui()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.txtInput:
            if event.text() == '\r':
                self.btn_search_clicked()
        return super(MainWindow, self).eventFilter(source, event)

    def disable_gui(self):
        self.txtInput.setDisabled(True)
        self.btnSearch.setDisabled(True)
        self.btnDownload.setDisabled(True)
        self.btnPath.setDisabled(True)
        self.rbtnNovel.setDisabled(True)
        self.rbtnAuthor.setDisabled(True)

    def enable_gui(self):
        self.txtInput.setEnabled(True)
        self.btnSearch.setEnabled(True)
        self.btnDownload.setEnabled(True)
        self.btnPath.setEnabled(True)
        self.rbtnNovel.setEnabled(True)
        self.rbtnAuthor.setEnabled(True)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "思兔閱讀下載", "確定要關閉嗎?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.browser.quit()
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def icon_from_base64(base64):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray.fromBase64(base64))
        icon = QtGui.QIcon(pixmap)
        return icon

    @staticmethod
    def win_or_mac():
        return platform.system()


if __name__ == '__main__':
    if MainWindow.win_or_mac() == 'Windows':
        myAppId = u'myCompany.myProduct.subProduct.version'  # arbitrary string, unicode
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppId)

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(MainWindow.icon_from_base64(favicon_ico)))
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
