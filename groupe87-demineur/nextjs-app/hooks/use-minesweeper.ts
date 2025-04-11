"use client"

import type React from "react"

import { useState, useCallback, useEffect } from "react"
import { DIFFICULTY_PRESETS } from "@/lib/constants"
import { solveMinesweeperCSP } from "@/lib/csp-solver"
import type { Cell } from "@/lib/types"

export function useMinesweeper(refreshView: () => void) {
  const [difficulty, setDifficulty] = useState<string>("medium")
  const [gameConfig, setGameConfig] = useState(DIFFICULTY_PRESETS.medium)
  const [customConfig, setCustomConfig] = useState({ rows: 5, cols: 5, mines: 5 })
  const [board, setBoard] = useState<Cell[][]>([])
  const [gameState, setGameState] = useState<"playing" | "won" | "lost">("playing")
  const [flagsPlaced, setFlagsPlaced] = useState(0)
  const [firstClick, setFirstClick] = useState(true)
  const [solution, setSolution] = useState<any>(null)
  const [showHint, setShowHint] = useState(false)
  const [animatingSolution, setAnimatingSolution] = useState(false)
  const [timeElapsed, setTimeElapsed] = useState(0)
  const [resetKey, setResetKey] = useState(0)
  const [stats, setStats] = useState({ gamesWon: 0, gamesPlayed: 0 })
  const [timerRunning, setTimerRunning] = useState(false)

  useEffect(() => {
    initializeGame()
  }, [])

  useEffect(() => {
    if (gameState === "playing" && !firstClick) {
      setTimerRunning(true)
    } else {
      setTimerRunning(false)
    }
  }, [gameState, firstClick])

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
    setTimerRunning(false)
  }, [gameConfig])

  const placeMines = (clickRow: number, clickCol: number) => {
    const { rows, cols, mines } = gameConfig
    const newBoard = [...board]
    let minesPlaced = 0

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

  const revealCell = (board: Cell[][], row: number, col: number) => {
    const { rows, cols } = gameConfig

    if (row < 0 || row >= rows || col < 0 || col >= cols || board[row][col].isRevealed || board[row][col].isFlagged) {
      return
    }

    board[row][col].isRevealed = true

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

  const handleCellClick = (row: number, col: number) => {
    if (gameState !== "playing" || board[row][col].isRevealed || board[row][col].isFlagged) {
      return
    }

    if (firstClick) {
      placeMines(row, col)
      setFirstClick(false)
    }

    const newBoard = [...board]

    if (newBoard[row][col].isMine) {
      revealAllMines()
      setGameState("lost")
      setStats((prev) => ({
        gamesWon: prev.gamesWon,
        gamesPlayed: prev.gamesPlayed + 1,
      }))
      return
    }

    revealCell(newBoard, row, col)
    setBoard(newBoard)

    checkWinCondition()
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

  const handleDifficultyChange = useCallback(
    (value: string) => {
      setDifficulty(value)

      if (value === "custom") {
        setGameConfig({ ...customConfig })
      } else {
        setGameConfig({ ...DIFFICULTY_PRESETS[value as keyof typeof DIFFICULTY_PRESETS] })
      }

      setTimeout(() => {
        initializeGame()
        refreshView()
      }, 50)
    },
    [customConfig, refreshView, initializeGame],
  )

  const updateCustomConfig = useCallback(
    (field: "rows" | "cols" | "mines", value: number) => {
      const newConfig = { ...customConfig }
      newConfig[field] = value

      const maxMines = newConfig.rows * newConfig.cols - 1
      if (newConfig.mines > maxMines) {
        newConfig.mines = maxMines
      }

      setCustomConfig(newConfig)

      if (difficulty === "custom") {
        setGameConfig({ ...newConfig })
        setTimeout(() => {
          initializeGame()
          refreshView()
        }, 50)
      }
    },
    [customConfig, difficulty, initializeGame, refreshView],
  )

  const handleSolveCSP = () => {
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

    const result = solveMinesweeperCSP(cspBoard, gameConfig.mines, minePositions)
    setSolution(result)
  }

  const handleNextMove = () => {
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

    const result = solveMinesweeperCSP(cspBoard, gameConfig.mines, minePositions, 1)

    if (result.safeRecommendations && result.safeRecommendations.length > 0) {
      setShowHint(true)
      setTimeout(() => setShowHint(false), 3000)
    }

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

  return {
    difficulty,
    gameConfig,
    customConfig,
    board,
    gameState,
    flagsPlaced,
    firstClick,
    solution,
    showHint,
    animatingSolution,
    timeElapsed,
    resetKey,
    stats,
    timerRunning,
    handleCellClick,
    handleCellRightClick,
    handleDifficultyChange,
    updateCustomConfig,
    handleSolveCSP,
    handleNextMove,
    showNextHint,
    animateSolution,
    resetGame,
    handleTimeUpdate,
  }
}
