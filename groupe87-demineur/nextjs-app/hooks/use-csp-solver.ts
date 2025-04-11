"use client"

import type React from "react"
import { useState, useEffect, useCallback } from "react"
import { solveMinesweeperCSP } from "@/lib/csp-solver"

// Configuration des niveaux de difficulté prédéfinis
const DIFFICULTY_PRESETS = {
  beginner: { rows: 8, cols: 8, mines: 10 },
  easy: { rows: 9, cols: 9, mines: 10 },
  medium: { rows: 16, cols: 16, mines: 40 },
  hard: { rows: 16, cols: 30, mines: 99 },
  expert: { rows: 24, cols: 30, mines: 150 },
  custom: { rows: 8, cols: 8, mines: 10 }, // Valeurs par défaut pour "custom"
}

export function useCSPSolver(refreshView: () => void, initialDifficulty: string = "medium") {
  const [rows, setRows] = useState(() => {
    const preset = DIFFICULTY_PRESETS[initialDifficulty as keyof typeof DIFFICULTY_PRESETS] 
    return preset.rows
  })
  const [cols, setCols] = useState(() => {
    const preset = DIFFICULTY_PRESETS[initialDifficulty as keyof typeof DIFFICULTY_PRESETS] 
    return preset.cols
  })
  const [mines, setMines] = useState(() => {
    const preset = DIFFICULTY_PRESETS[initialDifficulty as keyof typeof DIFFICULTY_PRESETS]
    return preset.mines
  })
  const [board, setBoard] = useState<(number | string)[][]>([])
  const [solutions, setSolutions] = useState<any>(null)
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null)
  const [maxSolutions, setMaxSolutions] = useState(10)
  const [animatingSolutions, setAnimatingSolutions] = useState(false)
  const [difficulty, setDifficulty] = useState<string>(initialDifficulty)

  useEffect(() => {
    const preset = DIFFICULTY_PRESETS[difficulty as keyof typeof DIFFICULTY_PRESETS]
    setRows(preset.rows)
    setCols(preset.cols)
    setMines(preset.mines)
    initializeBoard(preset.rows, preset.cols)
  }, [difficulty])

  const initializeBoard = (initRows = rows, initCols = cols) => {
    setBoard(
      Array(initRows)
        .fill(null)
        .map(() => Array(initCols).fill("?")),
    )
    setSolutions(null)
    setSelectedCell(null)
  }

  const handleCellClick = (row: number, col: number) => {
    if (row >= rows || col >= cols) return
    setSelectedCell([row, col])
  }

  const handleCellValueChange = (value: string) => {
    if (!selectedCell) return

    const [row, col] = selectedCell
    const newBoard = [...board]

    if (value === "?") {
      newBoard[row][col] = "?"
    } else {
      const numValue = Number.parseInt(value)
      if (!isNaN(numValue) && numValue >= 0 && numValue <= 8) {
        newBoard[row][col] = numValue
      }
    }

    setBoard(newBoard)
  }

  const animateSolutions = () => {
    setAnimatingSolutions(true)
    setTimeout(() => setAnimatingSolutions(false), 3000)
  }

  const handleSolve = () => {
    const result = solveMinesweeperCSP(board, mines, [], maxSolutions)
    setSolutions(result)
  }

  const handleReset = useCallback(() => {
    if (difficulty !== "custom") {
      const preset = DIFFICULTY_PRESETS[difficulty as keyof typeof DIFFICULTY_PRESETS]
      setRows(preset.rows)
      setCols(preset.cols)
      setMines(preset.mines)
      initializeBoard(preset.rows, preset.cols)
    } else {
      initializeBoard(rows, cols)
    }
    setSolutions(null)
  }, [difficulty])

  const handleSizeChange = useCallback(() => {
    const validRows = Math.max(2, Math.min(150, rows))
    const validCols = Math.max(2, Math.min(150, cols))
    const validMines = Math.max(1, Math.min(validRows * validCols - 1, mines))

    setRows(validRows)
    setCols(validCols)
    setMines(validMines)

    setBoard(
      Array(validRows)
        .fill(null)
        .map(() => Array(validCols).fill("?")),
    )

    setSolutions(null)
    setSelectedCell(null)

    setDifficulty("custom")

    refreshView()
  }, [rows, cols, mines, refreshView])

  const handleRowsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 2
    setRows(Math.max(2, Math.min(150, value)))
  }

  const handleColsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 2
    setCols(Math.max(2, Math.min(150, value)))
  }

  const handleMinesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 1
    const maxMines = rows * cols - 1
    setMines(Math.max(1, Math.min(maxMines, value)))
  }

  const handleMaxSolutionsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 1
    setMaxSolutions(Math.max(1, Math.min(100, value)))
  }

  const handleDifficultyChange = useCallback(
    (value: string) => {
      setDifficulty(value)

      if (value !== "custom") {
        const preset = DIFFICULTY_PRESETS[value as keyof typeof DIFFICULTY_PRESETS]
        setRows(preset.rows)
        setCols(preset.cols)
        setMines(preset.mines)

        initializeBoard(preset.rows, preset.cols)
      }
    },
    [],
  )

  return {
    rows,
    cols,
    mines,
    board,
    solutions,
    selectedCell,
    maxSolutions,
    animatingSolutions,
    difficulty,
    handleCellClick,
    handleCellValueChange,
    animateSolutions,
    handleSolve,
    handleReset,
    handleSizeChange,
    handleRowsChange,
    handleColsChange,
    handleMinesChange,
    handleMaxSolutionsChange,
    handleDifficultyChange,
  }
}
