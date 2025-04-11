"use client"

import { Alert, AlertDescription } from "@/components/ui/alert"
import MinesweeperBoard from "./minesweeper-board"
import SolutionDisplay from "./solution-display"
import GameControls from "./game-controls"
import GameStats from "./game-stats"
import GameTimer from "./game-timer"
import { useMinesweeper } from "@/hooks/use-minesweeper"

export default function MinesweeperGame({ refreshView }: { refreshView: () => void }) {
  const {
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
  } = useMinesweeper(refreshView)

  return (
    <div className="flex flex-col items-center">
      <div className="flex justify-between w-full mb-4">
        <GameTimer isRunning={timerRunning} onTimeUpdate={handleTimeUpdate} resetKey={resetKey} />
      </div>

      <GameStats
        timeElapsed={timeElapsed}
        flagsPlaced={flagsPlaced}
        totalMines={gameConfig.mines}
        gamesWon={stats.gamesWon}
        gamesPlayed={stats.gamesPlayed}
      />

      <GameControls
        difficulty={difficulty}
        onDifficultyChange={handleDifficultyChange}
        customConfig={customConfig}
        onCustomConfigChange={updateCustomConfig}
        onReset={resetGame}
        onSolve={handleSolveCSP}
        onNextMove={handleNextMove}
        onShowHint={showNextHint}
        onAnimateSolution={animateSolution}
        minesRemaining={gameConfig.mines - flagsPlaced}
        isPlaying={gameState === "playing"}
        isFirstClick={firstClick}
        hasSolution={!!solution}
      />

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
          <SolutionDisplay solution={solution} />
        </div>
      )}
    </div>
  )
}
