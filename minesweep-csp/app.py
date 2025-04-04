from flask import Flask, request, jsonify
from flask_cors import CORS
from backend import MinesweeperBackend

app = Flask(__name__)
CORS(
    app,
    origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization", "Accept"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

# Store active games
games = {}


@app.route("/api/game/new", methods=["POST"])
def new_game():
    """Create a new Minesweeper game."""
    try:
        data = request.get_json()
        width = data.get("width", 9)
        height = data.get("height", 9)
        num_mines = data.get("num_mines", 10)
        solver_type = data.get("solver_type", "basic")

        game_id = str(len(games))
        games[game_id] = MinesweeperBackend(width, height, num_mines, solver_type)

        return jsonify({"game_id": game_id, "state": games[game_id].get_game_state()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/game/<game_id>/state", methods=["GET"])
def get_game_state(game_id):
    """Get the current state of a game."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    state = games[game_id].get_game_state()

    state["explosions"] = games[game_id].nb_explosions

    return jsonify({"state": state})


@app.route("/api/game/<game_id>/reveal", methods=["POST"])
def reveal_cell(game_id):
    """Reveal a cell in the game."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    try:
        data = request.get_json()
        x = data.get("x")
        y = data.get("y")

        if x is None or y is None:
            return jsonify({"error": "Missing x or y coordinates"}), 400

        game = games[game_id]
        game_continues = game.reveal(x, y)

        return jsonify(
            {"state": game.get_game_state(), "game_continues": game_continues}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/game/<game_id>/flag", methods=["POST"])
def toggle_flag(game_id):
    """Toggle a flag on a cell."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    try:
        data = request.get_json()
        x = data.get("x")
        y = data.get("y")

        if x is None or y is None:
            return jsonify({"error": "Missing x or y coordinates"}), 400

        game = games[game_id]
        game.toggle_flag(x, y)

        return jsonify({"state": game.get_game_state()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/game/<game_id>/solve/next", methods=["GET"])
def get_next_solve_move(game_id):
    """Get the next move from the solver."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    game = games[game_id]
    next_move = game.solve_next_move()

    if next_move is None:
        return jsonify({"error": "No moves available"}), 400

    return jsonify({"x": next_move[0], "y": next_move[1]})


@app.route("/api/game/<game_id>/solve/apply", methods=["POST"])
def apply_solver_move(game_id):
    """Apply the next move from the solver."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    game = games[game_id]
    move_applied = game.apply_solver_move()

    return jsonify({"state": game.get_game_state(), "move_applied": move_applied})


@app.route("/api/game/<game_id>/solver", methods=["PUT"])
def change_solver(game_id):
    """Change the solver for a game."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    try:
        data = request.get_json()
        solver_type = data.get("solver_type")

        if not solver_type:
            return jsonify({"error": "Missing solver_type parameter"}), 400

        game = games[game_id]
        game.change_solver(solver_type)

        return jsonify({"state": game.get_game_state()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/solvers", methods=["GET"])
def get_available_solvers():
    """Get a list of available solver types."""
    return jsonify(
        {
            "solvers": [
                {
                    "id": "greedy",
                    "name": "Greedy Solver",
                    "description": "A basic solver that makes random guesses without taking into account cells information",
                },
                {
                    "id": "astar",
                    "name": "A* Solver",
                    "description": "An A* based solver that uses trivial moves and random guesses when needed",
                },
                {
                    "id": "astar_boost",
                    "name": "A* Boost",
                    "description": "An enhanced A* solver with probabilistic frontier analysis for better mine probability estimation when no trivial moves is found",
                },
            ]
        }
    )


@app.route("/api/game/<game_id>/reset", methods=["POST"])
def reset_game(game_id):
    """Reset a game to its initial state."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    game = games[game_id]
    game.reset_game()

    return jsonify({"state": game.get_game_state()})


@app.route("/api/games", methods=["GET"])
def list_games():
    """List all active games."""
    return jsonify({"games": [{"id": game_id} for game_id in games.keys()]})


@app.route("/api/game/<game_id>", methods=["DELETE"])
def delete_game(game_id):
    """Delete a game."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    del games[game_id]
    return jsonify({"message": "Game deleted successfully"})


@app.route("/api/game/<game_id>/explosions", methods=["GET"])
def get_explosion_count(game_id):
    """Get the number of explosions for a specific game."""
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    return jsonify({"explosions": games[game_id].nb_explosions, "game_id": game_id})


@app.route("/api/explosions", methods=["GET"])
def get_all_explosion_stats():
    """Get explosion statistics for all active games."""
    stats = {
        "total_explosions": sum(game.nb_explosions for game in games.values()),
        "average_explosions": (
            sum(game.nb_explosions for game in games.values()) / len(games)
            if games
            else 0
        ),
        "games": {
            game_id: {"explosions": game.nb_explosions, "solver_type": game.solver_type}
            for game_id, game in games.items()
        },
    }

    return jsonify(stats)


# Add a simple health check endpoint
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})


# Add a preflight handler for OPTIONS requests
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
