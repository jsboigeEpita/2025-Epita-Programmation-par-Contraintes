import React from "react";
import "./ExplosionsCounter.css";

interface ExplosionsCounterProps {
  count: number;
}

const ExplosionsCounter: React.FC<ExplosionsCounterProps> = ({ count }) => {
  return (
    <div className="explosions-counter">
      <div className="explosions-icon">💥</div>
      <div className="explosions-count">{count}</div>
    </div>
  );
};

export default ExplosionsCounter;
