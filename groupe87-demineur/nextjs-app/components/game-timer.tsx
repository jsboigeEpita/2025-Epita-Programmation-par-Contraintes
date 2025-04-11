"use client"

import { useEffect, useState } from "react"

interface GameTimerProps {
  isRunning: boolean
  onTimeUpdate: (time: number) => void
  resetKey?: number
}

export default function GameTimer({ isRunning, onTimeUpdate, resetKey = 0 }: GameTimerProps) {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    setSeconds(0)
    onTimeUpdate(0)
  }, [resetKey, onTimeUpdate])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null

    if (isRunning) {
      interval = setInterval(() => {
        setSeconds((prev) => {
          const newTime = prev + 1
          onTimeUpdate(newTime)
          return newTime
        })
      }, 1000)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [isRunning, onTimeUpdate])

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const secs = time % 60
    return `${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="text-2xl font-mono tabular-nums bg-gray-100 p-2 rounded-md border border-gray-300">
      {formatTime(seconds)}
    </div>
  )
}
