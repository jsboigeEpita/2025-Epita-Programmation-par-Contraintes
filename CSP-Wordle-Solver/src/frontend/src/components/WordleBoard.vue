<template>
  <div class="grid-wrapper">
    <div
      v-if="guesses.length > 0 && feedback.length > 0"
      class="grid-container"
    >
      <div v-for="(guess, index) in guesses" :key="index" class="guess-row">
        <div class="tiles-container">
          <div
            v-for="(letter, letterIndex) in guess"
            :key="letterIndex"
            class="letter-tile"
            :class="
              index < move ? feedbackClasses[index][letterIndex] : 'gray-tile'
            "
          >
            {{ index < move ? letter.toUpperCase() : " " }}
          </div>
        </div>
        <div class="possible-words-count">
          <span v-if="index < move">{{ nbPossibleWords[index] || "" }}</span>
        </div>
      </div>
      
      <!-- Explanation row (displayed after each guess when using hybrid solver) -->
      <div v-if="explanations.length > 0 && currentExplanation && move > 0" class="explanation-row">
        <div class="explanation-heading">LLM explanation for guess #{{ move }}:</div>
        <div class="explanation-content">{{ currentExplanation }}</div>
      </div>
    </div>
    <div v-else class="grid-container">
      <div v-for="i in 5" :key="i" class="guess-row">
        <div class="tiles-container">
          <div v-for="i in 5" :key="i" class="letter-tile gray-tile">
            {{ " " }}
          </div>
        </div>
        <div class="possible-words-count"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    guesses: Array,
    feedback: Array,
    nbPossibleWords: Array,
    explanations: {
      type: Array,
      default: () => []
    },
    move: Number,
  },
  computed: {
    feedbackClasses() {
      if (!this.feedback || this.feedback.length === 0) {
        return [];
      }
      
      return this.feedback.map((row) =>
        row.map((status) => ({
          "green-tile": status === "G",
          "yellow-tile": status === "Y",
          "gray-tile": status === "B",
        }))
      );
    },
    currentExplanation() {
      if (this.move > 0 && this.explanations && this.explanations.length > 0) {
        const moveIndex = this.move - 1;
        if (moveIndex < this.explanations.length) {
          return this.explanations[moveIndex] || "";
        }
      }
      return "";
    }
  },
};
</script>

<style>
.grid-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  margin-left: 100px;
}

.grid-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guess-row {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 20px;
}

.tiles-container {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 6px;
}

.letter-tile {
  width: 60px;
  height: 60px;
  border: 2px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2em;
  text-transform: uppercase;
}

.possible-words-count {
  min-width: 80px;
  font-weight: bold;
  color: black;
  text-align: left;
}

.green-tile {
  background-color: #6aaa64;
  color: white;
  border-color: #6aaa64;
}

.yellow-tile {
  background-color: #c9b458;
  color: white;
  border-color: #c9b458;
}

.gray-tile {
  background-color: #787c7e;
  color: white;
  border-color: #787c7e;
}

.explanation-row {
  margin-top: 20px;
  padding: 15px;
  border: 1px dashed #ccc;
  border-radius: 4px;
  background-color: #f9f9f9;
  max-width: 600px;
  text-align: left;
}

.explanation-heading {
  font-weight: bold;
  margin-bottom: 8px;
  color: #4285f4;
}

.explanation-content {
  line-height: 1.5;
  color: #666;
}
</style>
