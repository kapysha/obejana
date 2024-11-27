import sqlite3
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QTableWidget

from create_db import create_db


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)
        self.connection = sqlite3.connect("coffee.sqlite")
        cursor = self.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='coffee'")
        if not cursor.fetchone():
            create_db()

        self.tableWidget: QTableWidget = self.tableWidget
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(
            ['ID', 'Coffee Name', 'Roast Degree', 'Ground/Whole Beans', 'Taste Description', 'Price', 'Package Volume'])
        self.load_data()

    def load_data(self):
        cursor = self.connection.cursor()
        query_result = cursor.execute("SELECT * FROM coffee").fetchall()
        if query_result:
            self.tableWidget.setRowCount(len(query_result))
            for row_index, row_data in enumerate(query_result):
                for col_index, value in enumerate(row_data):
                    self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value)))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CoffeeApp()
    main_window.show()
    sys.exit(app.exec())
