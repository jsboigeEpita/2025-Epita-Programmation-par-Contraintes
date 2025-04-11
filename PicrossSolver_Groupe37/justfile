default_size := '8'
# example := "smiley"
example := "smiley-sourire-tapis-de-souris"

help:
    just -l


show-generation:
    xdg-open ./tests/smiley-sourire-tapis-de-souris.jpg &
    python ./generate/image_to_pc.py ./tests/smiley-sourire-tapis-de-souris.jpg 32

# Generate a test puzzle of specified size
generate size=default_size:
    cargo run -q --release --bin image_to_pc ./tests/{{example}}.jpg {{size}}
    @printf "\n\\033[1mGenerated puzzle:\033[0m\n"
    @cat ./{{example}}.pc
    @printf "\n\\033[1mSolution:\033[0m\n"
    @cat ./{{example}}.pcs | lolcat

# Naive approch
demo-1:
    cargo run -q --release --bin solver ./{{example}}.pc


# Existing tool
demo-2:
    #!/usr/bin/env bash
    @git clone https://github.com/tsionyx/nonogrid || true
    cd nonogrid
    wget -qO- https://webpbn.com/export.cgi --post-data "id=32480&fmt=nin&go=1" | cargo run -q --release 2>/dev/null | lolcat

# Ortools contraint programming
demo-3:
    python src/solvers/ortools_solver.py {{example}}.pc

clean:
    rm -rf *.pc *.pcs
