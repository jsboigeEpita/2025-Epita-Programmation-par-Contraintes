import React from "react";
import "./GameBoard.css";

interface GameBoardProps {
  grid: number[][];
  revealed: boolean[][];
  flagged: boolean[][];
  onCellClick: (x: number, y: number) => void;
  onCellRightClick: (x: number, y: number) => void;
  disabled: boolean;
}

const GameBoard: React.FC<GameBoardProps> = ({
  grid,
  revealed,
  flagged,
  onCellClick,
  onCellRightClick,
  disabled,
}) => {
  const handleContextMenu = (e: React.MouseEvent, x: number, y: number) => {
    if (disabled) return;
    e.preventDefault();
    onCellRightClick(x, y);
  };

  const getCellContent = (
    value: number,
    isRevealed: boolean,
    isFlagged: boolean
  ) => {
    if (isFlagged) return "🚩";
    if (!isRevealed) return "";
    if (value === -1) return "💣";
    if (value === 0) return "";
    return value.toString();
  };

  const getCellColor = (value: number) => {
    const colors = [
      "",
      "blue",
      "green",
      "red",
      "purple",
      "maroon",
      "turquoise",
      "black",
      "gray",
    ];
    return colors[value] || "";
  };

  return (
    <div className="game-board">
      {grid.map((row, y) => (
        <div key={y} className="row">
          {row.map((cell, x) => (
            <div
              key={`${x}-${y}`}
              className={`cell ${
                revealed[y][x] ? "revealed" : ""
              } ${getCellColor(cell)}`}
              onClick={() => {
                if (!disabled) onCellClick(x, y);
              }}
              onContextMenu={(e) => handleContextMenu(e, x, y)}
            >
              {getCellContent(cell, revealed[y][x], flagged[y][x])}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
};

export default GameBoard;
