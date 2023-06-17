# http://mahaljsp.asuscomm.com/index.php/2019/10/30/pyinstaller_picture/
import base64


def pic2py(pics, py_name):
    datas = []
    for pic in pics:
        image = open(pic, 'rb')
        key = pic.replace('.', '_')
        value = base64.b64encode(image.read()).decode()
        image.close()
        datas.append('{0} = b"{1}"\n'.format(key, value))  # put b in front of the value string
    f = open('{0}.py'.format(py_name), 'w+')
    for data in datas:
        f.write(data)
    f.close()


if __name__ == '__main__':
    pics = ["favicon.ico"]
    pic2py(pics, 'pic_string')