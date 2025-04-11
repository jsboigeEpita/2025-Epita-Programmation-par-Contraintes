"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { solveMinesweeperCSP } from "@/lib/csp-solver"

export function useCSPSolver(refreshView: () => void) {
  const [rows, setRows] = useState(5)
  const [cols, setCols] = useState(5)
  const [mines, setMines] = useState(5)
  const [board, setBoard] = useState<(number | string)[][]>([])
  const [solutions, setSolutions] = useState<any>(null)
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null)
  const [maxSolutions, setMaxSolutions] = useState(10)
  const [animatingSolutions, setAnimatingSolutions] = useState(false)

  useEffect(() => {
    initializeBoard()
  }, [])

  const initializeBoard = () => {
    setBoard(
      Array(rows)
        .fill(null)
        .map(() => Array(cols).fill("?")),
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

  const handleReset = () => {
    initializeBoard()
    refreshView()
  }

  const handleSizeChange = () => {
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

    refreshView()
  }

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

  return {
    rows,
    cols,
    mines,
    board,
    solutions,
    selectedCell,
    maxSolutions,
    animatingSolutions,
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
  }
}
