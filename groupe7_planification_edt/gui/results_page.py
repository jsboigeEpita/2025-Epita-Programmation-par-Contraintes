from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                             QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import pyqtSignal


class ResultsPage(QWidget):
    # Signal to return to the parameters page.
    backSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Table names in black color
        self.setStyleSheet(open("styler.qss", "r").read())

        self.layout = QVBoxLayout()
        self.infoLabel = QLabel("Results:")
        self.layout.addWidget(self.infoLabel)

        # A tab widget to display each class's schedule.
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.backButton = QPushButton("Back to Parameters")
        self.backButton.clicked.connect(lambda: self.backSignal.emit())
        self.layout.addWidget(self.backButton)

        self.setLayout(self.layout)

    def update_results(self, result):
        # Display the objective value.
        self.infoLabel.setText(f"Objective Value: {result.get('objective_value', 'N/A')}")

        self.tabs.clear()

        schedules = result.get("schedules", {})
        jours = result.get("jours", [])
        heures = result.get("heures", [])

        # For each class, create a table showing its schedule.
        for classe, schedule in schedules.items():
            table = QTableWidget()
            table.setRowCount(len(heures))
            table.setColumnCount(len(jours))
            table.setHorizontalHeaderLabels(jours)
            table.setVerticalHeaderLabels(heures)
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

            for i, heure in enumerate(heures):
                for j, jour in enumerate(jours):
                    cell_text = schedule.get(jour, {}).get(heure, "---")
                    table.setItem(i, j, QTableWidgetItem(cell_text))

            self.tabs.addTab(table, f"Classe {classe}")