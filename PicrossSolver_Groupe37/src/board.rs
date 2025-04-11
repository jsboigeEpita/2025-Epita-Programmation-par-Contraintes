use std::{fmt::Display, str::FromStr};

use anyhow::bail;

const DELIM: &str = "|";

/// Puzzle input
#[derive(Debug, PartialEq, Eq)]
pub struct Puzzle {
    pub rows: Vec<Vec<u32>>,
    pub cols: Vec<Vec<u32>>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Cell {
    Empty,
    Filled,
}

/// Solved puzzle
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Board {
    pub table: Vec<Vec<Cell>>,
}

pub struct FullSolution {
    pub board: Board,
    pub puzzle: Puzzle,
}

impl Puzzle {
    pub fn size(&self) -> usize {
        assert_eq!(
            self.rows.len(),
            self.cols.len(),
            "Only square puzzle are supported"
        );
        self.cols.len()
    }
}

impl Board {
    pub fn size(&self) -> usize {
        if self.table.is_empty() {
            return 0;
        }

        assert_eq!(
            self.table.len(),
            self.table[0].len(),
            "Only square puzzle are supported"
        );
        self.table.len()
    }

    pub fn from_col(&self, col: usize) -> Vec<u32> {
        let mut cols: Vec<u32> = Vec::new();
        for i in 0..self.size() {
            if self.table[i][col] == Cell::Filled {
                if i > 0 && self.table[i - 1][col] == Cell::Filled {
                    *cols.last_mut().unwrap() += 1;
                } else {
                    cols.push(1);
                }
            }
        }
        cols
    }

    pub fn from_row(&self, row: usize) -> Vec<u32> {
        let mut rows: Vec<u32> = Vec::new();
        for i in 0..self.size() {
            if self.table[row][i] == Cell::Filled {
                if i > 0 && self.table[row][i - 1] == Cell::Filled {
                    *rows.last_mut().unwrap() += 1;
                } else {
                    rows.push(1);
                }
            }
        }
        rows
    }
}

impl Cell {
    fn repr(&self) -> char {
        match self {
            Cell::Empty => '.',
            Cell::Filled => '#',
        }
    }
}
impl TryFrom<char> for Cell {
    type Error = anyhow::Error;

    fn try_from(value: char) -> Result<Self, Self::Error> {
        match value {
            '.' => Ok(Cell::Empty),
            '#' => Ok(Cell::Filled),
            _ => bail!("Board can only contain filled ('#') or empty ('.') cells"),
        }
    }
}

impl Display for Board {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        for line in self.table.clone() {
            for cell in line {
                let repr = cell.repr();
                write!(f, "{repr}")?;
            }
            writeln!(f)?;
        }
        Ok(())
    }
}

impl Display for FullSolution {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        let upper_padding = self
            .puzzle
            .cols
            .iter()
            .map(|col| col.len())
            .max()
            .unwrap_or(0);
        let left_padding = self
            .puzzle
            .rows
            .iter()
            .map(|row| row.len())
            .max()
            .unwrap_or(0);

        for line in 0..upper_padding {
            write!(f, "{}", " ".repeat(left_padding))?;
            for col in &self.puzzle.cols {
                match col.get(line) {
                    Some(n) => {
                        write!(f, "{n}")?;
                    }

                    None => {
                        write!(f, " ")?;
                    }
                }
            }
            writeln!(f)?;
        }

        for (i, line) in self.board.table.clone().iter().enumerate() {
            for j in 0..left_padding {
                match self.puzzle.rows[i].get(j) {
                    Some(n) => {
                        write!(f, "{n}")?;
                    }
                    None => {
                        write!(f, " ")?;
                    }
                }
            }
            for cell in line {
                let repr = cell.repr();
                write!(f, "{repr}")?;
            }
            writeln!(f)?;
        }

        Ok(())
    }
}

impl FromStr for Board {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let table = s
            .trim()
            .lines()
            .map(|line| {
                line.chars()
                    .map(Cell::try_from)
                    .collect::<Result<Vec<_>, _>>()
            })
            .collect::<Result<Vec<_>, _>>()?;
        Ok(Self { table })
    }
}

// give puzzle representation of solved board
impl From<&Board> for Puzzle {
    fn from(board: &Board) -> Self {
        let mut rows: Vec<Vec<u32>> = vec![vec![]; board.size()];
        let mut cols = vec![vec![]; board.size()];

        #[allow(
            clippy::needless_range_loop,
            reason = "Easier to understand (+ flemme de refactor...)"
        )]
        for i in 0..board.size() {
            for j in 0..board.size() {
                if board.table[i][j] == Cell::Filled {
                    if j > 0 && board.table[i][j - 1] == Cell::Filled {
                        *rows[i].last_mut().unwrap() += 1;
                    } else {
                        rows[i].push(1);
                    }

                    if i > 0 && board.table[i - 1][j] == Cell::Filled {
                        *cols[j].last_mut().unwrap() += 1;
                    } else {
                        cols[j].push(1);
                    }
                }
            }
        }
        Self { rows, cols }
    }
}

fn parse_picross_grid_line(var_name: &&str) -> anyhow::Result<Vec<Vec<u32>>> {
    Ok(var_name
        .split(DELIM)
        .map(|line| {
            line.split_whitespace()
                .map(|num| num.parse::<u32>())
                .collect::<Result<Vec<_>, _>>()
        })
        .collect::<Result<Vec<_>, _>>()?)
}

impl FromStr for Puzzle {
    type Err = anyhow::Error;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let lines: Vec<_> = s.trim().lines().collect();
        if lines.len() != 2 {
            bail!("Input file should be 2 lines long");
        }

        Ok(Self {
            cols: parse_picross_grid_line(&lines[0])?,
            rows: parse_picross_grid_line(&lines[1])?,
        })
    }
}

#[cfg(test)]
mod tests {
    use pretty_assertions::assert_eq;
    use rstest::rstest;

    #[rstest]
    #[case(
        r"
5   | 5 3 | 3 1 1 2 | 2 1 1 2 | 5 1 1 | 1 1 1 | 3 1 1 | 1 1 | 5 1 1 | 5 1 2 | 3 1 1 2 | 2 1 3 | 5
5 5 | 5 5 | 3 1 3 1 | 2 1 2 1 | 5 1 5 | 1     | 2     | 3 3 | 1 5 1 | 2 2   | 2 2     | 7     |
",
        r"
#####...#####
#####...#####
###.#...###.#
##..#...##..#
#####.#.#####
......#......
.....##......
.###.....###.
.#..#####..#.
.##.......##.
..##.....##..
...#######...
.............
"
    )]
    fn test_puzzle_from_board(#[case] puzzle: &str, #[case] board_str: &str) -> anyhow::Result<()> {
        use super::{Board, Puzzle};

        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;

        assert_eq!(puzzle, Puzzle::from(&board));

        Ok(())
    }
}
