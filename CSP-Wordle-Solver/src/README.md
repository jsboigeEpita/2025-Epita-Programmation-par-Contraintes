# CSP-Wordle-Solver

A hybrid Wordle solver using Constraint Satisfaction Programming (CSP) and Large Language Models (LLM).

## Features

- **CSP Solver**: Uses constraint satisfaction programming to solve Wordle puzzles efficiently
- **Hybrid LLM+CSP Solver**: Combines CSP with OpenAI's LLM for more intelligent word selection
- **Interactive Web Interface**: Play Wordle and watch AI solve it step-by-step
- **Explanation Mode**: See the reasoning behind each word selection in the hybrid mode

## Project Structure

```
CSP-Wordle-Solver/
├── src/
│   ├── backend/           # Flask API server
│   │   ├── api.py         # Main API endpoints
│   │   ├── wordle_solver/ # Solver implementations
│   │   │   ├── solver_lib.py    # Base CSP solver
│   │   │   ├── hybrid_solver.py # Hybrid CSP+LLM solver
│   │   │   └── words_alpha.txt  # Dictionary of words
│   └── frontend/          # Vue.js frontend
│       ├── src/
│       │   ├── App.vue    # Main application component
│       │   └── components/
│       │       └── WordleBoard.vue # Wordle board component
```

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:

   ```
   cd src/backend
   ```

2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up OpenAI API key:

   - Copy the `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file

4. Run the Flask API server:
   ```
   python api.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:

   ```
   cd src/frontend
   ```

2. Install dependencies:

   ```
   npm install
   ```

3. Run the development server:

   ```
   npm run serve
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```

## How to Play

1. Click "New Game" to start a new Wordle game
2. Choose either:
   - "Solve with CSP" to watch the basic solver in action
   - "Solve with CSP+LLM" to see the hybrid model with explanations
3. Click "Next Move" to step through the solution process

## Technologies Used

- **Backend**:

  - Python
  - Flask
  - OR-Tools (for CSP)
  - OpenAI API

- **Frontend**:
  - Vue.js
  - Axios

## Contacts

leon.ayral@epita.fr\
gabriel.calvente@epita.fr\
cedric.damais@epita.fr\
yacine.benihaddadene@epita.fr

## License

MIT
