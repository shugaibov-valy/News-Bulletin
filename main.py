# -*- coding: utf-8 -*-
import sys
import sqlite3
import requests
from bs4 import BeautifulSoup as BS
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from style import style_css
from functions import uploading_post, uploading_json, completion_comboBox


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(782, 704)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setGeometry(QtCore.QRect(50, 110, 661, 191))
        self.listWidget.setObjectName("listWidget")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(460, 300, 251, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(50, 330, 661, 300))
        self.textEdit.setObjectName("textEdit")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(50, 308, 300, 20))
        self.label_2.setText("")
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(49, 630, 663, 55))
        self.label_3.setText("")
        self.label_3.setObjectName("label_3")

        self.horizontalFrame = QtWidgets.QFrame(self.centralwidget)
        self.horizontalFrame.setGeometry(QtCore.QRect(50, 0, 661, 91))
        self.horizontalFrame.setObjectName("horizontalFrame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalFrame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.horizontalFrame)
        font = QtGui.QFont()
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.horizontalFrame)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout.addWidget(self.comboBox)
        self.pushButton = QtWidgets.QPushButton(self.horizontalFrame)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 782, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_2.setText(_translate("MainWindow", "подробнее..."))
        self.label.setText(_translate("MainWindow", "Новости"))
        self.pushButton.setText(_translate("MainWindow", "Выбрать"))
        self.pushButton.clicked.connect(self.choose_city)
        self.pushButton_2.clicked.connect(self.choose_post)
        completion_comboBox(self.comboBox)

    def choose_city(self):
        self.city = self.comboBox.currentText()
        try:       # check for internet connection
            r = requests.get('https://news.rambler.ru/regions/')
            html = BS(r.content, 'html.parser')
            city_url = ''
            for city_parse in html.find_all('a', 'j-regions__link'):
                if city_parse.contents[0].strip('\n') == self.city:
                    city_url = 'https://news.rambler.ru' + city_parse.get('href') + '?updated'
                    break
            my_json = uploading_json(city_url, self.city, self.listWidget)
            for i in range(0, 5):
                uploading_post(i, my_json, self.city, self.listWidget)

        except requests.exceptions.ConnectionError:
            con = sqlite3.connect('ParseNews.sqlite')
            cur = con.cursor()
            posts = cur.execute(f"""SELECT * FROM '{self.city}'""").fetchall()
            if len(posts) > 0:
                self.listWidget.clear()
                for i in posts:
                    self.listWidget.addItem(i[0])
                self.label_2.setText('Проверьте подключение к интернету!')
            else:
                self.listWidget.clear()
                self.textEdit.clear()
                self.label_2.setText('Проверьте подключение к интернету!')
            con.commit()
            con.close()

    def choose_post(self):
        try:
            title = self.listWidget.currentItem().text()
            con = sqlite3.connect('ParseNews.sqlite')
            cur = con.cursor()
            text_post = cur.execute(f"""SELECT text_post from '{self.city}' WHERE title_post = '{title}'""").fetchone()
            con.commit()
            con.close()
            self.textEdit.setText('')
            self.textEdit.setText(text_post[0])
        except:
            pass


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_css)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
