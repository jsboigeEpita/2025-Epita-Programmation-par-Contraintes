package org.example;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class RoundRobinScheduler {

    static int nbResult = 1;

    public static void run() {
        int n = 8;
        int rounds = n - 1;
        int matchesPerRound = n / 2;

        int maxConsecutive = 2;


        boolean[][] dispo = new boolean[n][rounds];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                dispo[t][r] = true;
            }
        }

        Model model = new Model("Calendrier de tournoi Round Robin");

        IntVar[][] home = new IntVar[rounds][matchesPerRound];
        IntVar[][] away = new IntVar[rounds][matchesPerRound];

        IntVar[][] pair = new IntVar[rounds][matchesPerRound];

        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                home[r][m] = model.intVar("home_" + r + "_" + m, 0, n - 1);
                away[r][m] = model.intVar("away_" + r + "_" + m, 0, n - 1);
                model.arithm(home[r][m], "!=", away[r][m]).post();
                pair[r][m] = model.intVar("pair_" + r + "_" + m, 0, n * n - 1);
            }
        }

        // Contrainte 1 : Chaque équipe joue une seule fois par journée.
        for (int r = 0; r < rounds; r++) {
            IntVar[] teamsRound = new IntVar[n];
            int idx = 0;
            for (int m = 0; m < matchesPerRound; m++) {
                teamsRound[idx++] = home[r][m];
                teamsRound[idx++] = away[r][m];
            }
            model.allDifferent(teamsRound).post();
        }

        // Contrainte 2 : Chaque paire d'équipes (peu importe l'ordre) se rencontre une seule fois.
        IntVar[] allPairs = new IntVar[rounds * matchesPerRound];
        int index = 0;
        for (int r = 0; r < rounds; r++) {
            for (int m = 0; m < matchesPerRound; m++) {
                IntVar minTeam = model.intVar("min_" + r + "_" + m, 0, n - 1);
                IntVar maxTeam = model.intVar("max_" + r + "_" + m, 0, n - 1);

                model.ifThenElse(
                        model.arithm(home[r][m], "<", away[r][m]),
                        model.and(
                                model.arithm(minTeam, "=", home[r][m]),
                                model.arithm(maxTeam, "=", away[r][m])
                        ),
                        model.and(
                                model.arithm(minTeam, "=", away[r][m]),
                                model.arithm(maxTeam, "=", home[r][m])
                        )
                );
                model.scalar(new IntVar[]{minTeam, maxTeam}, new int[]{n, 1}, "=", pair[r][m]).post();

                allPairs[index++] = pair[r][m];
            }
        }
        model.allDifferent(allPairs).post();

        // Contrainte 3 : Alternance domicile/extérieur pour chaque équipe.
        IntVar[][] homeIndicator = new IntVar[n][rounds];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                homeIndicator[t][r] = model.intVar("H_" + t + "_" + r, 0, 1);
                IntVar[] homeMatches = new IntVar[matchesPerRound];
                for (int m = 0; m < matchesPerRound; m++) {
                    homeMatches[m] = home[r][m];
                }
                model.count(t, homeMatches, homeIndicator[t][r]).post();
            }
        }
        for (int t = 0; t < n; t++) {
            for (int r = 0; r <= rounds - (maxConsecutive + 1); r++) {
                IntVar[] window = new IntVar[maxConsecutive + 1];
                for (int k = 0; k < maxConsecutive + 1; k++) {
                    window[k] = homeIndicator[t][r + k];
                }
                model.sum(window, "<=", maxConsecutive).post();
            }
        }

        // Contrainte 4 : Disponibilités de stades.
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds; r++) {
                if (!dispo[t][r]) {
                    model.arithm(homeIndicator[t][r], "=", 0).post();
                }
            }
        }

        IntVar[][] breakVars = new IntVar[n][rounds - 1];
        for (int t = 0; t < n; t++) {
            for (int r = 0; r < rounds - 1; r++) {
                breakVars[t][r] = model.intVar("break_" + t + "_" + r, 0, 1);
                model.ifThenElse(
                    model.arithm(homeIndicator[t][r], "=", homeIndicator[t][r+1]),
                    model.arithm(breakVars[t][r], "=", 1),
                    model.arithm(breakVars[t][r], "=", 0)
                );
            }
        }

        IntVar[] breakCount = new IntVar[n];
        for (int t = 0; t < n; t++) {
            breakCount[t] = model.intVar("breakCount_" + t, 0, rounds - 1);
            model.sum(breakVars[t], "=", breakCount[t]).post();
        }

        IntVar totalBreaks = model.intVar("totalBreaks", 0, n * (rounds - 1));
        model.sum(breakCount, "=", totalBreaks).post();
        // model.arithm(totalBreaks, "=", n - 2).post();

        Solver solver = model.getSolver();
        solver.showStatistics();
        solver.showSolutions();
        solver.setSearch(Search.inputOrderLBSearch(model.retrieveIntVars(true)));

        int nbSolutions = nbResult;
        while (solver.findOptimalSolution(totalBreaks, Model.MINIMIZE) != null) {
            System.out.println("=== Solution trouvée ===");
            for (int r = 0; r < rounds; r++) {
                System.out.println("Journée " + (r + 1) + " :");
                for (int m = 0; m < matchesPerRound; m++) {
                    System.out.println("  Match : Équipe " + home[r][m].getValue()
                            + " (domicile) vs Équipe " + away[r][m].getValue() + " (extérieur)");
                }
            }
            System.out.println("------------------------");
            nbSolutions--;
        }

        if (solver.getSolutionCount() == 0) {
            System.out.println("Aucune solution trouvée.");
        }
    }
}
