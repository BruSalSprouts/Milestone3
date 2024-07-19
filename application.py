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
        self._filterCategorySelection = QListWidget() # List of categories to filter businesses by from selected zipcode, also can help select a business
        self._zipcodeNumBusinesses = QLineEdit() # Number of businesses in the selected zipcode
        self._zipcodePopulation = QLineEdit() # Total population of the selected zipcode
        self._zipcodeAverageIncome = QLineEdit() # Average income of the selected zipcode
        self._topZipcodeCategories = QListWidget() # Top categories of businesses in the selected zipcode
        self._popularBusinesses = QTableWidget() # Popular businesses in the selected zipcode
        self._successfulBusinesses = QTableWidget() # Successful businesses in the selected zipcode

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

        _stateLabel = QLabel("State:")
        # self._stateSelection = QComboBox()
        self._cursor.execute("SELECT DISTINCT state FROM business ORDER BY state;")
        results = self._cursor.fetchall()
        self._stateSelection.addItems([state[0] for state in results])
        self._stateSelection.currentIndexChanged.connect(self.updateCities)

        _cityLabel = QLabel("City:")
        # self._citySelection = QListWidget()

        _zipcodeLabel = QLabel("Zipcode:")
        # self._zipcodeSelection = QListWidget()

        # Updating the cities and zipcodes
        self._citySelection.itemSelectionChanged.connect(self.updateZipcodes)
        self._zipcodeSelection.itemSelectionChanged.connect(self.updateBusinesses)
        self._zipcodeSelection.itemSelectionChanged.connect(self.updateZipcodeStats)
        self._zipcodeSelection.itemSelectionChanged.connect(self.updateCategoryBusinesses)
        self._zipcodeSelection.itemSelectionChanged.connect(self.updatePopularBusinesses)

        self._stateSelection.setFixedSize(50, 25)
        self._citySelection.setFixedSize(180, 140)
        self._zipcodeSelection.setFixedSize(100, 140)

        # Creating table views for business selection
        

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(_stateLabel)
        horizontal_layout.addWidget(self._stateSelection)
        horizontal_layout.addWidget(_cityLabel)
        horizontal_layout.addWidget(self._citySelection)
        horizontal_layout.addWidget(_zipcodeLabel)
        horizontal_layout.addWidget(self._zipcodeSelection)

        layout.addLayout(horizontal_layout)
        group_box.setLayout(layout)
        self.updateCities()
        return group_box

    def create_right_pane(self):
        group_box = QGroupBox("Zipcode Statistics")
        layout = QVBoxLayout()

        _businessCountLabel = QLabel("# of Businesses")
        # self._zipcodeNumBusinesses = QLineEdit()

        _totalPopulationLabel = QLabel("Total Population")
        # self._zipcodePopulation = QLineEdit()

        _averageIncomeLabel = QLabel("Average Income:")
        # self._zipcodeAverageIncome = QLineEdit()

        _topCategoriesLabel = QLabel("Top Categories:")
        # self._topZipcodeCategories = QListWidget()
        
        self._zipcodeNumBusinesses.setFixedSize(150, 25)
        self._zipcodePopulation.setFixedSize(150, 25)
        self._zipcodeAverageIncome.setFixedSize(150, 25)
        self._topZipcodeCategories.setFixedSize(470, 140)

        layout.addWidget(_businessCountLabel)
        layout.addWidget(self._zipcodeNumBusinesses)
        layout.addWidget(_totalPopulationLabel)
        layout.addWidget(self._zipcodePopulation)
        layout.addWidget(_averageIncomeLabel)
        layout.addWidget(self._zipcodeAverageIncome)
        layout.addWidget(_topCategoriesLabel)
        layout.addWidget(self._topZipcodeCategories)
        group_box.setLayout(layout)

        return group_box

    def create_middle_pane(self):
        group_box = QGroupBox("Businesses")
        layout = QHBoxLayout()

        list1_label = QLabel("Select Category")
        # self._filterCategory = QListWidget()
        self._filterCategorySelection.itemSelectionChanged.connect(self.updateBusinesses)
        self._filterCategorySelection.itemSelectionChanged.connect(self.updatePopularBusinesses)

        _categoryBusinessRefreshButton = QPushButton("Refresh")
        _categoryResetButton = QPushButton("Clear\nFilter")
        _categoryResetButton.clicked.connect(self._businessSelection.clear)
        _categoryResetButton.clicked.connect(self._filterCategorySelection.clear)
        _categoryResetButton.clicked.connect(self.updateBusinesses)
        _categoryResetButton.clicked.connect(self._popularBusinesses.clear)
        _categoryResetButton.clicked.connect(self.updatePopularBusinesses)
        _categoryResetButton.clicked.connect(self._successfulBusinesses.clear)

        list2_label = QLabel("Businesses")
        # self._businessSelection = QTableWidget()
        self._businessSelection.horizontalHeader().setStretchLastSection(True) 
        self._businessSelection.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self._filterCategorySelection.setFixedSize(200, 140)
        self._businessSelection.setFixedSize(600, 140)
        _categoryBusinessRefreshButton.setFixedSize(50, 50)
        _categoryResetButton.setFixedSize(50, 50)

        _middleButtonLayout = QVBoxLayout()
        _middleButtonLayout.addWidget(_categoryBusinessRefreshButton)
        _middleButtonLayout.addWidget(_categoryResetButton)

        layout.addWidget(list1_label)
        layout.addWidget(self._filterCategorySelection)
        layout.addLayout(_middleButtonLayout)
        layout.addWidget(list2_label)
        layout.addWidget(self._businessSelection)
        group_box.setLayout(layout)
        return group_box

    def create_bottom_pane(self):
        group_box = QGroupBox("What's Good?")
        layout = QHBoxLayout()

        button = QPushButton("Button")
        popularBizLabel = QLabel("Popular Businesses (in zipcode)")
        # self._popularBusinesses = QListWidget()

        successfulBizLabel = QLabel("Succesful Businesses (in zipcode)")
        # self._successfulBusinesses = QListWidget()

        self._popularBusinesses.setFixedSize(380, 140)
        self._successfulBusinesses.setFixedSize(380, 140)
        button.setFixedSize(40, 40)

        layout.addWidget(button)
        layout.addWidget(popularBizLabel)
        layout.addWidget(self._popularBusinesses)
        layout.addWidget(successfulBizLabel)
        layout.addWidget(self._successfulBusinesses)
        group_box.setLayout(layout)
        return group_box

    def updateCities(self):
        print("Updating cities")
        try:
            self._cursor.execute("SELECT DISTINCT city FROM business WHERE state='"+self._stateSelection.currentText()+"' ORDER BY city;")
            results = self._cursor.fetchall()

            self._citySelection.clear()
            self._citySelection.addItems([city[0] for city in results])

            self._filterCategorySelection.clear()
            self._businessSelection.clear()
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
            categoryItem = self._filterCategorySelection.currentItem()
            category = categoryItem.text() if categoryItem else ''

            if category:
                print("Updating businesses with category filter")
                query = "SELECT DISTINCT b.name, b.address, b.city, b.stars, b.review_count AS Reviews, b.review_rating AS Rating, b.num_checkins AS Checkins FROM business b LEFT JOIN categories c on b.business_id = c.business_id WHERE b.state=%s"
                params = [state]
                if city:
                    query += " AND city=%s"
                    params.append(city)
                if zipCode:
                    query += " AND postal_code=%s"
                    params.append(zipCode)
                if category:
                    query += " AND c.category=%s"
                    params.append(category)
                query += "ORDER BY b.name;"
            else:
                print("Updating businesses without category filter")
                query = 'SELECT DISTINCT name, address, city, stars, review_count AS "Reviews", review_rating AS "Rating", num_checkins AS "Checkins" FROM business WHERE state=%s'
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
            print("Updating zipcode stats")
            zipItem = self._zipcodeSelection.currentItem()
            zipcode = zipItem.text() if zipItem else ''

            # This query will be in charge of getting the number of businesses in the selected zipcode
            businessCountQuery ='SELECT COUNT(*) FROM business WHERE postal_code=\'' + zipcode + '\''
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
            # To note, the categories are not stored in the business table, so we will need to join the business table with the category table named "categories". It's schema is categories (business_id, category)
            topCategoriesQuery = 'SELECT category FROM business JOIN categories ON business.business_id = categories.business_id WHERE postal_code=\'' + zipcode + '\' GROUP BY category ORDER BY COUNT(*) DESC LIMIT 7'
            self._cursor.execute(topCategoriesQuery)
            topCategories = self._cursor.fetchall()
            self._topZipcodeCategories.clear()
            self._topZipcodeCategories.addItems([category[0] for category in topCategories])
        except Exception as e:
            print("Error updating zipcode stats: ", e)
            traceback.print_exc

    def updateCategoryBusinesses(self):
        try:
            print("Updating category for filtering businesses")
            state = self._stateSelection.currentText()
            cityItem = self._citySelection.currentItem()
            zipItem = self._zipcodeSelection.currentItem()
            city = cityItem.text() if cityItem else ''
            zipCode = zipItem.text() if zipItem else ''

            query = "SELECT DISTINCT c.category FROM categories c LEFT JOIN business b on c.business_id = b.business_id WHERE b.state=%s"
            params = [state]
            if city:
                query += " AND city=%s"
                params.append(city)
            if zipCode:
                query += " AND postal_code=%s"
                params.append(zipCode)
                query += " ORDER BY c.category;"

            self._cursor.execute(query, tuple(params))
            results = self._cursor.fetchall()

            self._filterCategorySelection.clear()
            self._filterCategorySelection.addItems([category[0] for category in results])

        except Exception as e:
            print("Error updating category businesses: ", e)
            traceback.print_exc()

    def resetCategoryBusinesses(self):
        self._filterCategorySelection.clear()
        self._updateBusinesses()

    def updatePopularBusinesses(self):
        try:
            print("Updating popular businesses")
            state = self._stateSelection.currentText()
            cityItem = self._citySelection.currentItem()
            zipItem = self._zipcodeSelection.currentItem()
            categoryItem = self._filterCategorySelection.currentItem()
            city = cityItem.text() if cityItem else ''
            zipCode = zipItem.text() if zipItem else ''
            category = categoryItem.text() if categoryItem else ''
            # We'll be getting the businesses that are doing better than the average business 
            # in the selected zipcode and category (if selected)

            if category:
                query = 'SELECT b.name, b.address, b.review_rating as Rating, b.stars FROM Business b JOIN (SELECT city, AVG(num_checkins) AS avg_checkins FROM Business GROUP BY city) AS city_avg ON b.city = city_avg.city LEFT JOIN categories c ON b.business_id = c.business_id WHERE b.num_checkins > city_avg.avg_checkins AND b.state=%s'
                params = [state]
                if city:
                    query += " AND b.city=%s"
                    params.append(city)
                if zipCode:
                    query += " AND b.postal_code=%s"
                    params.append(zipCode)
                if category:
                    query += " AND c.category=%s"
                    params.append(category)
                query += " GROUP BY b.business_id, b.city, b.name ORDER BY b.city, b.num_checkins DESC;"
            else:
                query = 'SELECT b.name, b.address, b.review_rating as Rating, b.stars FROM Business b JOIN (  SELECT city, AVG(num_checkins) AS avg_checkins FROM Business GROUP BY city) AS city_avg ON b.city = city_avg.city WHERE b.num_checkins > city_avg.avg_checkins AND b.state=%s'
                params = [state]
                if city:
                    query += " AND b.city=%s"
                    params.append(city)
                if zipCode:
                    query += " AND b.postal_code=%s"
                    params.append(zipCode)
                query += " GROUP BY b.business_id, b.city, b.name ORDER BY b.city, b.num_checkins DESC;"
            
            self._cursor.execute(query, tuple(params))
            results = self._cursor.fetchall()

            self._popularBusinesses.clear()
            # self._popularBusinesses.addItems([business[1] for business in results])
            self._popularBusinesses.setRowCount(len(results))
            self._popularBusinesses.setColumnCount(4)
            headers = ["Name", "Address", "Rating", "Stars"]
            self._popularBusinesses.setHorizontalHeaderLabels(headers)
            for row, tup in enumerate(results):
                for col, value in enumerate(tup):
                    item = QTableWidgetItem(str(value)) # Convert values to strings
                    self._popularBusinesses.setItem(row, col, item)

        except:
            print("Error updating popular businesses")
            traceback.print_exc()

    def updateSuccessfulBusinesses(self):
        print("Updating successful businesses")

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