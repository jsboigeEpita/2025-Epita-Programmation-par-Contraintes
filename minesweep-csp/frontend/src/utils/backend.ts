import { GameState, Solver } from "./types";

// Use relative path for API calls
const API_URL = "/api";

export interface GameStartResponse {
  game_id: string;
  state: GameState;
}

export interface SolveNextMoveResponse {
  x?: number;
  y?: number;
  error?: string;
}

export const MinesweeperAPI = {
  async startNewGame(
    cols: number,
    rows: number,
    mines: number,
    solverType: string = "basic"
  ): Promise<GameStartResponse> {
    try {
      const response = await fetch(`${API_URL}/game/new`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          width: cols,
          height: rows,
          num_mines: mines,
          solver_type: solverType,
        }),
      });

      if (!response.ok) {
        console.error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error starting new game:", error);
      throw error;
    }
  },

  async revealCell(
    gameId: string,
    x: number,
    y: number
  ): Promise<{ state: GameState }> {
    try {
      const response = await fetch(`${API_URL}/game/${gameId}/reveal`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ x, y }),
      });

      if (!response.ok) {
        console.error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error revealing cell:", error);
      throw error;
    }
  },

  async toggleFlag(
    gameId: string,
    x: number,
    y: number
  ): Promise<{ state: GameState }> {
    try {
      const response = await fetch(`${API_URL}/game/${gameId}/flag`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ x, y }),
      });

      if (!response.ok) {
        console.error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error toggling flag:", error);
      throw error;
    }
  },

  async getSolveNextMove(gameId: string): Promise<SolveNextMoveResponse> {
    try {
      const moveResponse = await fetch(`${API_URL}/game/${gameId}/solve/next`, {
        headers: {
          Accept: "application/json",
        },
        credentials: "include",
      });

      if (!moveResponse.ok) {
        if (moveResponse.status === 400) {
          return { error: "No moves available" };
        }
        console.error(
          `HTTP error! status: ${moveResponse.status} ${moveResponse.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${moveResponse.status} ${moveResponse.statusText}`
        );
      }

      return await moveResponse.json();
    } catch (error) {
      console.error("Error getting solve move:", error);
      throw error;
    }
  },

  async applySolveMove(gameId: string): Promise<{ state: GameState }> {
    try {
      const applyResponse = await fetch(
        `${API_URL}/game/${gameId}/solve/apply`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (!applyResponse.ok) {
        console.error(
          `HTTP error! status: ${applyResponse.status} ${applyResponse.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${applyResponse.status} ${applyResponse.statusText}`
        );
      }

      return await applyResponse.json();
    } catch (error) {
      console.error("Error solving move:", error);
      throw error;
    }
  },

  async getAvailableSolvers(): Promise<{ solvers: Solver[] }> {
    try {
      const response = await fetch(`${API_URL}/solvers`, {
        headers: {
          Accept: "application/json",
        },
      });

      if (!response.ok) {
        console.error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error fetching solvers:", error);
      throw error;
    }
  },

  async changeSolver(
    gameId: string,
    solverType: string
  ): Promise<{ state: GameState }> {
    try {
      const response = await fetch(`${API_URL}/game/${gameId}/solver`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ solver_type: solverType }),
      });

      if (!response.ok) {
        console.error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
        throw new Error(
          `HTTP error! status: ${response.status} ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error("Error changing solver:", error);
      throw error;
    }
  },
};
