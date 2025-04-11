use crate::board::{Board, Cell, Puzzle};

pub fn is_valid_col(puzzle: &Puzzle, solution: &Board, col: usize) -> bool {
    // FIXME: this could be much faster by splitting this method
    let sub_puzzle = solution.from_col(col);

    if sub_puzzle.is_empty() {
        return sub_puzzle.len() <= puzzle.cols[col].len();
    }

    let i = sub_puzzle.len() - 1;
    sub_puzzle.len() <= puzzle.cols[col].len()
        && sub_puzzle[i] <= puzzle.cols[col][i]
}

pub fn is_valid_row(puzzle: &Puzzle, solution: &Board, row: usize) -> bool {
    // FIXME: this could be much faster by splitting this method
    let sub_puzzle = solution.from_row(row);

    if sub_puzzle.is_empty() {
        return sub_puzzle.len() <= puzzle.rows[row].len();
    }

    let i = sub_puzzle.len() - 1;
    sub_puzzle.len() <= puzzle.rows[row].len()
        && sub_puzzle[i] <= puzzle.rows[row][i]
}

pub fn is_valid(puzzle: &Puzzle, solution: &Board) -> bool {
    &Puzzle::from(solution) == puzzle
}

/// Dumb solver
fn solve_backtracking(puzzle: &Puzzle, i: usize, mut board: Board) -> Option<Board> {
    if i >= puzzle.size() * puzzle.size() {
        return is_valid(puzzle, &board).then_some(board);
    }
    let x = i / puzzle.size();
    let y = i % puzzle.size();

    // Dot not recurse if the previoulsy finished row is not full
    if x > 0 && y == 0 {
        if puzzle.rows[x - 1] != board.from_row(x - 1) {
            return None
        }
    }

    for state in [Cell::Filled, Cell::Empty] {
        board.table[x][y] = state;
        if !(is_valid_col(puzzle, &board, y) && is_valid_row(puzzle, &board, x)) {
            continue;
        }
        if let Some(solved) = solve_backtracking(puzzle, i + 1, board.clone()) {
            return Some(solved);
        }
    }
    None
}

pub fn solve(puzzle: &Puzzle) -> Option<Board> {
    let board = Board {
        table: vec![vec![Cell::Empty; puzzle.size()]; puzzle.size()],
    };
    solve_backtracking(puzzle, 0, board)
}

#[cfg(test)]
mod tests {
    use rstest::rstest;

    use super::solve;
    use super::{is_valid_col, is_valid_row};
    use crate::board::{Board, Puzzle};

    #[rstest]
    #[case(
        true,
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
    //     #[case(
    //         false,
    //         r"
    // 5   | 5 3 | 3 1 1 2 | 2 1 1 2 | 5 1 1 | 1 1 1 | 3 1 1 | 1 1 | 5 1 1 | 5 1 2 | 3 1 1 2 | 2 1 3 | 5
    // 5 5 | 5 5 | 3 1 3 1 | 2 1 2 1 | 5 1 5 | 1     | 2     | 3 3 | 1 5 1 | 2 2   | 2 2     | 7     |
    // ",
    //         r"
    // #####...#####
    // #####...#####
    // ###.#...###.#
    // ###.#...##..#
    // #####.#.#####
    // #....##......
    // .#...##......
    // .####.#..###.
    // .#.######.###
    // .##....#####.
    // ..##.....##..
    // ...#######...
    // ...........#.
    // "
    //     )]
    fn test_is_valid_col(
        #[case] valid: bool,
        #[case] puzzle: &str,
        #[case] board_str: &str,
    ) -> anyhow::Result<()> {
        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;

        for i in 0..board.size() {
            assert_eq!(is_valid_col(&puzzle, &board, i), valid, "At index {i}");
        }
        Ok(())
    }

    #[rstest]
    #[case(
        true,
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
    fn test_is_valid_row(
        #[case] valid: bool,
        #[case] puzzle: &str,
        #[case] board_str: &str,
    ) -> anyhow::Result<()> {
        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;

        for i in 0..board.size() {
            assert_eq!(is_valid_row(&puzzle, &board, i), valid, "At index {i}");
        }
        Ok(())
    }
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
    fn test_solve(#[case] puzzle: &str, #[case] board_str: &str) -> anyhow::Result<()> {
        let puzzle: Puzzle = puzzle.parse()?;
        let board: Board = board_str.parse()?;
        assert_eq!(board, solve(&puzzle).expect("Board to be solvable"));
        Ok(())
    }
}
