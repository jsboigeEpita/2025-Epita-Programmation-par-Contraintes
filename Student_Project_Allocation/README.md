# Student Project Allocation System (Subject 28)

A constraint satisfaction-based system for optimally allocating students to projects based on preferences and constraints.

## Overview

This project implements a solution to the Student Project Allocation (SPA) problem using multiple algorithms and constraint programming approaches. It helps match students to projects while considering:

- Student preferences (ranked choices)
- Project capacities
- Overall satisfaction optimization

## Features

- Multiple allocation algorithms:
  - CP-SAT (Constraint Programming with SAT solver)
  - Greedy approach
  - Random allocation with optimization
- Benchmarking system to compare algorithm performance
- Interactive chatbot interface for easy usage
- Visualization of allocations using network graphs
- Detailed metrics on preference satisfaction

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY=your_key_here
```

## Usage

Run the interactive interface in the Student_Project_Allocation folder:
```bash
streamlit run chatbot_ui.py
```

The system will:
1. Accept student preferences and project details
2. Run multiple allocation algorithms
3. Compare and select the best solution
4. Provide detailed analysis of the allocation
5. Visualize the results

## Core Components

- `main.py`: Core allocation algorithms and logic
- `tool.py`: AI tools and visualization functions
- `chatbot_ui.py`: Streamlit-based user interface

## Algorithm Details

We implemented three different allocation algorithms to compare their effectiveness:

#### CP-SAT (Constraint Programming with SAT solver)
- Uses Google OR-Tools' CP-SAT solver for finding optimal solutions
- Models the problem with binary decision variables for each student-project pair
- Implements hard constraints for project capacities and preferences
- Uses an objective function that prioritizes higher preference rankings
- Advantage: Finds optimal solutions with respect to preference satisfaction
- Disadvantage: Can be computationally expensive for large problem instances

#### Greedy Algorithm
- Assigns students in order of preference list length (students with fewer options first)
- Makes locally optimal decisions without backtracking
- Advantage: Very fast execution time
- Disadvantage: May not find optimal global solutions

#### Random Algorithm with Optimization
- Generates multiple random allocations (up to 1000 iterations)
- Keeps track of the best allocation based on preference satisfaction
- Advantage: Can find good solutions when constraints are complex
- Disadvantage: Non-deterministic, results may vary between runs

## Solution Metrics

The system evaluates solutions based on:
- Preference satisfaction rates
- Individual student preference ranks
- Distribution of allocations
- Algorithm execution time
- Solution feasibility

## User Interface

We created a Streamlit-based chat interface that:
- Accepts user input in natural language
- Extracts problem parameters using LLM
- Runs the allocation algorithms and benchmarking
- Presents results in a user-friendly format
- Generates visualizations of allocations

## Conclusions

Our multi-algorithm approach to the Student Project Allocation problem demonstrates:

1. The effectiveness of constraint programming for finding optimal allocations
2. The trade-offs between solution quality and computational efficiency
3. The importance of benchmarking to select the most appropriate algorithm for a given problem instance

The system successfully balances:
- Student preference satisfaction
- Project capacity constraints
- Computational efficiency


## Future Improvements

Potential enhancements for future versions:
- Support for supervisor preferences and workload balancing
- Dynamic constraint generation from natural language
- Improved visualization options for larger allocation problems

## References

Based on research in:
- Gent et al.'s work on Stable Marriage as CSP
- University of Glasgow's SPA-P (Student-Project Allocation) studies
- Constraint programming approaches to matching problems

## Made by

- [Enguerrand Turcat](mailto:enguerrand.turcat@epita.fr)
- [Matthew Banawa](matthew.banawa@epita.fr)
- [Verhille Titouan](mailto:titouan.verhille@epita.fr)
