# -*- coding: utf-8 -*-

import sys
import sqlite3
import requests
import re
import json
from bs4 import BeautifulSoup as BS
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication


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
        self.pushButton_2.clicked.connect(self.choose_title_post)
        con = sqlite3.connect('ParseNews.sqlite')
        cur = con.cursor()
        cities_and_countries = cur.execute("""SELECT city_name FROM 'Список городов и стран'""").fetchall()
        for i in cities_and_countries:
            self.comboBox.addItem(i[0])
        con.close()

    def choose_city(self):
        self.current = self.comboBox.currentText()
        try:       # проверяем на подключение интернета
            r = requests.get('https://news.rambler.ru/regions/')
            html = BS(r.content, 'html.parser')
            for city_name in html.find_all('a', 'j-regions__link'):
                if city_name.contents[0].strip('\n') == self.current:
                    city_url = 'https://news.rambler.ru' + city_name.get('href') + '?updated'

            def prov_print():
                ssilka_post = json.loads(my_json)['itemListElement'][i]['url']
                r_post = requests.get(ssilka_post)
                html_post = BS(r_post.content, 'html.parser')
                html_post_title = html_post.find('meta', itemprop='name')
                html_post_text = html_post.find('meta', itemprop="articleBody")

                if str(html_post_text) == 'None' or str(html_post_title) == 'None':
                    prov_print()
                else:
                    con = sqlite3.connect('ParseNews.sqlite')
                    cur = con.cursor()
                    title_post = re.sub(r'\<[^>]*\>', '', str(html_post_title.attrs['content']))  # удаляем все лишние символы из текста
                    text_post = re.sub(r'\<[^>]*\>', '', str(html_post_text.attrs['content']))
                    cur.execute(f"""INSERT INTO '{self.current}' VALUES('{title_post}', '{text_post}')""")
                    con.commit()
                    con.close()
                    self.listWidget.addItem(title_post)
                    self.listWidget.update()

            html = requests.get(city_url)
            soup = BS(html.content, "html.parser")
            script = soup.find_all('script', type="application/ld+json")[-1]   # JSON
            my_json = str(script)[36:-10]
            con1 = sqlite3.connect('ParseNews.sqlite')
            cur1 = con1.cursor()
            cur1.execute(f"""DELETE FROM '{self.current}'""")
            con1.commit()
            con1.close()
            self.listWidget.clear()
            for i in range(0, 5):
                prov_print()

        except requests.exceptions.ConnectionError:
            con1 = sqlite3.connect('ParseNews.sqlite')
            cur1 = con1.cursor()
            part = cur1.execute(f"""SELECT * FROM '{self.current}'""").fetchall()
            if len(part) > 0:
                self.listWidget.clear()
                for i in part:
                    self.listWidget.addItem(i[0])
                self.label_2.setText('Проверьте подключение к интернету!')
            else:
                self.listWidget.clear()
                self.textEdit.clear()
                self.label_2.setText('Проверьте подключение к интернету!')
            con1.commit()
            con1.close()

    def choose_title_post(self):
        try:
            title = self.listWidget.currentItem().text()
            con = sqlite3.connect('ParseNews.sqlite')
            cur = con.cursor()
            text_post = cur.execute(f"""SELECT text_post from '{self.current}' WHERE title_post = '{title}'""").fetchone()
            con.commit()
            con.close()
            self.textEdit.setText('')
            self.textEdit.setText(text_post[0])
        except:
            pass


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # Вызываем метод для загрузки интерфейса из класса Ui_MainWindow,
        # остальное без изменений
        self.setupUi(self)

# СТИЛИ К ВИДЖЕТАМ
style = '''               
    QFrame#horizontalFrame {
        background-color: rgb(0, 0, 255);   
    }
    
    QLabel#label{
        color: white;
    }
    
    QLabel#label_2{
        font-size: 15px;
        font-weight: bold;
    }
    
    QComboBox {
        background-color: blue;
        font-size: 17px;
        color: white;
    }
    
    QPushButton#pushButton {
        background-color: blue;
        color: white;
        font-size: 15px;
    }
    
    QPushButton#pushButton_2 {
        font-size: 15px;
        font-weight: bold;
    }
    
    QTextEdit{
        font-size: 20px;    
    }
    
    QListWidget {
        background-color: rgb(204, 0, 2);
        color: white;
        font-size: 18px;
    }

    QLabel#label_3 {
        background-image: url(soc.PNG);
    }




    '''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
