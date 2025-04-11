"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Bomb, RefreshCw } from "lucide-react"
import { solveMinesweeperCSP } from "@/lib/csp-solver"
import MinesweeperBoard from "./minesweeper-board"
import SolutionDisplay from "./solution-display"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

// Mettre à jour les presets de difficulté pour inclure plus d'options
const DIFFICULTY_PRESETS = {
  beginner: { rows: 8, cols: 8, mines: 10 },
  easy: { rows: 9, cols: 9, mines: 10 },
  medium: { rows: 16, cols: 16, mines: 40 },
  hard: { rows: 16, cols: 30, mines: 99 },
  expert: { rows: 20, cols: 24, mines: 130 },
  custom: { rows: 5, cols: 5, mines: 5 },
}

export default function MinesweeperGame({ refreshView }: { refreshView: () => void }) {
  const [difficulty, setDifficulty] = useState<string>("easy")
  const [gameConfig, setGameConfig] = useState(DIFFICULTY_PRESETS.easy)
  const [board, setBoard] = useState<any[][]>([])
  const [gameState, setGameState] = useState<"playing" | "won" | "lost">("playing")
  const [flagsPlaced, setFlagsPlaced] = useState(0)
  const [firstClick, setFirstClick] = useState(true)
  const [solution, setSolution] = useState<any>(null)

  // Ajouter un état pour les dimensions personnalisées
  const [customConfig, setCustomConfig] = useState({ rows: 5, cols: 5, mines: 5 })
  const [showHint, setShowHint] = useState(false)
  const [animatingSolution, setAnimatingSolution] = useState(false)

  // Initialize the game board
  useEffect(() => {
    initializeGame()
  }, [gameConfig])

  const initializeGame = () => {
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
  }

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
    }
  }

  // Mettre à jour la fonction handleDifficultyChange pour gérer les dimensions personnalisées
  const handleDifficultyChange = (value: string) => {
    setDifficulty(value)
    if (value === "custom") {
      setGameConfig(customConfig)
    } else {
      setGameConfig(DIFFICULTY_PRESETS[value as keyof typeof DIFFICULTY_PRESETS])
    }
    refreshView()
  }

  // Ajouter une fonction pour mettre à jour les dimensions personnalisées
  const updateCustomConfig = (field: "rows" | "cols" | "mines", value: number) => {
    const newConfig = { ...customConfig, [field]: value }

    // Ensure mines don't exceed cells - 1 (to allow first click safety)
    const maxMines = newConfig.rows * newConfig.cols - 1
    if (newConfig.mines > maxMines) {
      newConfig.mines = maxMines
    }

    setCustomConfig(newConfig)
    if (difficulty === "custom") {
      setGameConfig(newConfig)
      refreshView()
    }
  }

  // Ajouter une fonction pour afficher un indice
  const showNextHint = () => {
    if (!solution || gameState !== "playing") return

    setShowHint(true)
    setTimeout(() => setShowHint(false), 3000)
  }

  // Ajouter une fonction pour animer la solution
  const animateSolution = () => {
    if (!solution || gameState !== "playing") return

    setAnimatingSolution(true)
    setTimeout(() => setAnimatingSolution(false), 2000)
  }

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

  const resetGame = () => {
    initializeGame()
    refreshView()
  }

  // Mettre à jour le rendu pour inclure les nouveaux contrôles et fonctionnalités
  return (
    <div className="flex flex-col items-center">
      <div className="flex justify-between w-full mb-6">
        <div className="flex items-center gap-4">
          <Select value={difficulty} onValueChange={handleDifficultyChange}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select difficulty" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="beginner">Beginner</SelectItem>
              <SelectItem value="easy">Easy</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="hard">Hard</SelectItem>
              <SelectItem value="expert">Expert</SelectItem>
              <SelectItem value="custom">Custom</SelectItem>
            </SelectContent>
          </Select>

          <div className="flex items-center gap-2">
            <Bomb className="h-5 w-5 text-red-500" />
            <span>{gameConfig.mines - flagsPlaced}</span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={resetGame}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSolveCSP} disabled={gameState !== "playing" || firstClick}>
            Solve with CSP
          </Button>
        </div>
      </div>

      {difficulty === "custom" && (
        <div className="grid grid-cols-3 gap-4 mb-6 w-full">
          <div>
            <Label htmlFor="custom-rows">Rows</Label>
            <Input
              id="custom-rows"
              type="number"
              min="2"
              max="20"
              value={customConfig.rows}
              onChange={(e) => updateCustomConfig("rows", Number.parseInt(e.target.value))}
            />
          </div>
          <div>
            <Label htmlFor="custom-cols">Columns</Label>
            <Input
              id="custom-cols"
              type="number"
              min="2"
              max="30"
              value={customConfig.cols}
              onChange={(e) => updateCustomConfig("cols", Number.parseInt(e.target.value))}
            />
          </div>
          <div>
            <Label htmlFor="custom-mines">Mines</Label>
            <Input
              id="custom-mines"
              type="number"
              min="1"
              max={customConfig.rows * customConfig.cols - 1}
              value={customConfig.mines}
              onChange={(e) => updateCustomConfig("mines", Number.parseInt(e.target.value))}
            />
          </div>
        </div>
      )}

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
          <div className="flex gap-4 mb-4">
            <Button onClick={showNextHint} variant="outline">
              Show Hint
            </Button>
            <Button onClick={animateSolution} variant="outline">
              Animate Solution
            </Button>
          </div>
          <SolutionDisplay solution={solution} />
        </div>
      )}
    </div>
  )
}
