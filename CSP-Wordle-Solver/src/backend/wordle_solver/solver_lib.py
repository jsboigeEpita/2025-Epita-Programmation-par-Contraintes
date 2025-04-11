# import pandas as pd
import itertools
from collections import Counter
from collections import defaultdict
from ortools.sat.python import cp_model
import random


# positional_freq = [defaultdict(int) for _ in range(5)]
# for word in words_data:
#     for pos in range(5):
#         char = word[pos]
#         positional_freq[pos][char] += 1

# letter_frequency = Counter(itertools.chain.from_iterable(words_data))

# total_words = len(words_data)
# for char, freq in letter_frequency.items():
#     letter_frequency[char] = freq / total_words

# for pos in range(5):
#     total_pos = sum(positional_freq[pos].values())
#     for char, freq in positional_freq[pos].items():
#         positional_freq[pos][char] = freq / total_pos


def choose_target(words_data):
    """
    Choose a target word from the list of words
    """
    return random.choice(words_data)

def get_feedback(guess, target):
    """
    Get the feedback for a given guess and target word and checks duplicate letters
    (G: green, B: black, Y: yellow)
    
    Example:
        guess = "leave"
        target = "place"
        returns : ['Y', 'B', 'G', 'B', 'G']
    """
    feedback = []
    target_counts = Counter(target)
    for g_char, t_char in zip(guess, target):
        if g_char == t_char:
            feedback.append('G')
            target_counts[g_char] -= 1
        else:
            feedback.append('B')

    for pos, (g_char, t_char) in enumerate(zip(guess, target)):
        if feedback[pos] == 'B' and g_char in target_counts and target_counts[g_char] > 0:
            feedback[pos] = 'Y'
            target_counts[g_char] -= 1
    return feedback


def update_model(model, position_vars, guess, feedback):
    """
    Update the model using the new feedback
    """
    letter_counts = defaultdict(int)    # Key: letter, Value: count
    gray_positions = defaultdict(list)  # Key: letter, Value: list of positions

    for pos in range(5):
        char = guess[pos]
        fb = feedback[pos]
        if fb == 'G':
            model.Add(position_vars[pos] == char)
            letter_counts[char] += 1
        elif fb == 'Y':
            model.Add(position_vars[pos] != char)
            letter_counts[char] += 1
        elif fb == 'B':
            # Track gray letters for their specific positions
            gray_positions[char].append(pos)

    for char, positions in gray_positions.items():
        for pos in positions:
            model.Add(position_vars[pos] != char)

    for char, count in letter_counts.items():
        occurs = [model.NewBoolVar(f'occurs_{p}_{char}') for p in range(5)]
        for p in range(5):
            if p not in gray_positions.get(char, []):  # Skip gray positions
                model.Add(position_vars[p] == char).OnlyEnforceIf(occurs[p])
                model.Add(position_vars[p] != char).OnlyEnforceIf(occurs[p].Not())
        model.Add(sum(occurs) >= count)
    

def update_heuristic(model, position_vars, positional_freq, letter_frequency):
    """
    Update the heuristic function to maximize for the model
    """
    c_pos_freq = 1000
    c_letter_freq = 2000
    c_dup = 500

    objective = []
    for pos in range(5):
        char_var = position_vars[pos]
        for char in range(26):
            is_char = model.NewBoolVar(f'pos_{pos}_char_{char}')
            model.Add(char_var == char).OnlyEnforceIf(is_char)
            model.Add(char_var != char).OnlyEnforceIf(is_char.Not())
            
            score = int(c_pos_freq * positional_freq[pos][char] + c_letter_freq * letter_frequency[char])
            objective.append(is_char * score)
                
    num_duplicates = model.NewIntVar(0, 25, 'num_duplicates')
    char_counts = []
    for char in range(26):
        count = sum([model.NewBoolVar(f'pos_{i}_char_{char}') for i in range(5)])
        for i, pos_var in enumerate(position_vars):
            is_char = model.NewBoolVar(f'pos_{i}_is_char_{char}')
            model.Add(pos_var == char).OnlyEnforceIf(is_char)
            model.Add(pos_var != char).OnlyEnforceIf(is_char.Not())
            count += is_char
        char_counts.append(count)

    duplicates = []
    for count in char_counts:
        is_duplicate = model.NewBoolVar(f'is_duplicate_{count}')
        model.Add(count > 1).OnlyEnforceIf(is_duplicate)
        model.Add(count <= 1).OnlyEnforceIf(is_duplicate.Not())
        duplicates.append(is_duplicate)

    model.Add(num_duplicates == sum(duplicates))

    objective.append(-c_dup * num_duplicates)

    model.Maximize(sum(objective))


def list_constraints(model):
    """
    Helper function to list all constraints in the model
    """
    model_proto = model.Proto()
    for i, ct in enumerate(model_proto.constraints):
        print(f"Constraint {i}: {ct}")


def filter_valid_words(words_data, guess, feedback):
    """
    Filter all the valid words based on the guess and feedback
    """
    valid = []
    for word in words_data:
        valid_word = True
        for pos in range(5):
            if feedback[pos] == 'G' and word[pos] != guess[pos]:
                valid_word = False
                break
        if not valid_word:
            continue

        for pos in range(5):
            if feedback[pos] == 'Y':
                if word[pos] == guess[pos] or guess[pos] not in word:
                    valid_word = False
                    break
        if not valid_word:
            continue
        
        gray_chars = [guess[pos] for pos in range(5) if feedback[pos] == 'B']
        for char in gray_chars:
            if char in word and char not in [guess[p] for p in range(5) if feedback[p] in ('G', 'Y')]:
                valid_word = False
                break

        if valid_word:
            valid.append(word)
    return valid


def solve_wordle(valid_words, target_word, max_attempts=6, print_output=True):
    """
    Main function to initialize and run the solver

    Args:
        words_data: list of words to use for the solver
        target_word: the word to solve
        max_attempts: the maximum number of attempts to solve the word
        print_output: whether to print the output of each attempt

    Returns:
        return the response object with the guesses, feedback, and number of possible words
    """

    # Initialize the model and the valid words
    target_as_int = [ord(c) - ord('a') for c in target_word]
    # valid_words = words_data.copy()  # Use a copy to avoid modifying the original

    positional_freq = [defaultdict(int) for _ in range(5)]
    for word in valid_words:
        for pos in range(5):
            char = word[pos]
            positional_freq[pos][char] += 1

    letter_frequency = Counter(itertools.chain.from_iterable(valid_words))

    total_words = len(valid_words)
    for char, freq in letter_frequency.items():
        letter_frequency[char] = freq / total_words

    for pos in range(5):
        total_pos = sum(positional_freq[pos].values())
        for char, freq in positional_freq[pos].items():
            positional_freq[pos][char] = freq / total_pos


    # Initialize the model and the variables for our model
    model = cp_model.CpModel()
    position_vars = [model.NewIntVar(0, 25, f'pos_{i}') for i in range(5)]
    status_dict = {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN"
    }
    response = {
        "guesses": [],
        "feedback": [],
        "nb_possible_words": []
    }
    
    for attempt in range(max_attempts):
        if print_output:
            print(f"Length of possible words: {len(valid_words)}")
            print(f"Is {target_word} in the dataset? {tuple(target_as_int) in valid_words}")

        # Reduce the list of all possible words 
        model.AddAllowedAssignments(position_vars, valid_words)

        # Initialize / update the heuristic function
        update_heuristic(model, position_vars, positional_freq, letter_frequency)

        # Initialize and run the solver
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        if print_output:
            print(f"status = {status_dict.get(status, 'UNKNOWN')}")

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            # Extract the guess and feedback
            guess = tuple([solver.Value(pos) for pos in position_vars])
            valid_words.remove(guess)
            guess_str = ''.join([chr(c + ord('a')) for c in guess])
            feedback = get_feedback(guess, target_as_int)

            response["guesses"].append(guess_str)
            response["nb_possible_words"].append(len(valid_words))
            response["feedback"].append(feedback)

            if print_output:
                print(f"\nAttempt {attempt+1}: {guess_str} → {feedback}")
            
            if feedback == ['G'] * 5:
                print(f"Solved {target_word} in {attempt+1} attempts!")
                return response
            
            # Remove invalid words and update the model
            valid_words = filter_valid_words(valid_words, guess, feedback)
            update_model(model, position_vars, guess, feedback)
        
        else:
            print("Model is infeasible. Exiting.")
            return response
        
    print(f"Failed to solve {target_word} in {max_attempts} attempts.")
    return response
