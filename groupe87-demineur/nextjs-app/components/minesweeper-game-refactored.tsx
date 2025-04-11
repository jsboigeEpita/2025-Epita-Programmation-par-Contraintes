"use client"

import type React from "react"

import { useState, useEffect, useCallback } from "react"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { solveMinesweeperCSP } from "@/lib/csp-solver"
import MinesweeperBoard from "./minesweeper-board"
import SolutionDisplay from "./solution-display"
import GameControls from "./game-controls"
import GameStats from "./game-stats"

// Game difficulty presets
const DIFFICULTY_PRESETS = {
  beginner: { rows: 8, cols: 8, mines: 10 },
  easy: { rows: 9, cols: 9, mines: 10 },
  medium: { rows: 16, cols: 16, mines: 40 },
  hard: { rows: 16, cols: 30, mines: 99 },
  expert: { rows: 20, cols: 24, mines: 130 },
  custom: { rows: 5, cols: 5, mines: 5 },
}

export default function MinesweeperGame({ refreshView }: { refreshView: () => void }) {
  // Changer la difficulté par défaut à "medium"
  const [difficulty, setDifficulty] = useState<string>("medium")
  const [gameConfig, setGameConfig] = useState(DIFFICULTY_PRESETS.medium)
  const [customConfig, setCustomConfig] = useState({ rows: 5, cols: 5, mines: 5 })
  const [board, setBoard] = useState<any[][]>([])
  const [gameState, setGameState] = useState<"playing" | "won" | "lost">("playing")
  const [flagsPlaced, setFlagsPlaced] = useState(0)
  const [firstClick, setFirstClick] = useState(true)
  const [solution, setSolution] = useState<any>(null)
  const [showHint, setShowHint] = useState(false)
  const [animatingSolution, setAnimatingSolution] = useState(false)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [resetKey, setResetKey] = useState(0)
  const [stats, setStats] = useState({ gamesWon: 0, gamesPlayed: 0 })

  // Initialize the game board
  useEffect(() => {
    initializeGame()
  }, [gameConfig])

  const initializeGame = useCallback(() => {
    const { rows, cols } = gameConfig
    const newBoard = Array(rows)
      .fill(null)
      .map(() =>
        Array(cols)
          .fill(null)
          .map(() => ({
            isMine: false,
            isRevealed: false,
            isFlagged: false,
            adjacentMines: 0,
          })),
      )

    setBoard(newBoard)
    setGameState("playing")
    setFlagsPlaced(0)
    setFirstClick(true)
    setSolution(null)
    setShowHint(false)
    setAnimatingSolution(false)
    setTimeElapsed(0)
    setResetKey((prev) => prev + 1)
  }, [gameConfig])

  const placeMines = (clickRow: number, clickCol: number) => {
    const { rows, cols, mines } = gameConfig
    const newBoard = [...board]
    let minesPlaced = 0

    // Make sure the first clicked cell and its neighbors are safe
    const safeZone = []
    for (let r = Math.max(0, clickRow - 1); r <= Math.min(rows - 1, clickRow + 1); r++) {
      for (let c = Math.max(0, clickCol - 1); c <= Math.min(cols - 1, clickCol + 1); c++) {
        safeZone.push(`${r},${c}`)
      }
    }

    while (minesPlaced < mines) {
      const randomRow = Math.floor(Math.random() * rows)
      const randomCol = Math.floor(Math.random() * cols)
      const cellKey = `${randomRow},${randomCol}`

      if (!newBoard[randomRow][randomCol].isMine && !safeZone.includes(cellKey)) {
        newBoard[randomRow][randomCol].isMine = true
        minesPlaced++
      }
    }

    // Calculate adjacent mines for each cell
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (!newBoard[r][c].isMine) {
          let count = 0
          for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
              const nr = r + dr
              const nc = c + dc
              if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && newBoard[nr][nc].isMine) {
                count++
              }
            }
          }
          newBoard[r][c].adjacentMines = count
        }
      }
    }

    setBoard(newBoard)
  }

  const handleCellClick = (row: number, col: number) => {
    if (gameState !== "playing" || board[row][col].isRevealed || board[row][col].isFlagged) {
      return
    }

    // Place mines on first click
    if (firstClick) {
      placeMines(row, col)
      setFirstClick(false)
    }

    const newBoard = [...board]

    // If clicked on a mine, game over
    if (newBoard[row][col].isMine) {
      revealAllMines()
      setGameState("lost")
      setStats((prev) => ({
        gamesWon: prev.gamesWon,
        gamesPlayed: prev.gamesPlayed + 1,
      }))
      return
    }

    // Reveal the clicked cell
    revealCell(newBoard, row, col)
    setBoard(newBoard)

    // Check if the player has won
    checkWinCondition()
  }

  const revealCell = (board: any[][], row: number, col: number) => {
    const { rows, cols } = gameConfig

    if (row < 0 || row >= rows || col < 0 || col >= cols || board[row][col].isRevealed || board[row][col].isFlagged) {
      return
    }

    board[row][col].isRevealed = true

    // If the cell has no adjacent mines, reveal its neighbors
    if (board[row][col].adjacentMines === 0) {
      for (let dr = -1; dr <= 1; dr++) {
        for (let dc = -1; dc <= 1; dc++) {
          if (dr !== 0 || dc !== 0) {
            revealCell(board, row + dr, col + dc)
          }
        }
      }
    }
  }

  const handleCellRightClick = (row: number, col: number, e: React.MouseEvent) => {
    e.preventDefault()

    if (gameState !== "playing" || board[row][col].isRevealed) {
      return
    }

    const newBoard = [...board]
    const cell = newBoard[row][col]

    if (cell.isFlagged) {
      cell.isFlagged = false
      setFlagsPlaced(flagsPlaced - 1)
    } else {
      cell.isFlagged = true
      setFlagsPlaced(flagsPlaced + 1)
    }

    setBoard(newBoard)
  }

  const revealAllMines = () => {
    const newBoard = [...board]

    for (let r = 0; r < gameConfig.rows; r++) {
      for (let c = 0; c < gameConfig.cols; c++) {
        if (newBoard[r][c].isMine) {
          newBoard[r][c].isRevealed = true
        }
      }
    }

    setBoard(newBoard)
  }

  const checkWinCondition = () => {
    const { rows, cols, mines } = gameConfig
    let revealedCount = 0

    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        if (board[r][c].isRevealed && !board[r][c].isMine) {
          revealedCount++
        }
      }
    }

    if (revealedCount === rows * cols - mines) {
      setGameState("won")
      setStats((prev) => ({
        gamesWon: prev.gamesWon + 1,
        gamesPlayed: prev.gamesPlayed + 1,
      }))
    }
  }

  // Corriger la fonction handleDifficultyChange
  const handleDifficultyChange = useCallback(
    (value: string) => {
      console.log("Changing difficulty to:", value)

      // Mettre à jour l'état de difficulté
      setDifficulty(value)

      // Appliquer la configuration en fonction de la difficulté sélectionnée
      if (value === "custom") {
        setGameConfig({ ...customConfig })
      } else {
        setGameConfig({ ...DIFFICULTY_PRESETS[value as keyof typeof DIFFICULTY_PRESETS] })
      }

      // Forcer un rafraîchissement complet
      setTimeout(() => {
        initializeGame()
        refreshView()
      }, 0)
    },
    [customConfig, refreshView, initializeGame],
  )

  const updateCustomConfig = useCallback(
    (field: "rows" | "cols" | "mines", value: number) => {
      const newConfig = { ...customConfig }
      newConfig[field] = value

      // Ensure mines don't exceed cells - 1 (to allow first click safety)
      const maxMines = newConfig.rows * newConfig.cols - 1
      if (newConfig.mines > maxMines) {
        newConfig.mines = maxMines
      }

      setCustomConfig(newConfig)

      // Si la difficulté actuelle est "custom", mettre à jour la configuration du jeu
      if (difficulty === "custom") {
        setGameConfig({ ...newConfig })
        setTimeout(() => {
          initializeGame()
          refreshView()
        }, 0)
      }
    },
    [customConfig, difficulty, refreshView, initializeGame],
  )

  const handleSolveCSP = () => {
    // Convert current board state to CSP input format
    const cspBoard = board.map((row) =>
      row.map((cell) => {
        if (cell.isRevealed) {
          return cell.adjacentMines
        }
        return "?"
      }),
    )

    const minePositions = []
    for (let r = 0; r < gameConfig.rows; r++) {
      for (let c = 0; c < gameConfig.cols; c++) {
        if (board[r][c].isMine) {
          minePositions.push([r, c])
        }
      }
    }

    // Solve the CSP
    const result = solveMinesweeperCSP(cspBoard, gameConfig.mines, minePositions)
    setSolution(result)
  }

  const showNextHint = () => {
    if (!solution || gameState !== "playing") return

    setShowHint(true)
    setTimeout(() => setShowHint(false), 3000)
  }

  const animateSolution = () => {
    if (!solution || gameState !== "playing") return

    setAnimatingSolution(true)
    setTimeout(() => setAnimatingSolution(false), 2000)
  }

  const resetGame = useCallback(() => {
    initializeGame()
    refreshView()
  }, [initializeGame, refreshView])

  const handleTimeUpdate = (time: number) => {
    setTimeElapsed(time)
  }

  return (
    <div className="flex flex-col items-center">
      <GameStats
        timeElapsed={timeElapsed}
        flagsPlaced={flagsPlaced}
        totalMines={gameConfig.mines}
        gamesWon={stats.gamesWon}
        gamesPlayed={stats.gamesPlayed}
      />

      <GameControls
        difficulty={difficulty}
        onDifficultyChange={handleDifficultyChange}
        customConfig={customConfig}
        onCustomConfigChange={updateCustomConfig}
        onReset={resetGame}
        onSolve={handleSolveCSP}
        onShowHint={showNextHint}
        onAnimateSolution={animateSolution}
        minesRemaining={gameConfig.mines - flagsPlaced}
        isPlaying={gameState === "playing"}
        isFirstClick={firstClick}
        hasSolution={!!solution}
      />

      {gameState === "won" && (
        <Alert className="mb-4 bg-green-50 border-green-200">
          <AlertDescription className="text-green-700">Congratulations! You've won the game!</AlertDescription>
        </Alert>
      )}

      {gameState === "lost" && (
        <Alert className="mb-4 bg-red-50 border-red-200">
          <AlertDescription className="text-red-700">Game over! You hit a mine.</AlertDescription>
        </Alert>
      )}

      <div className="mb-6">
        <MinesweeperBoard
          board={board}
          onCellClick={handleCellClick}
          onCellRightClick={handleCellRightClick}
          showHint={showHint && solution ? solution.safeRecommendations : []}
          animatingSolution={animatingSolution && solution ? solution.solutions[0] : null}
        />
      </div>

      {solution && (
        <div className="mt-6 w-full">
          <h2 className="text-xl font-bold mb-4">CSP Solution</h2>
          <SolutionDisplay solution={solution} />
        </div>
      )}
    </div>
  )
}
