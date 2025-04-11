"use client"

import type React from "react"

import type { Cell } from "@/lib/types"
import { Bomb, Flag } from "lucide-react"
import { NUMBER_COLORS } from "@/lib/constants"

interface MinesweeperBoardProps {
  board: Cell[][]
  onCellClick: (row: number, col: number) => void
  onCellRightClick: (row: number, col: number, e: React.MouseEvent) => void
  showHint?: [number, number][]
  animatingSolution?: number[][] | null
}

export default function MinesweeperBoard({
  board,
  onCellClick,
  onCellRightClick,
  showHint = [],
  animatingSolution = null,
}: MinesweeperBoardProps) {
  const hintCells = new Set(showHint.map(([r, c]) => `${r},${c}`))

  return (
    <div className="inline-block border-2 border-gray-300 bg-gray-100">
      {board.map((row, rowIndex) => (
        <div key={rowIndex} className="flex">
          {row.map((cell, colIndex) => {
            const isHint = hintCells.has(`${rowIndex},${colIndex}`)
            const isSolutionMine =
              animatingSolution &&
              rowIndex < animatingSolution.length &&
              colIndex < animatingSolution[0].length &&
              animatingSolution[rowIndex][colIndex] === 1

            return (
              <div
                key={`${rowIndex}-${colIndex}`}
                className={`
                  flex items-center justify-center
                  w-10 h-10 border border-gray-300
                  ${
                    cell.isRevealed
                      ? cell.isMine
                        ? "bg-red-200"
                        : "bg-gray-200"
                      : isHint
                        ? "bg-green-300 animate-pulse"
                        : isSolutionMine
                          ? "bg-red-300 animate-pulse"
                          : "bg-gray-300 hover:bg-gray-400 cursor-pointer"
                  }
                  transition-colors
                `}
                onClick={() => onCellClick(rowIndex, colIndex)}
                onContextMenu={(e) => onCellRightClick(rowIndex, colIndex, e)}
              >
                {cell.isRevealed ? (
                  cell.isMine ? (
                    <Bomb className="h-6 w-6 text-black" />
                  ) : (
                    cell.adjacentMines > 0 && (
                      <span className={`font-bold ${NUMBER_COLORS[cell.adjacentMines]}`}>{cell.adjacentMines}</span>
                    )
                  )
                ) : cell.isFlagged ? (
                  <Flag className="h-5 w-5 text-red-600" />
                ) : (
                  isHint && <span className="h-2 w-2 rounded-full bg-green-600 animate-ping"></span>
                )}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}
