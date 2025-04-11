from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QPushButton, QSpinBox,
                             QDoubleSpinBox, QHeaderView, QGroupBox)
from PyQt5.QtCore import pyqtSignal


class ParametersPage(QWidget):
    # Signal that sends parameters (as a dict) when the user clicks “Run Model”
    runModelSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        # Group for subjects (matières)
        matieresGroup = QGroupBox("Matières (Subject and Hours)")
        matieresLayout = QVBoxLayout()
        self.matieresTable = QTableWidget(0, 2)
        self.matieresTable.setHorizontalHeaderLabels(["Matière", "Heures"])
        self.matieresTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        matieresLayout.addWidget(self.matieresTable)
        matieresGroup.setLayout(matieresLayout)
        layout.addWidget(matieresGroup)

        # Pre-populate the subjects table with default values.
        default_matieres = [
            ("Histoire", "4"),
            ("Maths", "6"),
            ("Physique-Chimie", "6"),
            ("Philosophie", "4"),
            ("Sport", "3"),
            ("Anglais", "3"),
            ("Espagnol", "2"),
            ("Maths expertes", "2")
        ]
        self.matieresTable.setRowCount(len(default_matieres))
        for row, (matiere, heures) in enumerate(default_matieres):
            self.matieresTable.setItem(row, 0, QTableWidgetItem(matiere))
            self.matieresTable.setItem(row, 1, QTableWidgetItem(heures))

        # Group for teachers (enseignants)
        enseignantsGroup = QGroupBox("Enseignants (Teacher and Subject)")
        enseignantsLayout = QVBoxLayout()
        self.enseignantsTable = QTableWidget(0, 2)
        self.enseignantsTable.setHorizontalHeaderLabels(["Nom", "Matière"])
        self.enseignantsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        enseignantsLayout.addWidget(self.enseignantsTable)
        enseignantsGroup.setLayout(enseignantsLayout)
        layout.addWidget(enseignantsGroup)

        # Pre-populate the teachers table with default values.
        default_enseignants = [
            ("Nom1", "Histoire"),
            ("Nom11", "Histoire"),
            ("Nom2", "Maths"),
            ("Nom12", "Maths"),
            ("Nom3", "Physique-Chimie"),
            ("Nom13", "Physique-Chimie"),
            ("Nom4", "Philosophie"),
            ("Nom14", "Philosophie"),
            ("Nom5", "Sport"),
            ("Nom15", "Sport"),
            ("Nom6", "Anglais"),
            ("Nom16", "Anglais"),
            ("Nom7", "Maths expertes"),
            ("Nom17", "Maths expertes"),
            ("Nom8", "Espagnol"),
            ("Nom18", "Espagnol"),
        ]
        self.enseignantsTable.setRowCount(len(default_enseignants))
        for row, (nom, matiere) in enumerate(default_enseignants):
            self.enseignantsTable.setItem(row, 0, QTableWidgetItem(nom))
            self.enseignantsTable.setItem(row, 1, QTableWidgetItem(matiere))

        # Group for number of classes and salles.
        csGroup = QGroupBox("Classes and Salles")
        csLayout = QHBoxLayout()
        csLayout.addWidget(QLabel("Nb Classes:"))
        self.classesSpin = QSpinBox()
        self.classesSpin.setMinimum(1)
        self.classesSpin.setValue(8)
        csLayout.addWidget(self.classesSpin)
        csLayout.addWidget(QLabel("Nb Salles:"))
        self.sallesSpin = QSpinBox()
        self.sallesSpin.setMinimum(1)
        self.sallesSpin.setValue(8)
        csLayout.addWidget(self.sallesSpin)
        csGroup.setLayout(csLayout)
        layout.addWidget(csGroup)

        # Group for model time parameter.
        timeGroup = QGroupBox("Model Time (seconds)")
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(QLabel("Max Time:"))
        self.modelTimeSpin = QDoubleSpinBox()
        self.modelTimeSpin.setMinimum(1.0)
        self.modelTimeSpin.setMaximum(600.0)
        self.modelTimeSpin.setValue(60.0)
        self.modelTimeSpin.setSingleStep(1.0)
        timeLayout.addWidget(self.modelTimeSpin)
        timeGroup.setLayout(timeLayout)
        layout.addWidget(timeGroup)

        # Run Model button.
        self.runButton = QPushButton("Run Model")
        self.runButton.clicked.connect(self.on_run)
        layout.addWidget(self.runButton)

        self.setLayout(layout)

    def on_run(self):
        # Gather parameters from the UI
        matieres = {}
        for row in range(self.matieresTable.rowCount()):
            matiere_item = self.matieresTable.item(row, 0)
            heures_item = self.matieresTable.item(row, 1)
            if matiere_item and heures_item:
                try:
                    matieres[matiere_item.text()] = int(heures_item.text())
                except ValueError:
                    continue

        enseignants = {}
        for row in range(self.enseignantsTable.rowCount()):
            nom_item = self.enseignantsTable.item(row, 0)
            matiere_item = self.enseignantsTable.item(row, 1)
            if nom_item and matiere_item:
                enseignants[nom_item.text()] = matiere_item.text()

        params = {
            "matieres": matieres,
            "enseignants": enseignants,
            "nb_classes": self.classesSpin.value(),
            "nb_salles": self.sallesSpin.value(),
            # Days and hours are fixed for this example.
            "jours": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"],
            "heures": ["8h30-9h30", "9h30-10h30", "10h30-11h30", "11h30-12h30", "14h-15h", "15h-16h", "16h-17h",
                       "17h-18h"],
            "model_time": self.modelTimeSpin.value()
        }
        self.runModelSignal.emit(params)