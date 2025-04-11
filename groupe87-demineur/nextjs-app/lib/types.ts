export interface Cell {
  isMine: boolean
  isRevealed: boolean
  isFlagged: boolean
  adjacentMines: number
}

export interface CSPVariable {
  row: number
  col: number
  domain: number[]
}

export interface CSPConstraint {
  variables: CSPVariable[]
  sum: number
}
