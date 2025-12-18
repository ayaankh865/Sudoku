# Sudoku Solver and Generator using CSP

This project implements a **Sudoku Solver and Generator** using **Constraint Satisfaction Problem (CSP)** techniques.

The solver applies:
- Backtracking search  
- Minimum Remaining Values (MRV) heuristic  
- Forward checking for constraint propagation  

The generator creates Sudoku puzzles with a **unique solution** at different difficulty levels.

---

## Features
- Solve user-input 9×9 Sudoku puzzles  
- Generate Sudoku puzzles (`easy`, `medium`, `hard`)  
- MRV heuristic for variable selection  
- Forward checking to reduce search space  
- Execution time and step count measurement  
- Export solved Sudoku to a CSV file  

---

## Technologies Used
- Python 3  
- Standard Python libraries (`time`, `random`, `copy`, `csv`, `os`)  

---

## How to Run
1. Ensure Python 3 is installed  
2. Open a terminal in the project directory  
3. Run:

```bash
python main.py
```
---

## Usage
- Select `solver` to input and solve a Sudoku puzzle
- Select `generator` to generate a new Sudoku puzzle
- Option to export the solved puzzle as a CSV file

## Algorithm Used
- Constraint Satisfaction Problem (CSP)
- Backtracking search
- Minimum Remaining Values (MRV) heuristic
- Forward checking

## Output
- Solved Sudoku displayed in the terminal
- Optional CSV file containing the solution

## Author
Khan