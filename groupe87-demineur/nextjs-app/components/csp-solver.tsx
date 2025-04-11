"use client"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import SolutionDisplay from "./solution-display"
import { useCSPSolver } from "@/hooks/use-csp-solver"

export default function CSPSolver() {
  const {
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
  } = useCSPSolver()

  return (
    <div className="flex flex-col items-center">
      <div className="grid grid-cols-4 gap-4 mb-6 w-full">
        <div>
          <Label htmlFor="rows">Rows</Label>
          <Input id="rows" type="number" min="2" max="150" value={rows} onChange={handleRowsChange} />
        </div>
        <div>
          <Label htmlFor="cols">Columns</Label>
          <Input id="cols" type="number" min="2" max="150" value={cols} onChange={handleColsChange} />
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
