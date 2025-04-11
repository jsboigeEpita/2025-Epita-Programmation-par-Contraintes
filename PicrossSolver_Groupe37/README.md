# Solveur

## Quick start

dependencies: `just rust python(pillow, numpy, ortools, pandas)` or, have nix
installed and run `nix develop`

### Generate

```sh
❯ just generate 11
cargo run -q --release --bin image_to_pc ./tests/smiley-sourire-tapis-de-souris.jpg 11
wrote puzzle to smiley-sourire-tapis-de-souris.pc
wrote solutions to smiley-sourire-tapis-de-souris.pcs

Generated puzzle:
1 | 2 | 3 2 | 3 1 | 2 | 1 | 2 | 3 1 | 3 2 | 2 | 1
| 2 2 | 2 2 | 2 2 | | | 2 2 | 2 2 | 3 3 | 3 |

Solution:
...........
..##...##..
..##...##..
..##...##..
...........
...........
##.......##
.##.....##.
..###.###..
....###....
...........
```

### Run

```sh
# Run naïve solver on the generated puzzle
❯ just demo-1
cargo run -q --release --bin solver ./smiley-sourire-tapis-de-souris.pc
  12332123321
    21   12
  ...........
22..##...##..
22..##...##..
22..##...##..
  ...........
  ...........
22##.......##
22.##.....##.
33..###.###..
3 ....###....
  ...........

took 557ms 440us 198ns
```

```sh
# Run `PRCON` solver on the generated puzzle
❯ just demo-3
python src/solvers/ortools_solver.py smiley-sourire-tapis-de-souris.pc


     ##   ##
     ##   ##
     ##   ##


   ##       ##
    ##     ##
     ### ###
       ###


status: OPTIMAL

NumSolutions: 1
NumConflicts: 0
NumBranches: 0
WallTime: 0.00551566
```

## Solutions explorées

https://github.com/tsionyx/nonogrid

### Implementation naïve

- utilise le backtracking
- mets beaucoup de temps a se rendre compte d'une solution incorrecte
- nombre de cas a testé exponentiel:
  - 2x2: 16 possibilités
  - 4x4: 65536 possibilités

| taille de la grille | nombre de solutions existantes               |
| ------------------- | -------------------------------------------- |
| 2x2                 | 16                                           |
| 4x4                 | 65536                                        |
| 7x7                 | 562949953421312                              |
| 12x12               | 22300745198530623141535718272648361505980416 |

## Benchmarks

| taille de la grille | solution naïve    | solution `PRCON` |
| ------------------- | ----------------- | ---------------- |
| 9x9                 | 185ms             | 10ms             |
| 10x10               | 10s               | 15ms             |
| 13x13               | ~14.5 days (est.) | 45ms             |
| 15x15               | ~100 years (est.) | 70ms             |
