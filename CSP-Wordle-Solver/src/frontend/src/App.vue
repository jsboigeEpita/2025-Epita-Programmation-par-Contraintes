<template>
  <div id="app" style="text-align: center">
    <h1>AI Wordle Solver</h1>
    <div class="button-container">
      <button @click="startNewGame" class="btn">New Game</button>
      <button @click="solve('csp')" :disabled="solved || loading" class="btn">
        Solve with CSP
      </button>
      <button @click="solve('hybrid')" :disabled="solved || loading" class="btn">
        Solve with CSP+LLM
      </button>
      <button @click="nextSolverStep" :disabled="move >= guesses.length || guesses.length === 0" class="btn">Next Move</button>
    </div>

    <div v-if="loading" class="spinner"></div>
    <div v-if="error" class="error">{{ error }}</div>

    <div v-if="targetWord" class="target-word">Word to guess: {{ targetWord }}</div>
    <div v-if="isSolved" class="result">
      Solved {{ targetWord }} in {{ guesses.length }} attempts!
    </div>
    
    <WordleBoard
      :guesses="guesses"
      :feedback="feedback"
      :nbPossibleWords="nbPossibleWords"
      :explanations="explanations"
      :move="move"
    />
  </div>
</template>

<script>
import axios from "axios";
import WordleBoard from "./components/WordleBoard.vue";

export default {
  components: { WordleBoard },
  data() {
    return {
      targetWord: "",
      guesses: [],
      feedback: [],
      explanations: [],
      solved: false,
      nbPossibleWords: [],
      move: 0,
      loading: false,
      error: null,
    };
  },
  computed: {
    isSolved() {
      // Computing solved state from actual feedback data
      return this.feedback.length > 0 && 
        this.move > 0 &&
        this.move === this.feedback.length && 
        this.feedback[this.feedback.length - 1].every(f => f === 'G');
    }
  },
  methods: {
    async startNewGame() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.post("http://127.0.0.1:5000/new-game");
        this.targetWord = response.data.target_word;
        this.guesses = [];
        this.feedback = [];
        this.explanations = [];
        this.nbPossibleWords = [];
        this.solved = false;
        this.move = 0;
      } catch (error) {
        this.error = "Error starting new game: " + (error.response?.data?.error || error.message);
      } finally {
        this.loading = false;
      }
    },
    async solve(method) {
      if (!this.targetWord) {
        this.error = "Please start a new game first";
        return;
      }
      
      this.loading = true;
      this.error = null;
      this.move = 0; // Reset move counter before starting new solution
      
      try {
        const endpoint = method === 'hybrid' ? 'hybrid-solver' : 'solver-guess';
        const response = await axios.get(`http://127.0.0.1:5000/${endpoint}`);
        
        if (response.data.guesses && response.data.guesses.length > 0) {
          this.guesses = response.data.guesses;
          this.feedback = response.data.feedback;
          this.nbPossibleWords = response.data.nb_possible_words;
          
          // Check if explanations are available (for hybrid solver)
          if (response.data.explanations) {
            this.explanations = response.data.explanations;
          } else {
            this.explanations = new Array(this.guesses.length).fill("");
          }
          
          this.solved = false; // Reset solved state, will be computed by the computed property
          this.move = 0; // Start at 0 so first click of Next Move shows the first guess
        } else {
          this.error = "No guesses returned from the solver";
        }
      } catch (error) {
        if (error.response?.status === 500 && error.response?.data?.error) {
          this.error = error.response.data.error;
        } else {
          this.error = "Error solving the game: " + error.message;
        }
      } finally {
        this.loading = false;
      }
    },
    nextSolverStep() {
      if (this.move < this.guesses.length) {
        this.move++;
        console.log(`Moved to step ${this.move} of ${this.guesses.length}`);
      }
    },
    submitGuess() {
      // For future implementation - allow user to make manual guesses
    },
  },
};
</script>

<style>
.button-container {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  background-color: #4285f4;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #3367d6;
}

.btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.spinner {
  border: 8px solid #f3f3f3;
  border-top: 8px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error {
  color: #d32f2f;
  margin: 15px;
  padding: 10px;
  border: 1px solid #d32f2f;
  border-radius: 4px;
  background-color: #ffebee;
}

.result {
  margin: 20px;
  padding: 10px;
  font-weight: bold;
  color: #388e3c;
  font-size: 1.2em;
}

.target-word {
  margin: 15px;
  font-style: italic;
}
</style>
