"use client"

import { useState, useCallback } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import CSPSolver from "@/components/csp-solver"
import MinesweeperGame from "@/components/minesweeper-game-refactored"

export default function Home() {
  const [key, setKey] = useState(0)
  const [activeTab, setActiveTab] = useState("play")

  const refreshView = useCallback(() => {
    setKey((prev) => prev + 1)
  }, [])

  const handleTab = useCallback(
    (value: string) => {
      setActiveTab(value)
      refreshView()
    },
    [refreshView],
  )

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-50">
      <h1 className="text-4xl font-bold mb-8 text-gray-800">Minesweeper with CSP Solver</h1>

      <Tabs value={activeTab} onValueChange={handleTab} className="w-full max-w-4xl">
        <TabsList className="grid w-full grid-cols-2 mb-8">
          <TabsTrigger value="play">Play Minesweeper</TabsTrigger>
          <TabsTrigger value="solve">View CSP Solutions</TabsTrigger>
        </TabsList>

        <TabsContent value="play" key={`play-${key}`}>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <MinesweeperGame refreshView={refreshView} />
          </div>
        </TabsContent>

        <TabsContent value="solve" key={`solve-${key}`}>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <CSPSolver refreshView={refreshView} />
          </div>
        </TabsContent>
      </Tabs>
    </main>
  )
}
