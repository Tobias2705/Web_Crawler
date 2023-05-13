import os
import csv
import sys
import sqlite3

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QTextEdit, QMessageBox, QDialog, QGridLayout, QLineEdit, QTableWidget, QTableWidgetItem, QComboBox, QFileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'database')) + "\\KNF_sentiment.db"

        self.setWindowTitle('KNF Sentiment Client')
        self.setGeometry(0, 0, 800, 600)

        self.show_main_screen()

    def show_main_screen(self, table=None):
        if table:
            table.hide()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        nav_bar = QWidget()
        nav_bar.setFixedWidth(150)
        nav_layout = QVBoxLayout(nav_bar)

        commands_btn = QPushButton('Wykonaj polecenie')
        tables_btn = QPushButton('Pokaż tabele')
        export_btn = QPushButton('Eksport do CSV')

        text_edit = QTextEdit()

        nav_layout.addWidget(commands_btn)
        nav_layout.addWidget(tables_btn)
        nav_layout.addWidget(export_btn)
        layout.addWidget(nav_bar)
        layout.addWidget(text_edit)

        commands_btn.clicked.connect(self.execute_command_dialog)
        tables_btn.clicked.connect(self.show_table_dialog)
        export_btn.clicked.connect(self.export_to_csv_dialog)

    def execute_command_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Wykonaj polecenie SQL')
        dialog.setModal(True)

        layout = QGridLayout(dialog)

        query_label = QLabel('Wprowadź polecenie SQL:')
        query_text = QLineEdit()

        ok_button = QPushButton('Wykonaj')
        cancel_button = QPushButton('Anuluj')

        layout.addWidget(query_label, 0, 0)
        layout.addWidget(query_text, 0, 1)
        layout.addWidget(ok_button, 1, 0)
        layout.addWidget(cancel_button, 1, 1)

        ok_button.clicked.connect(lambda: self.execute_command(query_text.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def execute_command(self, query, dialog):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute(query)
            conn.commit()
            result = c.fetchall()
            conn.close()

            if result:
                table = QTableWidget(self)
                table.setColumnCount(len(result[0]))
                table.setRowCount(len(result))

                for i, row in enumerate(result):
                    for j, col in enumerate(row):
                        item = QTableWidgetItem(str(col))
                        table.setItem(i, j, item)

                headers = [description[0] for description in c.description]
                table.setHorizontalHeaderLabels(headers)

                back_btn = QPushButton('Powrót', self)
                back_btn.clicked.connect(lambda: self.show_main_screen(table=table))

                layout = QVBoxLayout()
                layout.addWidget(table)
                layout.addWidget(back_btn)
                widget = QWidget()
                widget.setLayout(layout)

                self.setCentralWidget(widget)
                self.update()
            else:
                self.statusBar().showMessage('Polecenie wykonane poprawnie.')
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, 'Błąd', 'Wystąpił błąd podczas wykonywania polecenia SQL: {}'.format(str(e)))
            dialog.reject()

    def show_table_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Pokaż tabelę')
        dialog.setModal(True)

        layout = QGridLayout(dialog)

        table_label = QLabel('Wybierz tabelę:')
        table_combo = QComboBox()

        ok_button = QPushButton('Wyświetl')
        cancel_button = QPushButton('Anuluj')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        for table in tables:
            if table[0] != 'sqlite_sequence':
                table_combo.addItem(table[0])
        conn.close()

        layout.addWidget(table_label, 0, 0)
        layout.addWidget(table_combo, 0, 1)
        layout.addWidget(ok_button, 1, 0)
        layout.addWidget(cancel_button, 1, 1)

        ok_button.clicked.connect(lambda: self.show_table(table_combo.currentText(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def show_table(self, table_name, dialog):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM " + table_name)
            result = c.fetchall()
            conn.close()

            if result:
                table = QTableWidget(self)
                table.setColumnCount(len(result[0]))
                table.setRowCount(len(result))

                for i, row in enumerate(result):
                    for j, col in enumerate(row):
                        item = QTableWidgetItem(str(col))
                        table.setItem(i, j, item)

                headers = [description[0] for description in c.description]
                table.setHorizontalHeaderLabels(headers)

                back_btn = QPushButton('Powrót', self)
                back_btn.clicked.connect(self.show_main_screen)

                layout = QVBoxLayout()
                layout.addWidget(table)
                layout.addWidget(back_btn)
                widget = QWidget()
                widget.setLayout(layout)

                self.setCentralWidget(widget)
                self.update()
            else:
                self.statusBar().showMessage('Wybrana tabela jest pusta.')
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, 'Błąd', 'Wystąpił błąd podczas wyświetlania tabeli: {}'.format(str(e)))
            dialog.reject()

    def export_to_csv_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Eksportuj do CSV')
        dialog.setModal(True)

        layout = QGridLayout(dialog)

        table_label = QLabel('Wybierz tabelę:')
        table_combo = QComboBox()

        location_label = QLabel('Wybierz lokalizację:')
        location_lineedit = QLineEdit()
        location_button = QPushButton('Wybierz')

        ok_button = QPushButton('Eksportuj')
        cancel_button = QPushButton('Anuluj')

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = c.fetchall()

        for table in tables:
            if table[0] != 'sqlite_sequence':
                table_combo.addItem(table[0])
        conn.close()

        layout.addWidget(table_label, 0, 0)
        layout.addWidget(table_combo, 0, 1)
        layout.addWidget(location_label, 1, 0)
        layout.addWidget(location_lineedit, 1, 1)
        layout.addWidget(location_button, 1, 2)
        layout.addWidget(ok_button, 2, 0)
        layout.addWidget(cancel_button, 2, 1)

        location_button.clicked.connect(lambda: self.select_location(location_lineedit))
        ok_button.clicked.connect(
            lambda: self.export_to_csv(table_combo.currentText(), location_lineedit.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec_()

    def select_location(self, location_lineedit):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Wybierz lokalizację", "", "CSV Files (*.csv)", options=options)
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            location_lineedit.setText(filename)

    def export_to_csv(self, table_name, location, dialog):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT * FROM " + table_name)
            result = c.fetchall()
            conn.close()

            if result:
                headers = [description[0] for description in c.description]
                with open(location, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                    writer.writerow(headers)
                    for row in result:
                        writer.writerow(row)

                self.statusBar().showMessage('Tabela została wyeksportowana do pliku CSV.')
            else:
                self.statusBar().showMessage('Wybrana tabela jest pusta.')

            dialog.accept()
        except Exception as e:
            QMessageBox.warning(self, 'Błąd',
                                'Wystąpił błąd podczas eksportowania tabeli do pliku CSV: {}'.format(str(e)))
            dialog.reject()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
