"use client"

import { Bomb } from "lucide-react"
import { useState, useEffect } from "react"

interface SolutionDisplayProps {
  solution: {
    solutions: number[][][]
    probabilities?: number[][]
    safeRecommendations?: [number, number][]
    mineRecommendations?: [number, number][]
  }
  animating?: boolean
}

export default function SolutionDisplay({ solution, animating = false }: SolutionDisplayProps) {
  const { solutions, probabilities, safeRecommendations, mineRecommendations } = solution
  const [currentSolutionIndex, setCurrentSolutionIndex] = useState(0)

  useEffect(() => {
    if (animating && solutions.length > 1) {
      const interval = setInterval(() => {
        setCurrentSolutionIndex((prev) => (prev + 1) % solutions.length)
      }, 500)

      return () => clearInterval(interval)
    } else {
      setCurrentSolutionIndex(0)
    }
  }, [animating, solutions.length])

  if (solutions.length === 0) {
    return (
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
        <p className="text-yellow-800">No solutions found for the current board state.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {solutions.length > 1 && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-blue-800">
            Found {solutions.length} possible solutions for the current board state.
            {animating && ` Showing solution ${currentSolutionIndex + 1} of ${solutions.length}`}
          </p>
        </div>
      )}

      {probabilities && (
        <div>
          <h3 className="text-lg font-medium mb-2">Mine Probabilities</h3>
          <div className="inline-block border-2 border-gray-300 bg-gray-100">
            {probabilities.map((row, rowIndex) => (
              <div key={rowIndex} className="flex">
                {row.map((probability, colIndex) => (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    className={`
                      flex items-center justify-center
                      w-10 h-10 border border-gray-300
                      ${probability === 1 ? "bg-red-200" : probability === 0 ? "bg-green-200" : "bg-yellow-100"}
                      ${animating ? "transition-colors duration-500" : ""}
                    `}
                  >
                    {probability === 1 ? (
                      <Bomb className="h-5 w-5 text-black" />
                    ) : (
                      <span className={`text-sm ${probability === 0 ? "text-green-700" : "text-red-700"}`}>
                        {Math.round(probability * 100)}%
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}

      {safeRecommendations && safeRecommendations.length > 0 && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-lg font-medium mb-2 text-green-800">Safe Moves</h3>
          <ul className="list-disc pl-5 text-green-700">
            {safeRecommendations.map(([row, col], index) => (
              <li key={index}>
                Row {row + 1}, Column {col + 1}
              </li>
            ))}
          </ul>
        </div>
      )}

      {mineRecommendations && mineRecommendations.length > 0 && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <h3 className="text-lg font-medium mb-2 text-red-800">Definite Mines</h3>
          <ul className="list-disc pl-5 text-red-700">
            {mineRecommendations.map(([row, col], index) => (
              <li key={index}>
                Row {row + 1}, Column {col + 1}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h3 className="text-lg font-medium mb-2">
          {animating && solutions.length > 1 ? `Solution ${currentSolutionIndex + 1}` : "First Solution"}
        </h3>
        <div className="inline-block border-2 border-gray-300 bg-gray-100">
          {(animating && solutions.length > 1 ? solutions[currentSolutionIndex] : solutions[0]).map((row, rowIndex) => (
            <div key={rowIndex} className="flex">
              {row.map((cell, colIndex) => (
                <div
                  key={`${rowIndex}-${colIndex}`}
                  className={`
                    flex items-center justify-center
                    w-10 h-10 border border-gray-300
                    ${cell === 1 ? "bg-red-200" : "bg-gray-200"}
                    ${animating ? "transition-colors duration-300" : ""}
                  `}
                >
                  {cell === 1 ? <Bomb className="h-5 w-5 text-black" /> : ""}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
