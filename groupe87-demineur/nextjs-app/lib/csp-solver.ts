import type { CSPVariable, CSPConstraint } from "./types"

/**
 * Solves a Minesweeper board using Constraint Satisfaction Problem (CSP) techniques
 *
 * @param board The current state of the board, with "?" for unknown cells and numbers for revealed cells
 * @param totalMines The total number of mines on the board
 * @param knownMines Optional array of known mine positions [row, col]
 * @param maxSolutions Maximum number of solutions to find
 * @returns Object containing solutions and recommendations
 */
export function solveMinesweeperCSP(
  board: (number | string)[][],
  totalMines: number,
  knownMines: number[][] = [],
  maxSolutions = 10,
) {
  const rows = board.length
  const cols = board[0].length

  // Create variables for each unknown cell
  const variables: CSPVariable[] = []
  const knownMinePositions = new Set(knownMines.map(([r, c]) => `${r},${c}`))

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (board[r][c] === "?" && !knownMinePositions.has(`${r},${c}`)) {
        variables.push({
          row: r,
          col: c,
          domain: [0, 1], // 0 = no mine, 1 = mine
        })
      }
    }
  }

  // Create constraints based on revealed cells
  const constraints: CSPConstraint[] = []

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (typeof board[r][c] === "number") {
        const adjacentVars: CSPVariable[] = []
        let knownAdjacentMines = 0

        // Check all 8 adjacent cells
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

  // Add constraint for total number of mines
  const totalMineConstraint: CSPConstraint = {
    variables: variables,
    sum: totalMines - knownMines.length,
  }
  constraints.push(totalMineConstraint)

  // Find all solutions using backtracking
  const solutions = findAllSolutions(variables, constraints, maxSolutions)

  // Calculate probabilities for each cell
  const probabilities = calculateProbabilities(rows, cols, solutions, knownMines)

  // Generate recommendations
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

/**
 * Finds all valid solutions to the CSP using backtracking
 */
function findAllSolutions(variables: CSPVariable[], constraints: CSPConstraint[], maxSolutions = 10): number[][][] {
  const solutions: number[][][] = []
  const assignment: Map<string, number> = new Map()

  // Recursive backtracking function
  function backtrack(index: number) {
    // If we've found enough solutions, stop searching
    if (solutions.length >= maxSolutions) {
      return
    }

    // Base case: all variables assigned
    if (index === variables.length) {
      // Check if all constraints are satisfied
      if (isAssignmentValid(assignment, constraints)) {
        // Convert assignment to a solution board
        const solution = createSolutionBoard(variables, assignment)
        solutions.push(solution)
      }
      return
    }

    const variable = variables[index]
    const key = `${variable.row},${variable.col}`

    // Try each value in the domain
    for (const value of variable.domain) {
      assignment.set(key, value)

      // Check if partial assignment is valid
      if (isPartialAssignmentValid(assignment, constraints)) {
        backtrack(index + 1)
      }

      assignment.delete(key)
    }
  }

  // Start backtracking
  backtrack(0)

  return solutions
}

/**
 * Checks if a partial assignment is valid
 */
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

    // If all variables are assigned, check if sum matches
    if (unassignedCount === 0) {
      if (sum !== constraint.sum) {
        return false
      }
    } else {
      // Check if partial assignment is still feasible
      remainingSum -= sum

      // If remaining sum is negative or greater than number of unassigned variables,
      // this partial assignment cannot lead to a valid solution
      if (remainingSum < 0 || remainingSum > unassignedCount) {
        return false
      }
    }
  }

  return true
}

/**
 * Checks if a complete assignment satisfies all constraints
 */
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

/**
 * Creates a solution board from an assignment
 */
function createSolutionBoard(variables: CSPVariable[], assignment: Map<string, number>): number[][] {
  if (variables.length === 0) return []

  // Find board dimensions
  let maxRow = 0
  let maxCol = 0

  for (const variable of variables) {
    maxRow = Math.max(maxRow, variable.row)
    maxCol = Math.max(maxCol, variable.col)
  }

  // Create empty board
  const board = Array(maxRow + 1)
    .fill(null)
    .map(() => Array(maxCol + 1).fill(0))

  // Fill in assigned values
  for (const variable of variables) {
    const key = `${variable.row},${variable.col}`
    board[variable.row][variable.col] = assignment.get(key) || 0
  }

  return board
}

/**
 * Calculates the probability of a mine for each cell based on all solutions
 */
function calculateProbabilities(
  rows: number,
  cols: number,
  solutions: number[][][],
  knownMines: number[][],
): number[][] {
  const probabilities = Array(rows)
    .fill(null)
    .map(() => Array(cols).fill(0))

  // Mark known mines with 100% probability
  for (const [r, c] of knownMines) {
    probabilities[r][c] = 1
  }

  if (solutions.length === 0) return probabilities

  // Calculate probabilities based on solutions
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (probabilities[r][c] === 1) continue // Skip known mines

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
