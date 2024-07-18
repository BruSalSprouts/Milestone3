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

        # Creation of QWidgets that will be updated throughout the program
        self._stateSelection = QComboBox() # Dropdown menu for states, also selects a state
        self._citySelection = QListWidget() # List of cities in the selected state, also selects a city
        self._zipcodeSelection = QListWidget() # List of zipcodes in the selected city, also selects a zipcode
        self._businessSelection = QTableWidget() # Table of businesses in the selected zipcode
        self._zipcodeNumBusinesses = QLineEdit() # Number of businesses in the selected zipcode
        self._zipcodePopulation = QLineEdit() # Total population of the selected zipcode
        self._zipcodeAverageIncome = QLineEdit() # Average income of the selected zipcode
        self._topZipcodeCategories = QListWidget() # Top categories of businesses in the selected zipcode


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
        self._zipcodeSelection.itemSelectionChanged.connect(self.updateZipcodeStats)

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
        # self._zipcodeNumBusinesses = QLineEdit()

        text2_label = QLabel("Total Population")
        # self._zipcodePopulation = QLineEdit()

        text3_label = QLabel("Average Income:")
        # self._zipcodeAverageIncome = QLineEdit()

        list_label = QLabel("Top Categories:")
        # self._topZipcodeCategories = QListWidget()
        
        self._zipcodeNumBusinesses.setFixedSize(150, 25)
        self._zipcodePopulation.setFixedSize(150, 25)
        self._zipcodeAverageIncome.setFixedSize(150, 25)
        self._topZipcodeCategories.setFixedSize(470, 140)

        layout.addWidget(text1_label)
        layout.addWidget(self._zipcodeNumBusinesses)
        layout.addWidget(text2_label)
        layout.addWidget(self._zipcodePopulation)
        layout.addWidget(text3_label)
        layout.addWidget(self._zipcodeAverageIncome)
        layout.addWidget(list_label)
        layout.addWidget(self._topZipcodeCategories)
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

    def updateZipcodeStats(self):
        try:
            zipItem = self._zipcodeSelection.currentItem()
            zipcode = zipItem.text() if zipItem else ''

            # This query will be in charge of getting the number of businesses in the selected zipcode
            businessCountQuery ='SELECT COUNT(*) FROM business WHERE postal_code=\'' + zipcode + '\''
            # params = [zipcode]
            # params.append(zipcode)

            self._cursor.execute(businessCountQuery)
            businessCount = self._cursor.fetchone()
            self._zipcodeNumBusinesses.setText(str(businessCount[0]))

            # This query will be in charge of getting the total population and average income of the selected zipcode
            populationQuery = 'SELECT population, "meanIncome" FROM "zipcodeData" WHERE zipcode=\'' + zipcode + '\''
            self._cursor.execute(populationQuery)
            population = self._cursor.fetchone()
            self._zipcodePopulation.setText(str(population[0]))
            self._zipcodeAverageIncome.setText(str(population[1]))

            # This query will be in charge of getting the top categories of the selected zipcode
            # topCategoriesQuery = 'SELECT category, COUNT(*) FROM business WHERE zipcode=' + zipcode + ' GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5'
            # self._cursor.execute(topCategoriesQuery)
            # topCategories = self._cursor.fetchall()
            # self._topZipcodeCategories.clear()
            # self._topZipcodeCategories.addItems([category[0] for category in topCategories])
        except Exception as e:
            print("Error updating zipcode stats: ", e)
            traceback.print_exc

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