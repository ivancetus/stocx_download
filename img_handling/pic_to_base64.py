# https://stackoverflow.com/questions/52293422/pyqt4-setwindowicon-from-base64
# not used in this app
from PyQt5 import QtCore, QtGui


def Base64ToBytes(filename):
    image = QtGui.QImage(filename)
    ba = QtCore.QByteArray()
    buff = QtCore.QBuffer(ba)
    image.save(buff, "PNG")
    print("ba", ba)
    print("buff", buff)
    print("image", image)
    return ba.toBase64().data()


if __name__ == '__main__':
    val = Base64ToBytes("favicon.ico")
    print(val)