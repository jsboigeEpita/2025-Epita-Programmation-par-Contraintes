import type { CSPVariable, CSPConstraint } from "./types"

export function solveMinesweeperCSP(
  board: (number | string)[][],
  totalMines: number,
  knownMines: number[][] = [],
  maxSolutions = 10,
) {
  const rows = board.length
  const cols = board[0].length

  const variables: CSPVariable[] = []
  const knownMinePositions = new Set(knownMines.map(([r, c]) => `${r},${c}`))

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (board[r][c] === "?" && !knownMinePositions.has(`${r},${c}`)) {
        variables.push({
          row: r,
          col: c,
          domain: [0, 1],
        })
      }
    }
  }

  const constraints: CSPConstraint[] = []

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (typeof board[r][c] === "number") {
        const adjacentVars: CSPVariable[] = []
        let knownAdjacentMines = 0

        for (let dr = -1; dr <= 1; dr++) {
          for (let dc = -1; dc <= 1; dc++) {
            if (dr === 0 && dc === 0) continue

            const nr = r + dr
            const nc = c + dc

            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols) {
              if (knownMinePositions.has(`${nr},${nc}`)) {
                knownAdjacentMines++
              } else if (board[nr][nc] === "?") {
                const variable = variables.find((v) => v.row === nr && v.col === nc)
                if (variable) {
                  adjacentVars.push(variable)
                }
              }
            }
          }
        }

        if (adjacentVars.length > 0) {
          constraints.push({
            variables: adjacentVars,
            sum: (board[r][c] as number) - knownAdjacentMines,
          })
        }
      }
    }
  }

  const totalMineConstraint: CSPConstraint = {
    variables: variables,
    sum: totalMines - knownMines.length,
  }
  constraints.push(totalMineConstraint)

  const solutions = findAllSolutions(variables, constraints, maxSolutions)
  const probabilities = calculateProbabilities(rows, cols, solutions, knownMines)

  const safeRecommendations: [number, number][] = []
  const mineRecommendations: [number, number][] = []

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (board[r][c] === "?" && !knownMinePositions.has(`${r},${c}`)) {
        if (probabilities[r][c] === 0) {
          safeRecommendations.push([r, c])
        } else if (probabilities[r][c] === 1) {
          mineRecommendations.push([r, c])
        }
      }
    }
  }

  return {
    solutions,
    probabilities,
    safeRecommendations,
    mineRecommendations,
  }
}

function findAllSolutions(variables: CSPVariable[], constraints: CSPConstraint[], maxSolutions = 10): number[][][] {
  const solutions: number[][][] = []
  const assignment: Map<string, number> = new Map()

  function backtrack(index: number) {
    if (solutions.length >= maxSolutions) {
      return
    }

    if (index === variables.length) {
      if (isAssignmentValid(assignment, constraints)) {
        const solution = createSolutionBoard(variables, assignment)
        solutions.push(solution)
      }
      return
    }

    const variable = variables[index]
    const key = `${variable.row},${variable.col}`

    for (const value of variable.domain) {
      assignment.set(key, value)

      if (isPartialAssignmentValid(assignment, constraints)) {
        backtrack(index + 1)
      }

      assignment.delete(key)
    }
  }

  backtrack(0)

  return solutions
}

function isPartialAssignmentValid(assignment: Map<string, number>, constraints: CSPConstraint[]): boolean {
  for (const constraint of constraints) {
    let sum = 0
    let unassignedCount = 0
    let remainingSum = constraint.sum

    for (const variable of constraint.variables) {
      const key = `${variable.row},${variable.col}`
      if (assignment.has(key)) {
        sum += assignment.get(key)!
      } else {
        unassignedCount++
      }
    }

    if (unassignedCount === 0) {
      if (sum !== constraint.sum) {
        return false
      }
    } else {
      remainingSum -= sum

      if (remainingSum < 0 || remainingSum > unassignedCount) {
        return false
      }
    }
  }

  return true
}

function isAssignmentValid(assignment: Map<string, number>, constraints: CSPConstraint[]): boolean {
  for (const constraint of constraints) {
    let sum = 0

    for (const variable of constraint.variables) {
      const key = `${variable.row},${variable.col}`
      sum += assignment.get(key)!
    }

    if (sum !== constraint.sum) {
      return false
    }
  }

  return true
}

function createSolutionBoard(variables: CSPVariable[], assignment: Map<string, number>): number[][] {
  if (variables.length === 0) return []

  let maxRow = 0
  let maxCol = 0

  for (const variable of variables) {
    maxRow = Math.max(maxRow, variable.row)
    maxCol = Math.max(maxCol, variable.col)
  }

  const board = Array(maxRow + 1)
    .fill(null)
    .map(() => Array(maxCol + 1).fill(0))

  for (const variable of variables) {
    const key = `${variable.row},${variable.col}`
    board[variable.row][variable.col] = assignment.get(key) || 0
  }

  return board
}

function calculateProbabilities(
  rows: number,
  cols: number,
  solutions: number[][][],
  knownMines: number[][],
): number[][] {
  const probabilities = Array(rows)
    .fill(null)
    .map(() => Array(cols).fill(0))

  for (const [r, c] of knownMines) {
    probabilities[r][c] = 1
  }

  if (solutions.length === 0) return probabilities

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (probabilities[r][c] === 1) continue

      let mineCount = 0

      for (const solution of solutions) {
        if (r < solution.length && c < solution[0].length && solution[r][c] === 1) {
          mineCount++
        }
      }

      probabilities[r][c] = mineCount / solutions.length
    }
  }

  return probabilities
}
