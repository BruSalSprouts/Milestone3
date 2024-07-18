import sys
from PyQt6.QtWidgets import QWidget, QApplication, QMainWindow, QGridLayout, QLabel, QComboBox, QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QVBoxLayout
import psycopg2
import traceback

class YelpApp(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        #define postgresql variables
        self._conn = psycopg2.connect(database="milestonedb2", user="postgres", password="Bettaman65065", host="127.0.0.1", port=5432)
        self._cursor = self._conn.cursor()

        #initialize UI
        self._initUI()

    def _initUI(self):
        self._layout = QGridLayout(self)
        self.setLayout(self._layout)

        #create labels
        self._header = QLabel("CPTS451 Yelp Buisnesses", self)
        self._locationHeader = QLabel("Select Location", self)
        self._stateCityHeader = QLabel("State/City", self)
        self._stateHeader = QLabel("State", self)
        self._cityHeader = QLabel("City", self)
        self._zipcodeHeader = QLabel("Zipcode", self)
        self._businessHeader = QLabel("Business", self)

        #create combo box for state selection
        self._stateSelection = QComboBox(self)
        self._cursor.execute("SELECT DISTINCT state FROM business ORDER BY state;")
        results = self._cursor.fetchall()
        self._stateSelection.addItems([state[0] for state in results])
        self._stateSelection.currentIndexChanged.connect(self.updateCities)

        #create list views for city and zipcode selection
        self._citySelection = QListWidget(self)
        self._zipcodeSelection = QListWidget(self)
        self._citySelection.itemSelectionChanged.connect(self.updateZipcodes)
        self._zipcodeSelection.itemSelectionChanged.connect(self._updateBusinesses)
       
        # self._updateZipcodes()

        #create table views for business selection
        self._businessSelection = QTableWidget(self)
        self._businessSelection.horizontalHeader().setStretchLastSection(True) 
        self._businessSelection.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        #populate layout
        self._layout.addWidget(self._header,0,0,1,4)
        self._layout.addWidget(self._locationHeader,1,0,1,3)
        self._layout.addWidget(self._stateHeader,2,0,1,1)
        self._layout.addWidget(self._cityHeader,2,1,1,1)
        self._layout.addWidget(self._zipcodeHeader,2,2,1,1)
        self._layout.addWidget(self._stateSelection,3,0,1,1)
        self._layout.addWidget(self._citySelection,3,1,1,1)
        self._layout.addWidget(self._zipcodeSelection,3,2,1,1)
        self._layout.addWidget(self._businessHeader,1,3,1,1)
        self._layout.addWidget(self._businessSelection,3,3,2,1)

        # self._layout.addWidget(self._stateCityHeader,1,0,1,2)
        # self._layout.addWidget(self._businessHeader,1,2,1,1)
        # self._layout.addWidget(self._stateHeader,2,0,1,1)
        # self._layout.addWidget(self._cityHeader,3,0,1,1)
        # self._layout.addWidget(self._stateSelection,2,1,1,1)
        # self._layout.addWidget(self._citySelection,3,1,1,1)
        # self._layout.addWidget(self._businessSelection,2,2,2,1)

        self.updateCities()

    def _updateZipcodes(self):
        print("Updating zipcodes")
        try:
            self._cursor.execute("SELECT DISTINCT postal_code FROM business WHERE state='"+self._stateSelection.currentText()+"' ORDER BY postal_code;")
            results = self._cursor.fetchall()

            self._zipcodeSelection.clear()
            self._zipcodeSelection.addItems([zipcode[0] for zipcode in results])

            self._updateCities()
        except Exception as e:
            print("Error updating zip codes: ", e)
            traceback.print_exc()

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

    def _updateCities(self):
        try:
            state = self._stateSelection.currentText()
            zipItem = self._zipcodeSelection.currentItem()
            zipCode = zipItem.text() if zipItem else ''

            query = "SELECT DISTINCT city FROM business WHERE state=%s"
            params=[state]
            if zipCode:
                query += " AND zipcode=%s"
                params.append(zipCode)
            query += " ORDER BY city;"

            self._cursor.execute(query, tuple(params))
            # self._cursor.execute("SELECT DISTINCT city FROM business WHERE state='"+self._stateSelection.currentText()+"' ORDER BY city;")
            results = self._cursor.fetchall()

            self._citySelection.clear()
            self._citySelection.addItems([city[0] for city in results])

            self._updateBusinesses()
        except Exception as e:
            print("Error updating cities: ", e)
            traceback.print_exc()
        
    def _updateBusinesses(self):
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
    window = QMainWindow()
    window.setCentralWidget(YelpApp(window))
    window.setWindowTitle("CptS 451 - Business Analytics")
    window.setGeometry(300,200,1000,600)
    window.show()
    sys.exit(app.exec())