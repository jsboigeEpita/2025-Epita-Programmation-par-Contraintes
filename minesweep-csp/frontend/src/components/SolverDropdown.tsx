import React, { useState, useEffect, useRef } from "react";
import { Solver } from "../utils/types";
import "./SolverDropdown.css";

interface SolverDropdownProps {
  solvers: Solver[];
  currentSolver: string;
  onSelect: (solverId: string) => void;
}

const SolverDropdown: React.FC<SolverDropdownProps> = ({
  solvers,
  currentSolver,
  onSelect,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get current solver details
  const currentSolverDetails =
    solvers.find((s) => s.id === currentSolver) || solvers[0];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Handle solver selection
  const handleSelect = (solver: Solver) => {
    onSelect(solver.id);
    setIsOpen(false);
  };

  return (
    <div className="solver-dropdown-container" ref={dropdownRef}>
      <button
        className="solver-dropdown-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="solver-icon">🧩</span>
        <span className="solver-name">{currentSolverDetails.name}</span>
        <span className="solver-arrow">{isOpen ? "▲" : "▼"}</span>
      </button>

      {isOpen && (
        <div className="solver-dropdown-menu">
          {solvers.map((solver) => (
            <div
              key={solver.id}
              className={`solver-dropdown-item ${
                solver.id === currentSolver ? "active" : ""
              }`}
              onClick={() => handleSelect(solver)}
            >
              <div className="solver-item-icon">
                {solver.id === currentSolver ? "✓" : " "}
              </div>
              <div className="solver-item-content">
                <div className="solver-item-title">{solver.name}</div>
                <div className="solver-item-description">
                  {solver.description}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SolverDropdown;
