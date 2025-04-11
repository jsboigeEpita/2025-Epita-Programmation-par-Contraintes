from flask import Flask, jsonify, request
from flask_cors import CORS
from wordle_solver import solver_lib
from wordle_solver import hybrid_solver
import pandas as pd
import random
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for Vue.js frontend

total_words = pd.read_fwf("wordle_solver/words_alpha.txt", names=["words"])
words = total_words[total_words["words"].str.len() == 5]
words_data = [tuple([ord(c) - ord('a') for c in word]) for word in words["words"]]

current_game = {
    "target_word": None,
    "guesses": [],
    "feedback": []
}

@app.route('/new-game', methods=['POST'])
def new_game():
    current_game["target_word"] = solver_lib.choose_target(words["words"].tolist())
    current_game["guesses"] = []
    current_game["feedback"] = []
    return jsonify(current_game)

@app.route('/solver-guess', methods=['GET'])
def get_solver_guess():
    response = solver_lib.solve_wordle(
        valid_words=words_data,
        target_word=current_game["target_word"],
        max_attempts=6,
        print_output=False
    )
    return jsonify({
        "guesses": response["guesses"],
        "feedback": response["feedback"],
        "nb_possible_words": response["nb_possible_words"],
    })

@app.route('/hybrid-solver', methods=['GET'])
def get_hybrid_solver_guess():
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({
            "error": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        }), 500
    
    response = hybrid_solver.solve_wordle_hybrid(
        valid_words=words_data,
        target_word=current_game["target_word"],
        max_attempts=6,
        print_output=False
    )
    return jsonify({
        "guesses": response["guesses"],
        "feedback": response["feedback"],
        "nb_possible_words": response["nb_possible_words"],
        "explanations": response["explanations"]
    })

@app.route('/user-guess', methods=['POST'])
def process_user_guess():
    data = request.json
    guess = data.get('guess', '').lower()
    
    # Validate the guess
    if len(guess) != 5 or guess not in words["words"].tolist():
        return jsonify({"error": "Invalid guess. Must be a valid 5-letter word"}), 400
    
    # Get feedback for this guess
    feedback = solver_lib.get_feedback(
        tuple([ord(c) - ord('a') for c in guess]), 
        [ord(c) - ord('a') for c in current_game["target_word"]]
    )
    
    # Store the guess and feedback
    current_game["guesses"].append(guess)
    current_game["feedback"].append(feedback)
    
    # Calculate remaining possible words
    valid_words_int = words_data.copy()
    for g, f in zip(current_game["guesses"], current_game["feedback"]):
        g_int = tuple([ord(c) - ord('a') for c in g])
        valid_words_int = solver_lib.filter_valid_words(valid_words_int, g_int, f)
    
    return jsonify({
        "guess": guess,
        "feedback": feedback,
        "possible_words_count": len(valid_words_int),
        "solved": ''.join(feedback) == 'GGGGG'
    })

if __name__ == '__main__':
    app.run(port=5000)