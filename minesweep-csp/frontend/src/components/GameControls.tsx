import React, { useEffect, useState } from "react";
import "./GameControls.css";

// Helper function to format time
const formatTime = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes.toString().padStart(2, "0")}:${remainingSeconds
    .toString()
    .padStart(2, "0")}`;
};

// Define difficulty presets
const DIFFICULTY_PRESETS = {
  beginner: { cols: 9, rows: 9, mines: 10 },
  intermediate: { cols: 16, rows: 16, mines: 40 },
  expert: { cols: 30, rows: 16, mines: 99 },
};

// Maximum board dimensions
const MAX_COLS = 40;
const MAX_ROWS = 30;

interface GameControlsProps {
  onNewGame: (cols: number, rows: number, mines: number) => void;
  onSolveMove: () => void;
  mineCount: number;
  gameStatus: string;
  remainingFlags?: number;
  elapsedTime?: number;
}

const GameControls: React.FC<GameControlsProps> = ({
  onNewGame,
  onSolveMove,
  mineCount,
  gameStatus,
  remainingFlags = mineCount,
  elapsedTime = 0,
}) => {
  const [cols, setCols] = useState(9);
  const [rows, setRows] = useState(9);
  const [mines, setMines] = useState(10);
  const [difficulty, setDifficulty] = useState("beginner");
  const [isCustom, setIsCustom] = useState(false);
  const [error, setError] = useState("");

  // Validate inputs and set error message if needed
  const validateInputs = () => {
    if (cols <= 0 || rows <= 0) {
      setError("Columns and rows must be positive numbers");
      return false;
    }

    if (cols > MAX_COLS) {
      setCols(MAX_COLS);
      setError(`Columns limited to ${MAX_COLS}`);
      return false;
    }

    if (rows > MAX_ROWS) {
      setRows(MAX_ROWS);
      setError(`Rows limited to ${MAX_ROWS}`);
      return false;
    }

    const maxMines = cols * rows - 1;
    if (mines <= 0) {
      setError("Must have at least 1 mine");
      return false;
    }

    if (mines > maxMines) {
      setMines(maxMines);
      setError(`Maximum mines for this board size is ${maxMines}`);
      return false;
    }

    setError("");
    return true;
  };

  // Handle difficulty change
  useEffect(() => {
    if (!isCustom && difficulty !== "custom") {
      const preset =
        DIFFICULTY_PRESETS[difficulty as keyof typeof DIFFICULTY_PRESETS];
      setCols(preset.cols);
      setRows(preset.rows);
      setMines(preset.mines);
    }
  }, [difficulty, isCustom]);

  // Ensure mines don't exceed maximum possible
  useEffect(() => {
    const maxMines = cols * rows - 1;
    if (mines > maxMines) {
      setMines(maxMines);
    }
    validateInputs();
  }, [cols, rows, mines]);

  // Handle custom input changes
  const handleInputChange = (
    setter: React.Dispatch<React.SetStateAction<number>>,
    value: number,
    isForMines = false
  ) => {
    setter(value);
    setIsCustom(true);
    setDifficulty("custom");
  };

  // Start new game
  const handleNewGame = () => {
    if (validateInputs()) {
      onNewGame(cols, rows, mines);
    }
  };

  // Get status icon based on game state
  const getStatusIcon = () => {
    switch (gameStatus.toLowerCase()) {
      case "won!":
      case "won":
        return "🎉";
      case "game over":
      case "lost":
        return "💥";
      case "playing":
        return "🎮";
      default:
        return "🎲";
    }
  };

  const isGameOver = gameStatus === "Won!" || gameStatus === "Game Over";

  return (
    <div className="game-controls">
      <div className="game-header">
        <div className="game-header-item">
          <span className="icon">💣</span>
          <span className="value">{remainingFlags}</span>
        </div>
        <div className="game-status">
          <span className="status-icon">{getStatusIcon()}</span>
          <span className="status-text">{gameStatus}</span>
        </div>
        <div className="game-header-item">
          <span className="icon">⏱️</span>
          <span className="value">{formatTime(elapsedTime)}</span>
        </div>
      </div>

      <div className="difficulty-selector">
        <label>Difficulty:</label>
        <div className="difficulty-buttons">
          <button
            className={
              difficulty === "beginner" && !isCustom ? "active" : "not-active"
            }
            onClick={() => {
              setIsCustom(false);
              setDifficulty("beginner");
            }}
          >
            Beginner
          </button>
          <button
            className={
              difficulty === "intermediate" && !isCustom
                ? "active"
                : "not-active"
            }
            onClick={() => {
              setIsCustom(false);
              setDifficulty("intermediate");
            }}
          >
            Intermediate
          </button>
          <button
            className={
              difficulty === "expert" && !isCustom ? "active" : "not-active"
            }
            onClick={() => {
              setIsCustom(false);
              setDifficulty("expert");
            }}
          >
            Expert
          </button>
          <button
            className={isCustom ? "active" : "not-active"}
            onClick={() => setIsCustom(!isCustom)}
          >
            Custom
          </button>
        </div>
      </div>

      {isCustom && (
        <div className="game-settings">
          <div className="input-group">
            <label htmlFor="cols-input">Columns:</label>
            <input
              id="cols-input"
              type="number"
              value={cols}
              onChange={(e) =>
                handleInputChange(
                  setCols,
                  Math.min(MAX_COLS, Math.max(1, Number(e.target.value)))
                )
              }
              min="1"
              max={MAX_COLS}
            />
          </div>
          <div className="input-group">
            <label htmlFor="rows-input">Rows:</label>
            <input
              id="rows-input"
              type="number"
              value={rows}
              onChange={(e) =>
                handleInputChange(
                  setRows,
                  Math.min(MAX_ROWS, Math.max(1, Number(e.target.value)))
                )
              }
              min="1"
              max={MAX_ROWS}
            />
          </div>
          <div className="input-group">
            <label htmlFor="mines-input">Mines:</label>
            <input
              id="mines-input"
              type="number"
              value={mines}
              onChange={(e) =>
                handleInputChange(
                  setMines,
                  Math.max(1, Number(e.target.value)),
                  true
                )
              }
              min="1"
              max={cols * rows - 1}
            />
            <span className="input-hint">Max: {cols * rows - 1}</span>
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      <div className="game-buttons">
        <button className="primary-button" onClick={handleNewGame}>
          New Game
        </button>
        <button
          className="secondary-button"
          onClick={onSolveMove}
          disabled={isGameOver}
        >
          Hint
        </button>
      </div>
    </div>
  );
};

export default GameControls;
