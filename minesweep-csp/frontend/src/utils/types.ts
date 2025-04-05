export interface GameState {
  grid: number[][];
  revealed: boolean[][];
  flagged: boolean[][];
  game_over: boolean;
  won: boolean;
  width: number;
  height: number;
  num_mines: number;
  solver_type: string;
  start_time?: number; // Optional start time
}

export interface Solver {
  id: string;
  name: string;
  description: string;
}

export interface Move {
  type: "reveal" | "flag" | "solver";
  x: number;
  y: number;
  timestamp: number;
}
