import React from "react";
import { Move } from "../utils/types";
import "./MoveHistory.css";

interface MoveHistoryProps {
  moves: Move[];
}

const MoveHistory: React.FC<MoveHistoryProps> = ({ moves }) => {
  const formatMove = (move: Move): string => {
    if (move.type === "reveal") {
      return `[USER] Select at x: ${move.x} y: ${move.y}`;
    } else if (move.type === "flag") {
      return `[USER] Flag at x: ${move.x} y: ${move.y}`;
    } else {
      return `[Solver] Select at x: ${move.x} y: ${move.y}`;
    }
  };

  return (
    <div className="move-history">
      <h3 className="move-history-title">Move History</h3>
      <div className="moves-container">
        {moves.length === 0 ? (
          <div className="no-moves">No moves yet</div>
        ) : (
          <ul className="moves-list">
            {moves.map((move, index) => (
              <li key={index} className="move-item">
                {formatMove(move)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default MoveHistory;
