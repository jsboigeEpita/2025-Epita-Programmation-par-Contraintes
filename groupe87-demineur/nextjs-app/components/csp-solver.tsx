"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { solveMinesweeperCSP } from "@/lib/csp-solver"
import SolutionDisplay from "./solution-display"

export default function CSPSolver({ refreshView }: { refreshView: () => void }) {
  const [rows, setRows] = useState(5)
  const [cols, setCols] = useState(5)
  const [mines, setMines] = useState(5)
  const [board, setBoard] = useState<(number | string)[][]>([])
  const [solutions, setSolutions] = useState<any>(null)
  const [selectedCell, setSelectedCell] = useState<[number, number] | null>(null)
  const [maxSolutions, setMaxSolutions] = useState(10)
  const [animatingSolutions, setAnimatingSolutions] = useState(false)

  // Initialiser le tableau au chargement et lors des changements de dimensions
  useEffect(() => {
    initializeBoard()
  }, [rows, cols])

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

  // Corriger la fonction handleSizeChange
  const handleSizeChange = () => {
    // Vérifier que les valeurs sont valides
    const validRows = Math.max(2, Math.min(100, rows))
    const validCols = Math.max(2, Math.min(100, cols))
    const validMines = Math.max(1, Math.min(validRows * validCols - 1, mines))

    // Mettre à jour les états avec les valeurs validées
    setRows(validRows)
    setCols(validCols)
    setMines(validMines)

    // Initialiser le tableau avec les nouvelles dimensions
    setBoard(
      Array(validRows)
        .fill(null)
        .map(() => Array(validCols).fill("?")),
    )

    setSolutions(null)
    setSelectedCell(null)

    // Forcer un rafraîchissement
    refreshView()
  }

  // Ajouter des gestionnaires d'événements pour les changements de dimensions
  const handleRowsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 2
    setRows(Math.max(2, Math.min(100, value)))
  }

  const handleColsChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || 2
    setCols(Math.max(2, Math.min(100, value)))
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

  return (
    <div className="flex flex-col items-center">
      <div className="grid grid-cols-4 gap-4 mb-6 w-full">
        <div>
          <Label htmlFor="rows">Rows</Label>
          <Input id="rows" type="number" min="2" max="100" value={rows} onChange={handleRowsChange} />
        </div>
        <div>
          <Label htmlFor="cols">Columns</Label>
          <Input id="cols" type="number" min="2" max="100" value={cols} onChange={handleColsChange} />
        </div>
        <div>
          <Label htmlFor="mines">Mines</Label>
          <Input id="mines" type="number" min="1" max={rows * cols - 1} value={mines} onChange={handleMinesChange} />
        </div>
        <div>
          <Label htmlFor="max-solutions">Max Solutions</Label>
          <Input
            id="max-solutions"
            type="number"
            min="1"
            max="100"
            value={maxSolutions}
            onChange={handleMaxSolutionsChange}
          />
        </div>
      </div>

      <div className="flex gap-4 mb-6">
        <Button onClick={handleSizeChange}>Apply Size</Button>
        <Button onClick={handleReset} variant="outline">
          Reset Board
        </Button>
        <Button onClick={handleSolve}>Solve CSP</Button>
        {solutions && (
          <Button onClick={animateSolutions} variant="outline">
            Animate Solutions
          </Button>
        )}
      </div>

      <div className="flex gap-8 mb-8">
        <div>
          <h3 className="text-lg font-medium mb-2">Board Setup</h3>
          <p className="text-sm text-gray-500 mb-4">
            Click on a cell to select it, then choose a value from the dropdown. Use "?" for unknown cells and numbers
            for revealed cells.
          </p>

          <div className="inline-block border-2 border-gray-300 bg-gray-100">
            {board.map((row, rowIndex) => (
              <div key={rowIndex} className="flex">
                {row.map((cell, colIndex) => (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={`
                    flex items-center justify-center
                    w-10 h-10 border border-gray-300
                    ${
                      selectedCell && selectedCell[0] === rowIndex && selectedCell[1] === colIndex
                        ? "bg-blue-200"
                        : "bg-gray-200 hover:bg-gray-300"
                    }
                    cursor-pointer
                  `}
                    onClick={() => handleCellClick(rowIndex, colIndex)}
                  >
                    {cell === "?" ? "?" : cell}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>

        {selectedCell && selectedCell[0] < rows && selectedCell[1] < cols && (
          <div>
            <h3 className="text-lg font-medium mb-2">Cell Value</h3>
            <p className="text-sm text-gray-500 mb-4">
              Selected cell: Row {selectedCell[0] + 1}, Column {selectedCell[1] + 1}
            </p>

            <Select value={board[selectedCell[0]][selectedCell[1]].toString()} onValueChange={handleCellValueChange}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select value" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="?">? (Unknown)</SelectItem>
                <SelectItem value="0">0</SelectItem>
                <SelectItem value="1">1</SelectItem>
                <SelectItem value="2">2</SelectItem>
                <SelectItem value="3">3</SelectItem>
                <SelectItem value="4">4</SelectItem>
                <SelectItem value="5">5</SelectItem>
                <SelectItem value="6">6</SelectItem>
                <SelectItem value="7">7</SelectItem>
                <SelectItem value="8">8</SelectItem>
              </SelectContent>
            </Select>
          </div>
        )}
      </div>

      {solutions && (
        <div className="w-full">
          <h2 className="text-xl font-bold mb-4">CSP Solutions</h2>
          <SolutionDisplay solution={solutions} animating={animatingSolutions} />
        </div>
      )}
    </div>
  )
}
