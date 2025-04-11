import os
import random
import json
from collections import Counter, defaultdict
import itertools
import math
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
import openai
from dotenv import load_dotenv
from .solver_lib import get_feedback, filter_valid_words

# Load OpenAI API key from environment
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@dataclass
class WordleConstraints:
    """Class to store Wordle game constraints"""
    green: Dict[int, str] = field(default_factory=dict)  # Correct letter in correct position
    yellow: Dict[int, str] = field(default_factory=dict)  # Correct letter in wrong position
    grey: Set[str] = field(default_factory=set)  # Letters not in the word
    min_letter_counts: Dict[str, int] = field(default_factory=dict)
    
    def __str__(self):
        return f"Green: {self.green}, Yellow: {self.yellow}, Grey: {self.grey}, Min counts: {self.min_letter_counts}"


class LanguageAgent:
    """LLM-based agent for strategic word selection"""
    def __init__(self, model_name="gpt-4o-mini", api_key=None):
        self.model_name = model_name
        self.client = openai.OpenAI(api_key=api_key)
        self.past_guesses = []
        self.last_explanation = None
    
    def _calculate_entropy(self, word_list):
        total = len(word_list)
        if total == 0:
            return 0
        return math.log2(total)

    def _calculate_information_gain(self, word, word_candidates):
        if not word or not word_candidates:
            return 0.0
        
        initial_entropy = self._calculate_entropy(word_candidates)
        
        feedback_groups = defaultdict(list)
        
        for potential_target in word_candidates:
            feedback = self.generate_feedback(word, potential_target)
            feedback_key = tuple(feedback)  # Convert list to hashable tuple
            feedback_groups[feedback_key].append(potential_target)
        
        # Calculate expected entropy after guess
        expected_entropy = 0.0
        total = len(word_candidates)
        
        for feedback, group in feedback_groups.items():
            probability = len(group) / total
            group_entropy = self._calculate_entropy(group)
            expected_entropy += probability * group_entropy
        
        # Information gain = reduction in entropy
        information_gain = initial_entropy - expected_entropy
        return round(information_gain, 3)
    
    def generate_feedback(self, guess, target_word):
        """Generate feedback for a guess in Wordle format"""
        if len(guess) != len(target_word):
            return None
        
        # Count letters in target word for proper yellow handling
        target_letter_counts = {}
        for letter in target_word:
            target_letter_counts[letter] = target_letter_counts.get(letter, 0) + 1
        
        # First pass: Mark green matches and decrement counts
        feedback = [''] * len(guess)
        for i, (g, t) in enumerate(zip(guess, target_word)):
            if g == t:
                feedback[i] = 'G'
                target_letter_counts[g] -= 1
        
        # Second pass: Mark yellow and grey
        for i, (g, f) in enumerate(zip(guess, feedback)):
            if f == '':  # Not marked green yet
                if g in target_letter_counts and target_letter_counts[g] > 0:
                    feedback[i] = 'Y'
                    target_letter_counts[g] -= 1
                else:
                    feedback[i] = 'B'
                    
        return feedback
    
    def _extract_word(self, content, candidates, word_length):
        """Extract a word from the LLM's response"""
        # Look for exact word matches
        for word in candidates:
            if word.lower() in content.lower():
                return word
        return candidates[0] if candidates else None
    
    def suggest_word(self, word_candidates, past_guesses=None):
        """Suggest the best word using the LLM with function calling"""
        if past_guesses is None:
            past_guesses = []

        if len(word_candidates) <= 1:
            return word_candidates[0] if word_candidates else None
            
        if len(word_candidates) <= 3:
            # For small candidate pools, calculate information gain directly
            best_word = word_candidates[0]
            best_gain = 0
            
            for word in word_candidates:
                gain = self._calculate_information_gain(word, word_candidates)
                if gain > best_gain:
                    best_gain = gain
                    best_word = word
            
            return best_word
        
        # For larger candidate pools, use LLM with function calling to suggest words
        word_length = len(word_candidates[0]) if word_candidates else 5
        
        # Define available functions for the LLM to call
        functions = [
            {
                "name": "explain_choice",
                "description": "Explain the reasoning behind choosing a particular word",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "The chosen word"
                        },
                        "explanation": {
                            "type": "string",
                            "description": "Detailed explanation of why this word is the best choice"
                        }
                    },
                    "required": ["word", "explanation"]
                }
            },
            {
                "name": "evaluate_information_gain",
                "description": "Calculate information gain for a potential guess",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "word": {
                            "type": "string",
                            "description": "Word to evaluate"
                        }
                    },
                    "required": ["word"]
                }
            },
            {
                "name": "analyze_letter_patterns",
                "description": "Analyze letter patterns and distribution in candidate words",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "candidates_count": {
                            "type": "integer",
                            "description": "Number of candidate words to analyze"
                        }
                    },
                    "required": ["candidates_count"]
                }
            }
        ]
        
        # Limit candidates list in prompt to avoid token limits
        display_candidates = word_candidates
        
        prompt = f"""
        You are a Wordle-solving assistant. Choose the best next word to guess.
        
        Current game state:
        - Previous guesses: {', '.join(past_guesses)}
        - Number of candidates: {len(word_candidates)}
        - Some possible candidates: {', '.join(display_candidates)}
        
        Choose the word that would most effectively narrow down the possibilities.
        You can call functions to help analyze the candidates.
        Finally, call the explain_choice function with your final decision.
        """
        
        messages = [{"role": "system", "content": prompt}]
        
        # Track the interaction with the LLM to enable multiple function calls
        for _ in range(5):  # Limit the maximum number of iterations
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    functions=functions,
                    function_call="auto"
                )
                
                response_message = response.choices[0].message
                messages.append(response_message)
                
                # Handle function calls
                if hasattr(response_message, "function_call") and response_message.function_call:
                    function_name = response_message.function_call.name
                    function_args = json.loads(response_message.function_call.arguments)
                    
                    if function_name == "evaluate_information_gain":
                        word = function_args.get("word")
                        if word in word_candidates:
                            score = self._calculate_information_gain(word, word_candidates)
                            result = {"word": word, "info_gain": score}
                            messages.append({
                                "role": "function",
                                "name": function_name,
                                "content": json.dumps(result)
                            })
                        else:
                            messages.append({
                                "role": "function",
                                "name": function_name,
                                "content": json.dumps({"error": f"Word '{word}' not in candidates"})
                            })
                    
                    elif function_name == "analyze_letter_patterns":
                        letter_counts = {}
                        position_counts = [defaultdict(int) for _ in range(word_length)]
                        
                        # Analyze letter distributions
                        for word in word_candidates:
                            for i, letter in enumerate(word):
                                letter_counts[letter] = letter_counts.get(letter, 0) + 1
                                position_counts[i][letter] += 1
                        
                        result = {
                            "letter_frequency": {k: v for k, v in sorted(letter_counts.items(), key=lambda item: -item[1])},
                            "positional_analysis": [{k: v for k, v in sorted(pos.items(), key=lambda item: -item[1])} 
                                                   for pos in position_counts]
                        }
                        messages.append({
                            "role": "function",
                            "name": function_name,
                            "content": json.dumps(result)
                        })
                    
                    elif function_name == "explain_choice":
                        word = function_args.get("word")
                        explanation = function_args.get("explanation")
                        self.last_explanation = explanation
                        
                        # Verify the word is in candidates and return it
                        if word in word_candidates:
                            return word
                        else:
                            # If the suggested word is not in candidates, inform the LLM
                            messages.append({
                                "role": "function",
                                "name": function_name,
                                "content": json.dumps({"error": f"Word '{word}' not in candidates. Please select from valid candidates."})
                            })
                else:
                    # If no function call, check if the message contains a word suggestion
                    suggestion = self._extract_word(response_message.content, word_candidates, word_length)
                    if suggestion:
                        self.last_explanation = response_message.content
                        return suggestion
            
            except Exception as e:
                print(f"Error with LLM suggestion: {e}")
                break
        
        # Fallback: return a random word from candidates
        return random.choice(word_candidates)


def solve_wordle_hybrid(valid_words, target_word, max_attempts=6, print_output=False):
    """
    Main function to solve wordle using a hybrid CSP+LLM approach
    
    Args:
        valid_words: list of valid words (as integer tuples)
        target_word: target word to guess
        max_attempts: maximum number of attempts
        print_output: whether to print debug info
    
    Returns:
        Dictionary with guesses, feedback, and number of possible words
    """
    # Initialize
    target_as_int = [ord(c) - ord('a') for c in target_word]
    
    # Convert valid_words to strings for the LLM agent
    valid_words_str = [''.join([chr(c + ord('a')) for c in word]) for word in valid_words]
    
    # Set up response structure
    response = {
        "guesses": [],
        "feedback": [],
        "nb_possible_words": [],
        "explanations": []
    }
    
    # Initialize LLM agent with OpenAI API key
    language_agent = LanguageAgent(api_key=OPENAI_API_KEY)
    past_guesses = []
    
    # Good starting words for efficient solving
    if len(valid_words) > 1000 and len(valid_words[0]) == 5:  # First guess for large dictionaries
        first_guess = "crane"  # Good starting word with common letters
        first_guess_int = tuple([ord(c) - ord('a') for c in first_guess])
        
        # Add to response
        feedback = get_feedback(first_guess_int, target_as_int)
        response["guesses"].append(first_guess)
        response["feedback"].append(feedback)
        response["nb_possible_words"].append(len(valid_words))
        response["explanations"].append("Common starting word with high-frequency letters")
        
        # Update valid words
        valid_words = filter_valid_words(valid_words, first_guess_int, feedback)
        valid_words_str = [''.join([chr(c + ord('a')) for c in word]) for word in valid_words]
        past_guesses.append(first_guess)
        
        if feedback == ['G'] * 5:
            if print_output:
                print(f"Solved {target_word} in 1 attempt!")
            return response
    
    # Main solving loop
    for attempt in range(len(past_guesses), max_attempts):
        if print_output:
            print(f"Attempt {attempt+1}, {len(valid_words)} possible words")
        
        # Get suggestion from LLM
        suggestion_str = language_agent.suggest_word(valid_words_str, past_guesses)
        suggestion_int = tuple([ord(c) - ord('a') for c in suggestion_str])
        
        # Get feedback
        feedback = get_feedback(suggestion_int, target_as_int)
        
        # Update response
        response["guesses"].append(suggestion_str)
        response["feedback"].append(feedback)
        response["nb_possible_words"].append(len(valid_words))
        response["explanations"].append(language_agent.last_explanation or "")
        past_guesses.append(suggestion_str)
        
        if print_output:
            print(f"Guess: {suggestion_str}, Feedback: {feedback}")
        
        if feedback == ['G'] * 5:
            if print_output:
                print(f"Solved {target_word} in {attempt+1} attempts!")
            return response

        if all(letter == 'G' for letter in feedback):
            if print_output:
                print(f"Solved {target_word} in {attempt+1} attempts!")
            return response
        
        # Filter valid words
        valid_words = filter_valid_words(valid_words, suggestion_int, feedback)
        valid_words_str = [''.join([chr(c + ord('a')) for c in word]) for word in valid_words]
        
        if not valid_words:
            break
    
    if print_output:
        print(f"Failed to solve {target_word} in {max_attempts} attempts.")
    
    return response 