# Copyright Maxou, Oscour, Oumine et Alouxis

from __future__ import print_function
from ortools.sat.python import cp_model as cp
import sys

MAX_SOLUTIONS = 3


class SolutionPrinter(cp.CpSolverSolutionCallback):
    """
    SolutionPrinter for Nonogram.
    """

    def __init__(
        self,
        board,
        rows,
        cols,
    ):
        cp.CpSolverSolutionCallback.__init__(self)
        self.__board = board
        self.__rows = rows
        self.__cols = cols
        self.__solution_count = 0

    def OnSolutionCallback(self):
        self.__solution_count += 1
        print()
        for i in range(self.__rows):
            row = [self.Value(self.__board[j, i]) for j in range(self.__cols)]
            row_pres = []
            for j in row:
                if j == 1:
                    row_pres.append("#")
                else:
                    row_pres.append(" ")
            print("  ", "".join(row_pres))
        print()

        if self.__solution_count >= MAX_SOLUTIONS:
            print(f"{MAX_SOLUTIONS} solutions is enough...")
            self.StopSearch()

    def SolutionCount(self):
        return self.__solution_count


def make_transition_automaton(pattern):
    """
    Make a transition (automaton) matrix from a
    single pattern, e.g. [3,2,1]
    """
    t = []
    c = 0
    for i in range(len(pattern)):
        t.append((c, 0, c))  # 0*
        for _j in range(pattern[i]):
            t.append((c, 1, c + 1))  # 1{pattern[i]}
            c += 1

        t.append((c, 0, c + 1))  # 0+
        c += 1

    t.append((c, 0, c))  # 0*

    return t, c


def load_nonogram(path: str):
    """
    Load a nonogram from a pc file. (Code is outerageous)
    """
    with open(path) as f:
        raw_lines = f.read().splitlines()
    parsed = [
        [list(map(int, part.strip().split())) for part in line.split("|")]
        for line in raw_lines
    ]

    # Trouver la longueur maximale dans tous les sous-tableaux
    max_len = max(len(sublist) for line in parsed for sublist in line)

    # Remplir avec des zéros
    [l1, l2] = [
        [[0] * (max_len - len(sublist)) + sublist for sublist in line]
        for line in parsed
    ]
    return l1, l2


def check_rule(model, rules, y):
    """
    Check each rule by creating an automaton
    and then run the regular constraint.
    """

    rules_tmp = []
    for i in range(len(rules)):
        if rules[i] > 0:
            rules_tmp.append(rules[i])

    transitions, last_state = make_transition_automaton(rules_tmp)

    initial_state = 0
    accepting_states = [last_state - 1, last_state]

    #
    # constraints
    #
    model.AddAutomaton(y, initial_state, accepting_states, transitions)


def main(rows, row_rule_len, row_rules, cols, col_rule_len, col_rules):
    """
    Run a Nonogram instance.
    """
    model = cp.CpModel()

    #
    # variables
    #
    board = {}
    for i in range(rows):
        for j in range(cols):
            board[i, j] = model.NewBoolVar("board[%i, %i]" % (i, j))

    #
    # constraints
    #
    for i in range(rows):
        check_rule(
            model,
            [row_rules[i][j] for j in range(row_rule_len)],
            [board[i, j] for j in range(cols)],
        )

    for j in range(cols):
        check_rule(
            model,
            [col_rules[j][k] for k in range(col_rule_len)],
            [board[i, j] for i in range(rows)],
        )

    #
    # solution and search
    #
    solver = cp.CpSolver()
    solver.parameters.linearization_level = 0
    solver.parameters.cp_model_probing_level = 0

    solution_printer = SolutionPrinter(board, rows, cols)
    status = solver.SearchForAllSolutions(model, solution_printer)

    print("status:", solver.StatusName(status))
    if not (status == cp.OPTIMAL or status == cp.FEASIBLE):
        print("No solution")

    print()
    print("NumSolutions:", solution_printer.SolutionCount())
    print("NumConflicts:", solver.NumConflicts())
    print("NumBranches:", solver.NumBranches())
    print("WallTime:", solver.WallTime())


if __name__ == "__main__":
    file = sys.argv[1]
    row_rules, col_rules = load_nonogram(file)

    rows = len(row_rules)
    cols = len(col_rules)

    row_rule_len = len(row_rules[0])
    col_rule_len = len(col_rules[0])

    main(rows, row_rule_len, row_rules, cols, col_rule_len, col_rules)
