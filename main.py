import sys
from create_db import create_db
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, \
    QDoubleSpinBox, QSpinBox, QPushButton, QDialog, QVBoxLayout, QMessageBox
from PyQt6 import uic


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

        self.add_button.clicked.connect(self.open_add_coffee_form)
        self.edit_button.clicked.connect(self.open_edit_coffee_form)
        self.delete_button.clicked.connect(self.delete_coffee)

    def load_data(self):
        cursor = self.connection.cursor()
        query_result = cursor.execute("SELECT * FROM coffee").fetchall()
        if query_result:
            self.tableWidget.setRowCount(len(query_result))
            for row_index, row_data in enumerate(query_result):
                for col_index, value in enumerate(row_data):
                    self.tableWidget.setItem(row_index, col_index, QTableWidgetItem(str(value)))

    def open_add_coffee_form(self):
        form = AddEditCoffeeForm(connection=self.connection)
        form.exec()
        self.load_data()

    def open_edit_coffee_form(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row != -1:
            coffee_id = self.tableWidget.item(selected_row, 0).text()
            cursor = self.connection.cursor()
            coffee_data = cursor.execute("SELECT * FROM coffee WHERE ID = ?", (coffee_id,)).fetchone()
            form = AddEditCoffeeForm(coffee_data, connection=self.connection)
            form.exec()
            self.load_data()
        else:
            self.show_error_message("Вы не выбрали запись для редактирования.")

    def delete_coffee(self):
        selected_row = self.tableWidget.currentRow()
        if selected_row != -1:
            coffee_id = self.tableWidget.item(selected_row, 0).text()
            cursor = self.connection.cursor()
            try:
                cursor.execute("DELETE FROM coffee WHERE ID = ?", (coffee_id,))
                self.connection.commit()
                self.load_data()
                self.label_status.setText("Запись удалена!")
            except Exception as e:
                self.show_error_message(f"Ошибка при удалении: {e}")
        else:
            self.show_error_message("Вы не выбрали запись для удаления.")

    def show_error_message(self, message):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Icon.Critical)
        error_message.setWindowTitle("Ошибка")
        error_message.setText(message)
        error_message.exec()


class AddEditCoffeeForm(QDialog):
    def __init__(self, coffee_data=None, connection=None):
        super().__init__()
        uic.loadUi("addEditCoffeeForm.ui", self)
        self.connection = connection
        self.coffee_data = coffee_data
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.coffee_name_edit: QLineEdit = self.findChild(QLineEdit, 'coffee_name_edit')
        self.roast_degree_combo: QComboBox = self.findChild(QComboBox, 'roast_degree_combo')
        self.ground_or_whole_combo: QComboBox = self.findChild(QComboBox, 'ground_or_whole_combo')
        self.taste_desc_edit: QLineEdit = self.findChild(QLineEdit, 'taste_desc_edit')
        self.price_spin: QDoubleSpinBox = self.findChild(QDoubleSpinBox, 'price_spin')
        self.volume_spin: QSpinBox = self.findChild(QSpinBox, 'volume_spin')
        self.save_button: QPushButton = self.findChild(QPushButton, 'save_button')

        self.populate_comboboxes()

        if coffee_data:
            self.coffee_name_edit.setText(coffee_data[1])
            self.roast_degree_combo.setCurrentText(coffee_data[2])
            self.ground_or_whole_combo.setCurrentText(coffee_data[3])
            self.taste_desc_edit.setText(coffee_data[4])
            self.price_spin.setValue(coffee_data[5])
            self.volume_spin.setValue(coffee_data[6])

        self.save_button.clicked.connect(self.save_coffee)

    def populate_comboboxes(self):
        roast_degrees = ['Светлая', 'Средняя', 'Темная']
        for degree in roast_degrees:
            self.roast_degree_combo.addItem(degree)

        ground_or_whole = ['Молотый', 'В зернах']
        for option in ground_or_whole:
            self.ground_or_whole_combo.addItem(option)

    def save_coffee(self):
        coffee_name = self.coffee_name_edit.text()
        roast_degree = self.roast_degree_combo.currentText()
        ground_or_whole = self.ground_or_whole_combo.currentText()
        taste_desc = self.taste_desc_edit.text()
        price = self.price_spin.value()
        volume = self.volume_spin.value()

        if not coffee_name or not roast_degree or not ground_or_whole or not taste_desc:
            self.show_error_message("Пожалуйста, заполните все поля!")
            return

        try:
            cursor = self.connection.cursor()
            if self.coffee_data:
                cursor.execute('''UPDATE coffee
                                  SET coffee_name = ?, roast_degree = ?, ground_or_whole_beans = ?, taste_description = ?, price = ?, package_volume = ?
                                  WHERE ID = ?''',
                               (coffee_name, roast_degree, ground_or_whole, taste_desc, price, volume,
                                self.coffee_data[0]))
                self.connection.commit()
            else:
                cursor.execute('''INSERT INTO coffee (coffee_name, roast_degree, ground_or_whole_beans, taste_description, price, package_volume)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (coffee_name, roast_degree, ground_or_whole, taste_desc, price, volume))
                self.connection.commit()

            self.accept()

        except Exception as e:
            self.show_error_message(f"Произошла ошибка при сохранении данных: {e}")

    def show_error_message(self, message):
        error_message = QMessageBox(self)
        error_message.setIcon(QMessageBox.Icon.Critical)
        error_message.setWindowTitle("Ошибка")
        error_message.setText(message)
        error_message.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = CoffeeApp()
    main_window.show()
    sys.exit(app.exec())
