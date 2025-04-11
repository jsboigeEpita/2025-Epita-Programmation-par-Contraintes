"use client"

import type React from "react"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { RefreshCw, Lightbulb, Play, Bomb, ArrowRight } from "lucide-react"

interface GameControlsProps {
  difficulty: string
  onDifficultyChange: (value: string) => void
  customConfig: { rows: number; cols: number; mines: number }
  onCustomConfigChange: (field: "rows" | "cols" | "mines", value: number) => void
  onReset: () => void
  onSolve: () => void
  onNextMove: () => void
  onShowHint: () => void
  onAnimateSolution: () => void
  minesRemaining: number
  isPlaying: boolean
  isFirstClick: boolean
  hasSolution: boolean
}

export default function GameControls({
  difficulty,
  onDifficultyChange,
  customConfig,
  onCustomConfigChange,
  onReset,
  onSolve,
  onNextMove,
  onShowHint,
  onAnimateSolution,
  minesRemaining,
  isPlaying,
  isFirstClick,
  hasSolution,
}: GameControlsProps) {
  const handleDifficultyChange = (value: string) => {
    onDifficultyChange(value)
  }

  const handleCustomConfigChange = (field: "rows" | "cols" | "mines", e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number.parseInt(e.target.value) || (field === "mines" ? 1 : 2)

    let validValue = value
    if (field === "rows" || field === "cols") {
      validValue = Math.max(2, Math.min(150, value))
    } else if (field === "mines") {
      const maxMines = customConfig.rows * customConfig.cols - 1
      validValue = Math.max(1, Math.min(maxMines, value))
    }

    onCustomConfigChange(field, validValue)
  }

  return (
    <div className="w-full">
      <div className="flex justify-between w-full mb-4">
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
            <span>{minesRemaining}</span>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={onReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={onSolve} disabled={!isPlaying || isFirstClick}>
            Solve with CSP
          </Button>
          <Button onClick={onNextMove} disabled={!isPlaying || isFirstClick} variant="secondary">
            <ArrowRight className="h-4 w-4 mr-2" />
            Next Move
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
              max="150"
              value={customConfig.rows}
              onChange={(e) => handleCustomConfigChange("rows", e)}
            />
          </div>
          <div>
            <Label htmlFor="custom-cols">Columns</Label>
            <Input
              id="custom-cols"
              type="number"
              min="2"
              max="150"
              value={customConfig.cols}
              onChange={(e) => handleCustomConfigChange("cols", e)}
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
              onChange={(e) => handleCustomConfigChange("mines", e)}
            />
          </div>
        </div>
      )}

      {hasSolution && (
        <div className="flex gap-4 mb-4">
          <Button onClick={onShowHint} variant="outline" disabled={!isPlaying}>
            <Lightbulb className="h-4 w-4 mr-2" />
            Show Hint
          </Button>
          <Button onClick={onAnimateSolution} variant="outline" disabled={!isPlaying}>
            <Play className="h-4 w-4 mr-2" />
            Animate Solution
          </Button>
        </div>
      )}
    </div>
  )
}
