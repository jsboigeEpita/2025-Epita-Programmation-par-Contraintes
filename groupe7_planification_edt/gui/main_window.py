from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from parameters_page import ParametersPage
from results_page import ResultsPage
from solver_worker import SolverWorker


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("School Schedule Planner")
        self.resize(1000, 800)

        # Load the stylesheet
        self.setStyleSheet(open("styler.qss", "r").read())

        # Create a stack widget to swap pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create pages
        self.param_page = ParametersPage()
        self.results_page = ResultsPage()

        self.stack.addWidget(self.param_page)
        self.stack.addWidget(self.results_page)

        # Connect signals. Use toggle_solver so that clicking the button when running cancels.
        self.param_page.runModelSignal.connect(self.toggle_solver)
        self.results_page.backSignal.connect(self.show_parameters)

        self.thread = None
        self.worker = None
        self.model_running = False

    @pyqtSlot(dict)
    def toggle_solver(self, params):
        if not self.model_running:
            # Start the solver
            self.param_page.runButton.setText("Model is running... Click again to stop the model")
            self.model_running = True
            self.thread = QThread()
            self.worker = SolverWorker(params)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.run)
            self.worker.finished.connect(self.solver_finished)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()
        else:
            # Cancel the running model and remain on the parameters page.
            if self.worker is not None:
                self.worker.cancel()
            self.model_running = False
            self.param_page.runButton.setText("Run Model")
            # Stay on the parameters page; the solver_finished slot will handle cancellation.

    @pyqtSlot(dict)
    def solver_finished(self, result):
        # Reset running state and button text.
        self.model_running = False
        self.param_page.runButton.setText("Run Model")

        # If the model was cancelled, show a message and remain on parameters page.
        if "error" in result and result["error"] == "Model was cancelled.":
            # Optionally, show a message box here.
            # For this example, we just switch back to the parameters page.
            self.stack.setCurrentWidget(self.param_page)
        else:
            # Otherwise, update results and show the results page.
            self.results_page.update_results(result)
            self.stack.setCurrentWidget(self.results_page)

    @pyqtSlot()
    def show_parameters(self):
        self.stack.setCurrentWidget(self.param_page)