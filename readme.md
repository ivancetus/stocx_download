
### Note
- similar to [youtube_download](https://github.com/ivancetus/youtube-download-pyqt5) which is a web crawler that search videos on YouTube, return a list of results, user can choose what to download as mp3 or mp4.

- To modify UI layout, open qtDesigner, select file `ui/ui_mainwindow.ui`, compile .ui using a custom tool. 

- Set up a custom tool (using PyCharm) to compile .ui into .py

1. Open file setting `Ctrl + Alt + S`
2. Tools / External Tools / Add
3. Name: pyUic
4. Program: C:\myproject\venv\Scripts\pyuic5.exe `select pyuic5.exe inside project venv`
5. Arguments: $FileName$ -o $FileNameWithoutExtension$.py
6. Working Directory: $ProjectFileDir$\ui

- right click on .ui, tools / external tools / pyUic

- provide custom `img/favicon.ico` if you want it to show on the app

- execute `pic_to_string.py` to get `pic_string.py`

- execute pyinstaller on your system, need to have every package installed as in venv 

```commandline
cd C:\myproject

pyinstaller --hidden-import=queue -F --icon=img_handling/favicon.ico stocx.py
```
-w => not showing the debug window, might cause the program unable to initiate webdriver manager

### obsolete
打包 icon 到 windows 圖示
pyinstaller --hidden-import=queue -w -F --icon=img_handling/favicon.ico stocx.py
若新建立好的程式icon沒有更新, 進到 %localappdata% 刪除 IconCache.db 重新開機
有沒有更好的解決辦法呢?
https://stackoverflow.com/questions/24363719/pyinstaller-cant-change-the-shortcut-icon
    