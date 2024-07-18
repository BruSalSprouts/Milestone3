import sys
import traceback
import psycopg2
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QLabel, QComboBox, QListWidget, QLineEdit, QPushButton, QTableWidgetItem, 
    QTableWidget, QHeaderView
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        #define postgresql variables
        self._conn = psycopg2.connect(database="milestonedb2", user="postgres", password="Bettaman65065", host="127.0.0.1", port=5432)
        self._cursor = self._conn.cursor()

        # Create QWidgets that will be updated throughout the program
        self._stateSelection = QComboBox()
        self._citySelection = QListWidget()
        self._zipcodeSelection = QListWidget()
        self._businessSelection = QTableWidget()

        self._initUI()

    def _initUI(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Top row
        top_row = QHBoxLayout()
        left_pane = self.create_left_pane()
        right_pane = self.create_right_pane()
        top_row.addWidget(left_pane)
        top_row.addWidget(right_pane)

        # Middle row
        middle_row = QHBoxLayout()
        middle_pane = self.create_middle_pane()
        middle_row.addWidget(middle_pane)

        # Bottom row
        bottom_row = QHBoxLayout()
        bottom_pane = self.create_bottom_pane()
        bottom_row.addWidget(bottom_pane)

        # Adding rows to the main layout
        main_layout.addLayout(top_row)
        main_layout.addLayout(middle_row)
        main_layout.addLayout(bottom_row)

        self.setCentralWidget(central_widget)

    def create_left_pane(self):
        group_box = QGroupBox("Select Location")
        layout = QVBoxLayout()

        dropdown_label = QLabel("State:")
        # self._stateSelection = QComboBox()
        self._cursor.execute("SELECT DISTINCT state FROM business ORDER BY state;")
        results = self._cursor.fetchall()
        self._stateSelection.addItems([state[0] for state in results])
        self._stateSelection.currentIndexChanged.connect(self.updateCities)

        list1_label = QLabel("City:")
        # self._citySelection = QListWidget()

        list2_label = QLabel("Zipcode:")
        # self._zipcodeSelection = QListWidget()

        # Updating the cities and zipcodes
        self._citySelection.itemSelectionChanged.connect(self.updateZipcodes)
        self._zipcodeSelection.itemSelectionChanged.connect(self.updateBusinesses)

        self._stateSelection.setFixedSize(50, 25)
        self._citySelection.setFixedSize(180, 140)
        self._zipcodeSelection.setFixedSize(100, 140)

        # Creating table views for business selection
        

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(dropdown_label)
        horizontal_layout.addWidget(self._stateSelection)
        horizontal_layout.addWidget(list1_label)
        horizontal_layout.addWidget(self._citySelection)
        horizontal_layout.addWidget(list2_label)
        horizontal_layout.addWidget(self._zipcodeSelection)

        layout.addLayout(horizontal_layout)
        group_box.setLayout(layout)
        self.updateCities()
        return group_box

    def create_right_pane(self):
        group_box = QGroupBox("Zipcode Statistics")
        layout = QVBoxLayout()

        text1_label = QLabel("# of Businesses")
        text1 = QLineEdit()

        text2_label = QLabel("Total Population")
        text2 = QLineEdit()

        text3_label = QLabel("Average Income:")
        text3 = QLineEdit()

        list_label = QLabel("Top Categories:")
        list_widget = QListWidget()

        text1.setFixedSize(150, 25)
        text2.setFixedSize(150, 25)
        text3.setFixedSize(150, 25)
        list_widget.setFixedSize(470, 140)

        layout.addWidget(text1_label)
        layout.addWidget(text1)
        layout.addWidget(text2_label)
        layout.addWidget(text2)
        layout.addWidget(text3_label)
        layout.addWidget(text3)
        layout.addWidget(list_label)
        layout.addWidget(list_widget)
        group_box.setLayout(layout)
        return group_box

    def create_middle_pane(self):
        group_box = QGroupBox("Businesses")
        layout = QHBoxLayout()

        list1_label = QLabel("Select Category for Filtering")
        list1 = QListWidget()

        button1 = QPushButton("Button 1")
        button2 = QPushButton("Button 2")

        list2_label = QLabel("Businesses")
        # self._businessSelection = QTableWidget()
        self._businessSelection.horizontalHeader().setStretchLastSection(True) 
        self._businessSelection.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        list1.setFixedSize(200, 140)
        self._businessSelection.setFixedSize(490, 140)
        button1.setFixedSize(40, 50)
        button2.setFixedSize(40, 50)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(button1)
        vertical_layout.addWidget(button2)

        layout.addWidget(list1_label)
        layout.addWidget(list1)
        layout.addLayout(vertical_layout)
        layout.addWidget(list2_label)
        layout.addWidget(self._businessSelection)
        group_box.setLayout(layout)
        return group_box

    def create_bottom_pane(self):
        group_box = QGroupBox("What's Good?")
        layout = QHBoxLayout()

        button = QPushButton("Button")
        list1_label = QLabel("Popular Businesses (in zipcode):")
        list1 = QListWidget()

        list2_label = QLabel("Succesful Businesses (in zipcode):")
        list2 = QListWidget()

        list1.setFixedSize(300, 140)
        list2.setFixedSize(300, 140)
        button.setFixedSize(20, 20)

        layout.addWidget(button)
        layout.addWidget(list1_label)
        layout.addWidget(list1)
        layout.addWidget(list2_label)
        layout.addWidget(list2)
        group_box.setLayout(layout)
        return group_box

    def updateCities(self):
        print("Updating cities")
        try:
            self._cursor.execute("SELECT DISTINCT city FROM business WHERE state='"+self._stateSelection.currentText()+"' ORDER BY city;")
            results = self._cursor.fetchall()

            self._citySelection.clear()
            self._citySelection.addItems([city[0] for city in results])

            # self._updateBusinesses()
        except Exception as e:
            print("Error updating cities: ", e)
            traceback.print_exc()

    def updateZipcodes(self):
        print("Updating zipcodes")
        try:
            state = self._stateSelection.currentText()
            cityItem = self._citySelection.currentItem()
            city = cityItem.text() if cityItem else ''

            query = "SELECT DISTINCT postal_code FROM business WHERE state=%s"
            params=[state]
            if city:
                query += " AND city=%s"
                params.append(city)
            query += " ORDER BY postal_code;"

            self._cursor.execute(query, tuple(params))
            results = self._cursor.fetchall()

            self._zipcodeSelection.clear()
            self._zipcodeSelection.addItems([zipcode[0] for zipcode in results])

        except Exception as e:
            print("Error updating zip codes: ", e)
            traceback.print_exc()

    def updateBusinesses(self):
        try:
            state = self._stateSelection.currentText()
            cityItem = self._citySelection.currentItem()
            zipItem = self._zipcodeSelection.currentItem()
            city = cityItem.text() if cityItem else ''
            zipCode = zipItem.text() if zipItem else ''

            query = "SELECT DISTINCT name, address, city, stars, review_count, review_rating, num_checkins FROM business WHERE state=%s"
            params = [state]
            if city:
                query += " AND city=%s"
                params.append(city)
            if zipCode:
                query += " AND postal_code=%s"
                params.append(zipCode)
            query += " ORDER BY name;"

            self._cursor.execute(query, tuple(params))
            results = self._cursor.fetchall()

            self._businessSelection.clear()
            self._businessSelection.setRowCount(len(results))
            self._businessSelection.setColumnCount(7)
            headers = ["Name", "Address", "City", "Stars", "Review Count", "Review Rating", "Num Checkins"]
            self._businessSelection.setHorizontalHeaderLabels(headers)
            for row, tup in enumerate(results):
                for col, value in enumerate(tup):
                    item = QTableWidgetItem(str(value)) # Convert values to strings
                    self._businessSelection.setItem(row, col, item)
        except Exception as e:
            print("Error updating businesses: ", e)
            traceback.print_exc()
    
    def closeEvent(self, event):
        self._cursor.close()
        self._conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    
    window.setWindowTitle("CptS 451 - Business Analytics")
    window.setGeometry(150,100,1000,600)
    window.show()
    sys.exit(app.exec())