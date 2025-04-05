import { useState, useEffect, useRef } from "react";
import GameBoard from "./components/GameBoard";
import GameControls from "./components/GameControls";
import SolverDropdown from "./components/SolverDropdown";
import MoveHistory from "./components/MoveHistory";
import "./App.css";
import { GameState, Solver, Move } from "./utils/types";
import { MinesweeperAPI } from "./utils/backend";

const DEFAULT_COLS = 10;
const DEFAULT_ROWS = 10;
const DEFAULT_MINES = 10;
const DEFAULT_SOLVER = "basic";

// Define default solvers until we fetch from API
const DEFAULT_SOLVERS: Solver[] = [
  {
    id: "basic",
    name: "Basic Solver",
    description: "A simple solver using basic strategies",
  },
  {
    id: "csp",
    name: "CSP Solver",
    description: "Constraint satisfaction programming solver",
  },
  {
    id: "astar",
    name: "A* Solver",
    description: "An A* based solver (coming soon)",
  },
  {
    id: "astar_boost",
    name: "A* Boost",
    description: "An enhanced A* solver with heuristics (coming soon)",
  },
];

function App() {
  const [gameId, setGameId] = useState<string | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  const [solverType, setSolverType] = useState<string>(DEFAULT_SOLVER);
  const [solvers, setSolvers] = useState<Solver[]>(DEFAULT_SOLVERS);
  const [moveHistory, setMoveHistory] = useState<Move[]>([]);
  const timerRef = useRef<number | null>(null);

  // Load available solvers
  useEffect(() => {
    const fetchSolvers = async () => {
      try {
        const { solvers: availableSolvers } =
          await MinesweeperAPI.getAvailableSolvers();
        setSolvers(availableSolvers);
      } catch (error) {
        console.error("Error fetching solvers:", error);
        // Fall back to default solvers
      }
    };

    fetchSolvers();
  }, []);

  // Stop the timer when game is over or reset
  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  // Start the timer
  const startTimer = () => {
    // Stop any existing timer first
    stopTimer();

    // Start a new interval timer
    timerRef.current = setInterval(() => {
      setElapsedTime((prevTime) => prevTime + 1);
    }, 1000);
  };

  const startNewGame = async (cols: number, rows: number, mines: number) => {
    try {
      console.log("Starting new game...");
      const { game_id, state } = await MinesweeperAPI.startNewGame(
        cols,
        rows,
        mines,
        solverType
      );

      console.log("Game started:", { game_id, state });
      setGameId(game_id);
      setGameState(state);
      setError(null);
      setSolverType(state.solver_type);
      setMoveHistory([]); // Clear move history for new game

      // Reset elapsed time and start timer
      setElapsedTime(0);
      startTimer();
    } catch (error) {
      console.error("Error starting new game:", error);
      setError("Failed to start new game. Is the backend running?");
      stopTimer();
    }
  };

  const handleCellClick = async (x: number, y: number) => {
    if (!gameId || !gameState) return;

    try {
      const { state } = await MinesweeperAPI.revealCell(gameId, x, y);
      setGameState(state);

      // Record the move
      const newMove: Move = {
        type: "reveal",
        x,
        y,
        timestamp: Date.now(),
      };
      setMoveHistory((prevHistory) => [newMove, ...prevHistory]);

      // Stop timer if game is over
      if (state.game_over) {
        stopTimer();
      }
    } catch (error) {
      console.error("Error revealing cell:", error);
    }
  };

  const handleCellRightClick = async (x: number, y: number) => {
    if (!gameId || !gameState) return;

    try {
      const { state } = await MinesweeperAPI.toggleFlag(gameId, x, y);
      setGameState(state);

      // Check if this action actually toggled a flag by comparing the previous and new state
      const wasAlreadyFlagged = !state.flagged[y][x];

      // Only record if it's a new flag (not removing an existing one)
      if (!wasAlreadyFlagged) {
        const newMove: Move = {
          type: "flag",
          x,
          y,
          timestamp: Date.now(),
        };
        setMoveHistory((prevHistory) => [newMove, ...prevHistory]);
      }
    } catch (error) {
      console.error("Error toggling flag:", error);
    }
  };

  const handleSolveMove = async () => {
    if (!gameId || !gameState) return;

    try {
      // Get next move
      const moveData = await MinesweeperAPI.getSolveNextMove(gameId);

      if (moveData.error) {
        console.error("No moves available");
        return;
      }

      // Get the coordinates of the move before applying it
      const x = moveData.x !== undefined ? moveData.x : -1;
      const y = moveData.y !== undefined ? moveData.y : -1;

      // Apply the move
      const { state } = await MinesweeperAPI.applySolveMove(gameId);
      setGameState(state);

      // Only record if we have valid coordinates
      if (x >= 0 && y >= 0) {
        const newMove: Move = {
          type: "solver",
          x,
          y,
          timestamp: Date.now(),
        };
        setMoveHistory((prevHistory) => [newMove, ...prevHistory]);
      }

      // Stop timer if game is over
      if (state.game_over) {
        stopTimer();
      }
    } catch (error) {
      console.error("Error solving move:", error);
    }
  };

  const handleChangeSolver = async (newSolverType: string) => {
    if (!gameId || !gameState) return;

    try {
      console.log("Changing solver to:", newSolverType);
      const { state } = await MinesweeperAPI.changeSolver(
        gameId,
        newSolverType
      );
      setGameState(state);
      setSolverType(newSolverType);
    } catch (error) {
      console.error("Error changing solver:", error);
    }
  };

  // Clean up timer on component unmount
  useEffect(() => {
    console.log("App mounted, starting new game...");
    startNewGame(DEFAULT_COLS, DEFAULT_ROWS, DEFAULT_MINES);

    return () => {
      stopTimer();
    };
  }, []);

  return (
    <div className="minesweeper-app-container">
      <header className="global-header">
        <div className="header-content">
          <div className="header-left">
            <SolverDropdown
              solvers={solvers}
              currentSolver={solverType}
              onSelect={handleChangeSolver}
            />
          </div>
          <h1 className="header-title">Minesweeper</h1>
          <div className="header-right">{/* Empty for symmetry */}</div>
        </div>
      </header>

      <main className="app-container">
        {error ? (
          <div className="error">{error}</div>
        ) : (
          <>
            <GameControls
              onNewGame={startNewGame}
              onSolveMove={handleSolveMove}
              mineCount={gameState?.num_mines || 0}
              gameStatus={
                gameState?.game_over
                  ? gameState.won
                    ? "Won!"
                    : "Game Over"
                  : "Playing"
              }
              elapsedTime={elapsedTime}
            />

            <div className="game-with-history">
              {gameState ? (
                <GameBoard
                  grid={gameState.grid}
                  revealed={gameState.revealed}
                  flagged={gameState.flagged}
                  onCellClick={handleCellClick}
                  onCellRightClick={handleCellRightClick}
                  disabled={gameState?.game_over}
                />
              ) : (
                <div className="loading">Loading game...</div>
              )}

              <MoveHistory moves={moveHistory} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
