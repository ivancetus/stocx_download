import errno
import logging
import os
import subprocess
from platform import system
from PyQt5.QtCore import QThread, pyqtSignal
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common import WebDriverException


class MyService(Service):
    def _start_process(self, path: str) -> None:
        logger = logging.getLogger(__name__)
        """Creates a subprocess by executing the command provided.

        :param cmd: full command to execute
        """
        cmd = [path]
        cmd.extend(self.command_line_args())
        try:
            self.process = subprocess.Popen(
                cmd,
                env=self.env,
                close_fds=system() != "Windows",
                stdout=self.log_file,
                stderr=self.log_file,
                stdin=subprocess.PIPE,
                # creationflags=self.creation_flags,
                # creationflags=134217728,
                creationflags=0x8000000,
            )
            logger.debug(f"Started executable: `{self.path}` in a child process with pid: {self.process.pid}")
        except TypeError:
            raise
        except OSError as err:
            if err.errno == errno.ENOENT:
                raise WebDriverException(
                    f"'{os.path.basename(self.path)}' executable needs to be in PATH. {self.start_error_message}"
                )
            elif err.errno == errno.EACCES:
                raise WebDriverException(
                    f"'{os.path.basename(self.path)}' executable may have wrong permissions. {self.start_error_message}"
                )
            else:
                raise
        except Exception as e:
            raise WebDriverException(
                f"The executable {os.path.basename(self.path)} needs to be available in the path. {self.start_error_message}\n{str(e)}"
            )


class BrowserThread(QThread):
    callback = pyqtSignal(object)

    def __init__(self, path):
        super().__init__(None)
        self.browser = None
        self.path = path

    def run(self):
        opt = Options()
        opt.add_argument('--headless')
        opt.add_argument('--disable-gpu')
        opt.add_argument('--window-size=1280,720')
        # random header info
        # pyinstaller cannot detect the files which are used by Fake_UserAgent, which are cache files, so one way to
        # fix it is to disable those saved cache files
        user_agent = UserAgent(use_external_data=True)
        opt.add_argument('--user-agent=%s' % user_agent.random)
        opt.add_experimental_option("excludeSwitches", ["enable-logging"])
        opt.add_argument('--disable-dev-shm-usage')

        # ser = MyService(ChromeDriverManager().install())
        ser = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=ser, options=opt)
        self.callback.emit(browser)
