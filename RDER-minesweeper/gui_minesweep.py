#!/usr/bin/env python3

import sys
import os
import traceback
import random
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGridLayout,
    QMessageBox,
    QFileDialog,
    QGroupBox,
    QTextEdit,
    QCheckBox,
    QLineEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

if __package__ is None:
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, path)
try:
    from pcon.minesweeper import Minesweeper
    from pcon.csp_solver import MinesweeperCSPSolver
    from pcon.llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE
except ImportError:
    # Try relative import if executed as a module
    try:
        from .minesweeper import Minesweeper
        from .csp_solver import MinesweeperCSPSolver
        from .llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE
    except ImportError:
        # Fallback to direct imports for compatibility
        from minesweeper import Minesweeper
        from csp_solver import MinesweeperCSPSolver
        from llm_csp_solver import LLMCSPSolver, OPENAI_AVAILABLE


# Check if OpenAI is available
# Try to load dotenv for environment variables
try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    DOTENV_AVAILABLE = False


class OutputRedirector:
    """Class to capture print outputs and redirect them to the GUI"""

    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""

    def write(self, text):
        self.buffer += text
        if "\n" in text:
            self.text_widget.append(self.buffer)
            self.buffer = ""

    def flush(self):
        if self.buffer:
            self.text_widget.append(self.buffer)
            self.buffer = ""


class SolverThread(QThread):
    """Thread for running the solver without freezing the UI"""

    update_signal = pyqtSignal(object)
    finished_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(
        self, game, use_llm=False, step_by_step=False, api_key=None, base_url=None
    ):
        super().__init__()
        self.game = game
        self.use_llm = use_llm
        self.step_by_step = step_by_step
        self.api_key = api_key
        self.base_url = base_url

    def run(self):
        try:
            # Store the original stdout and stderr
            original_stdout = sys.stdout
            original_stderr = sys.stderr

            # Create custom update callback function
            def update_callback(game):
                self.update_signal.emit(game)
                QApplication.processEvents()  # Allow GUI updates

            # Set environment variables for OpenAI if provided
            if self.api_key:
                os.environ["OPENAI_API_KEY"] = self.api_key
            if self.base_url:
                os.environ["OPENAI_BASE_URL"] = self.base_url

            # Initialize solver
            if self.use_llm:
                solver = LLMCSPSolver(self.game)
            else:
                solver = MinesweeperCSPSolver(self.game)

            # Solve the game
            if self.step_by_step:
                for game_state in solver.step_by_step_solve(update_callback):
                    update_callback(game_state)
            else:
                # For non-step-by-step solving, we need to manually update after each solve
                while not self.game.game_over:
                    safe_cells, mines = solver.solve()
                    updated = solver.update_game(auto_play=True)
                    if updated:
                        update_callback(self.game)
                    else:
                        # If no progress was made, break to avoid infinite loop
                        break

            # Restore original stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

            # Emit the final result
            self.finished_signal.emit(self.game)
        except Exception as e:
            self.error_signal.emit(str(e))
            traceback.print_exc()


class GenerateGridDialog(QDialog):
    """Dialog for grid generation parameters"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Générer une grille")

        # Create layout
        layout = QFormLayout(self)

        # Width input
        self.width_input = QSpinBox()
        self.width_input.setRange(5, 30)
        self.width_input.setValue(10)
        layout.addRow("Largeur:", self.width_input)

        # Height input
        self.height_input = QSpinBox()
        self.height_input.setRange(5, 30)
        self.height_input.setValue(10)
        layout.addRow("Hauteur:", self.height_input)

        # Mine count input
        self.mines_input = QSpinBox()
        self.mines_input.setRange(1, 100)
        self.mines_input.setValue(15)
        layout.addRow("Nombre de mines:", self.mines_input)

        # Reveal percentage input
        self.reveal_input = QDoubleSpinBox()
        self.reveal_input.setRange(0.0, 1.0)
        self.reveal_input.setSingleStep(0.1)
        self.reveal_input.setValue(0.3)
        self.reveal_input.setDecimals(2)
        layout.addRow("Pourcentage de révélation:", self.reveal_input)

        # Update mine count range when dimensions change
        self.width_input.valueChanged.connect(self.update_mine_range)
        self.height_input.valueChanged.connect(self.update_mine_range)
        self.update_mine_range()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def update_mine_range(self):
        """Update mine count range based on grid dimensions"""
        max_mines = self.width_input.value() * self.height_input.value() - 1
        self.mines_input.setRange(1, max_mines)

    def get_values(self):
        """Return the input values"""
        return {
            "width": self.width_input.value(),
            "height": self.height_input.value(),
            "mines": self.mines_input.value(),
            "reveal_percentage": self.reveal_input.value()
        }


class MinesweeperSolverGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = None
        self.solver_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("DÉMINEUR - SOLVEUR CSP INTELLIGENT")
        self.setMinimumSize(900, 600)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("DÉMINEUR - SOLVEUR CSP INTELLIGENT")
        title_font = QFont("Arial", 16, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        # Content layout (grid on left, controls on right)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left panel - Grid and status
        left_panel = QVBoxLayout()
        content_layout.addLayout(left_panel, 2)

        # Grid display
        grid_group = QGroupBox("Grille de jeu")
        grid_layout = QVBoxLayout(grid_group)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setSpacing(2)
        grid_layout.addWidget(self.grid_widget)
        left_panel.addWidget(grid_group)

        # Status display
        status_group = QGroupBox("Statistiques")
        status_layout = QVBoxLayout(status_group)
        self.status_label = QLabel(
            "Aucune grille active. Générez ou chargez une grille pour commencer."
        )
        status_layout.addWidget(self.status_label)
        left_panel.addWidget(status_group)

        # Console output
        console_group = QGroupBox("Console")
        console_layout = QVBoxLayout(console_group)
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        console_layout.addWidget(self.console_text)
        left_panel.addWidget(console_group)

        # Create an output redirector and connect it to the console
        self.output_redirector = OutputRedirector(self.console_text)

        # Right panel - Controls
        right_panel = QVBoxLayout()
        content_layout.addLayout(right_panel, 1)

        # Controls group
        controls_group = QGroupBox("Contrôles")
        controls_layout = QVBoxLayout(controls_group)

        # Button: Generate Grid
        generate_btn = QPushButton("1. Générer une grille")
        generate_btn.clicked.connect(self.on_generate_grid)
        controls_layout.addWidget(generate_btn)

        # Button: Load Grid
        load_btn = QPushButton("2. Charger une grille")
        load_btn.clicked.connect(self.on_load_grid)
        controls_layout.addWidget(load_btn)

        # Button: Play Manually
        play_btn = QPushButton("3. Jouer manuellement")
        play_btn.clicked.connect(self.on_play_manually)
        controls_layout.addWidget(play_btn)

        # CSP Solver controls
        csp_group = QGroupBox("Résolution CSP")
        csp_layout = QVBoxLayout(csp_group)

        # Button: Solve with CSP
        csp_btn = QPushButton("4. Résoudre avec CSP")
        csp_btn.clicked.connect(lambda: self.on_solve_with_csp(False))
        csp_layout.addWidget(csp_btn)

        controls_layout.addWidget(csp_group)

        # LLM Solver controls
        llm_group = QGroupBox("Résolution CSP + LLM")
        llm_layout = QVBoxLayout(llm_group)

        # OpenAI API Key
        api_key_layout = QHBoxLayout()
        api_key_layout.addWidget(QLabel("Clé API:"))
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText(
            "Laisser vide pour utiliser OPENAI_API_KEY"
        )
        api_key_layout.addWidget(self.api_key_input)
        llm_layout.addLayout(api_key_layout)

        # OpenAI Base URL
        base_url_layout = QHBoxLayout()
        base_url_layout.addWidget(QLabel("URL de base:"))
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText(
            "Laisser vide pour utiliser OPENAI_BASE_URL"
        )
        base_url_layout.addWidget(self.base_url_input)
        llm_layout.addLayout(base_url_layout)

        # Button: Solve with CSP + LLM
        llm_btn = QPushButton("5. Résoudre avec CSP + LLM")
        llm_btn.clicked.connect(lambda: self.on_solve_with_csp(True))
        llm_layout.addWidget(llm_btn)

        if not OPENAI_AVAILABLE:
            llm_btn.setEnabled(False)
            llm_btn.setToolTip(
                "La bibliothèque OpenAI n'est pas disponible.\nInstallez-la avec 'pip install openai'"
            )

        controls_layout.addWidget(llm_group)

        # Button: Exit
        exit_btn = QPushButton("0. Quitter")
        exit_btn.clicked.connect(self.close)
        controls_layout.addWidget(exit_btn)

        right_panel.addWidget(controls_group)

        # Status bar
        self.statusBar().showMessage("Prêt")

    def redirect_output(self):
        """Redirect stdout and stderr to the console widget"""
        sys.stdout = self.output_redirector
        sys.stderr = self.output_redirector

    def restore_output(self):
        """Restore original stdout and stderr"""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def on_generate_grid(self):
        """Generate a grid interactively using dialog"""
        dialog = GenerateGridDialog(self)
        if dialog.exec():
            # Get values from dialog
            values = dialog.get_values()

            # Redirect output to capture print statements
            self.redirect_output()
            try:
                # Generate grid using the Minesweeper class with reveal_percentage=0.3
                self.game = Minesweeper(
                    width=values["width"],
                    height=values["height"],
                    num_mines=values["mines"],
                )
                # Initialize mines (no first click position specified)
                self.game.initialize_mines()
                
                # Reveal some cells to give the solver something to work with
                total_cells = values["width"] * values["height"]
                non_mine_cells = total_cells - values["mines"]
                cells_to_reveal = int(non_mine_cells * values["reveal_percentage"])
                
                # Create a list of all positions without mines
                safe_positions = []
                for r in range(values["height"]):
                    for c in range(values["width"]):
                        if self.game.solution[r, c] != Minesweeper.MINE:
                            safe_positions.append((r, c))
                
                # Reveal random cells
                positions_to_reveal = random.sample(safe_positions, min(cells_to_reveal, len(safe_positions)))
                for r, c in positions_to_reveal:
                    self.game.reveal(r, c)
                
                self.statusBar().showMessage(
                    f"Grille générée: {values['width']}×{values['height']} avec {values['mines']} mines"
                )
                self.update_grid_display()
            except Exception as e:
                self.show_error(f"Erreur lors de la génération de la grille: {e}")
            finally:
                self.restore_output()

    def on_load_grid(self):
        """Load grid from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une grille",
            "",
            "Fichiers texte (*.txt);;Tous les fichiers (*)",
        )
        if not file_path:
            return

        self.redirect_output()
        try:
            # Read the file content
            with open(file_path, "r") as f:
                board_str = f.read()

            # Create game from string
            self.game = Minesweeper.from_string(board_str)
            self.statusBar().showMessage(f"Grille chargée depuis {file_path}")
            self.update_grid_display()
        except Exception as e:
            self.show_error(f"Erreur lors du chargement de la grille: {e}")
        finally:
            self.restore_output()

    def on_play_manually(self):
        """Allow manual play"""
        if not self.game:
            QMessageBox.warning(
                self, "Erreur", "Veuillez d'abord générer ou charger une grille."
            )
            return

        # Create a modal dialog for manual play
        play_dialog = QDialog(self)
        play_dialog.setWindowTitle("Jeu Manuel")
        play_dialog.setModal(True)

        # Layout
        layout = QVBoxLayout(play_dialog)

        # Game grid widget
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(2)
        layout.addWidget(grid_widget)

        # Instructions
        instructions = QLabel(
            "Cliquez gauche pour révéler une cellule, cliquez droit pour placer/retirer un drapeau."
        )
        layout.addWidget(instructions)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(play_dialog.reject)
        layout.addWidget(buttons)

        # Set up the grid
        game_copy = Minesweeper(self.game.width, self.game.height, self.game.num_mines)
        game_copy.board = self.game.board.copy()
        game_copy.solution = self.game.solution.copy()
        game_copy.revealed_cells = self.game.revealed_cells.copy()
        game_copy.flagged_cells = self.game.flagged_cells.copy()
        game_copy.game_over = self.game.game_over
        game_copy.win = self.game.win

        def update_manual_grid():
            # Clear existing grid
            while grid_layout.count():
                item = grid_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Populate grid
            for y in range(game_copy.height):
                for x in range(game_copy.width):
                    cell_value = game_copy.board[y][x]
                    btn = QPushButton()
                    btn.setFixedSize(40, 40)

                    # Set cell text and style based on state
                    if (y, x) in game_copy.revealed_cells:
                        if game_copy.solution[y][x] == Minesweeper.MINE:
                            btn.setText("💣")
                            btn.setStyleSheet("background-color: red; font-size: 20px;")
                        else:
                            count = game_copy.count_adjacent_mines(y, x)
                            if count > 0:
                                btn.setText(str(count))
                                # Use different colors for different numbers
                                colors = [
                                    "blue",
                                    "green",
                                    "red",
                                    "purple",
                                    "maroon",
                                    "turquoise",
                                    "black",
                                    "gray",
                                ]
                                if count <= len(colors):
                                    btn.setStyleSheet(
                                        f"color: {colors[count - 1]}; font-size: 16px;"
                                    )
                            else:
                                btn.setText("")
                            btn.setStyleSheet(
                                btn.styleSheet() + "background-color: lightgray;"
                            )
                    elif cell_value == Minesweeper.FLAG:
                        btn.setText("🚩")
                        btn.setStyleSheet("font-size: 20px;")
                    else:
                        btn.setText("")

                    # Set up click handlers
                    btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

                    # Left click to reveal
                    btn.clicked.connect(lambda checked, x=x, y=y: reveal_cell(x, y))

                    # Right click to flag
                    btn.customContextMenuRequested.connect(
                        lambda pos, x=x, y=y: toggle_flag(x, y)
                    )

                    grid_layout.addWidget(btn, y, x)

        def reveal_cell(x, y):
            """Handle revealing a cell"""
            if game_copy.reveal(y, x):
                if game_copy.game_over:
                    if game_copy.win:
                        QMessageBox.information(
                            play_dialog,
                            "Félicitations",
                            "Vous avez gagné! Toutes les cases sûres ont été révélées.",
                        )
                    else:
                        QMessageBox.information(
                            play_dialog,
                            "Game Over",
                            "Vous avez touché une mine! Partie terminée.",
                        )
                    play_dialog.accept()
                update_manual_grid()

        def toggle_flag(x, y):
            """Handle flagging/unflagging a cell"""
            game_copy.toggle_flag(y, x)
            update_manual_grid()

        # Initial grid setup
        update_manual_grid()

        # Execute the dialog
        if play_dialog.exec() == QDialog.DialogCode.Accepted:
            # If dialog was accepted, update the main game state
            self.game = game_copy
            self.update_grid_display()

    def on_solve_with_csp(self, use_llm=False):
        """Solve the grid with CSP solver"""
        if not self.game:
            QMessageBox.warning(
                self, "Erreur", "Veuillez d'abord générer ou charger une grille."
            )
            return

        if use_llm and not OPENAI_AVAILABLE:
            QMessageBox.warning(
                self,
                "Erreur",
                "La bibliothèque OpenAI n'est pas disponible.\n"
                "Installez-la avec 'pip install openai'",
            )
            return

        # Get API key and base URL if using LLM
        api_key = None
        base_url = None
        if use_llm:
            api_key = self.api_key_input.text().strip() or None
            base_url = self.base_url_input.text().strip() or None

            if not api_key and not os.environ.get("OPENAI_API_KEY"):
                QMessageBox.warning(
                    self,
                    "Erreur",
                    "Aucune clé API OpenAI fournie.\n"
                    "Vous pouvez en obtenir une sur https://platform.openai.com/api-keys",
                )
                return

        # Clear console
        self.console_text.clear()

        # Start solver in a separate thread
        self.statusBar().showMessage("Résolution en cours...")
        solver_mode = "CSP + LLM" if use_llm else "CSP"
        self.console_text.append(
            f"Démarrage de la résolution avec {solver_mode} (pas à pas)"
        )

        # Redirect output before starting solver
        self.redirect_output()

        self.solver_thread = SolverThread(
            self.game, use_llm, True, api_key, base_url  # Always use step-by-step mode
        )
        self.solver_thread.update_signal.connect(self.update_solver_progress)
        self.solver_thread.finished_signal.connect(self.solver_finished)
        self.solver_thread.error_signal.connect(self.solver_error)
        self.solver_thread.start()

    def update_solver_progress(self, game):
        """Update progress during solving"""
        self.game = game
        self.update_grid_display()

    def solver_finished(self, game):
        """Handle solver completion"""
        self.game = game
        self.restore_output()
        self.update_grid_display()
        self.statusBar().showMessage("Résolution terminée")
        self.console_text.append("Résolution terminée")

    def solver_error(self, error_msg):
        """Handle solver errors"""
        self.restore_output()
        self.show_error(f"Erreur pendant la résolution: {error_msg}")
        self.statusBar().showMessage("Erreur pendant la résolution")

    def update_grid_display(self):
        """Update the grid display"""
        if not self.game:
            self.status_label.setText("Aucune grille active.")
            return

        # Clear existing grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Update grid
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell_value = self.game.board[y][x]
                btn = QPushButton()
                btn.setFixedSize(30, 30)

                # Set cell text and style based on state
                if (y, x) in self.game.revealed_cells:
                    if self.game.solution[y][x] == Minesweeper.MINE:
                        btn.setText("💣")
                        btn.setStyleSheet("background-color: red;")
                    else:
                        count = self.game.count_adjacent_mines(y, x)
                        if count > 0:
                            btn.setText(str(count))
                            # Use different colors for different numbers
                            colors = [
                                "blue",
                                "green",
                                "red",
                                "purple",
                                "maroon",
                                "turquoise",
                                "black",
                                "gray",
                            ]
                            if count <= len(colors):
                                btn.setStyleSheet(f"color: {colors[count - 1]};")
                        else:
                            btn.setText("")
                        btn.setStyleSheet(
                            btn.styleSheet() + "background-color: lightgray;"
                        )
                elif cell_value == Minesweeper.FLAG:
                    btn.setText("🚩")
                    btn.setStyleSheet("font-size: 16px;")
                else:
                    btn.setText("")

                self.grid_layout.addWidget(btn, y, x)

        # Update statistics
        stats_text = f"Dimensions: {self.game.width}×{self.game.height}\n"
        stats_text += f"Mines: {self.game.num_mines}\n"

        # Count revealed cells
        revealed = len(self.game.revealed_cells)
        total = self.game.width * self.game.height
        stats_text += f"Révélé: {revealed}/{total} cellules"

        self.status_label.setText(stats_text)

    def show_error(self, message):
        """Display an error message"""
        QMessageBox.critical(self, "Erreur", message)
        self.console_text.append(f"ERREUR: {message}")


def main():
    app = QApplication(sys.argv)
    gui = MinesweeperSolverGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
