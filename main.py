#!/usr/bin/env python3
import time
import random
import csv
import sys
import copy
import os

def print_grid(grid):
    """Print the Sudoku grid in a readable format."""
    for row in grid:
        print(" ".join(str(num) if num != 0 else '.' for num in row))

def parse_grid_input():
    """
    Prompt user to  9 rows of Sudoku, each 9 chars (digits or '.') 
    and return a 9x9 grid as list of lists of ints (0 for blanks).
    """
    print("Enter the Sudoku puzzle row by row (use digits 1-9, and . for empty):")
    grid = []
    for i in range(9):
        while True:
            line = input(f"Row {i+1}: ").strip()
            # Allow either a continuous 9-char string or space-separated
            line = line.replace(" ", "")
            if len(line) == 9 and all(c.isdigit() or c == '.' for c in line):
                break
            print("Invalid format. Enter exactly 9 characters (digits or .).")
        row = [(int(c) if c.isdigit() else 0) for c in line]
        grid.append(row)
    return grid

def get_empty_domains(grid):
    """
    Compute initial domains for all empty cells in the grid.
    Domains[(r,c)] is the set of possible digits for cell (r,c).
    """
    global domains
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                # Candidate values 1-9 minus those in same row, col, box
                used = set(grid[r])  # in row
                used |= {grid[i][c] for i in range(9)}  # in column
                br, bc = 3*(r//3), 3*(c//3)
                for i in range(br, br+3):
                    for j in range(bc, bc+3):
                        used.add(grid[i][j])
                domains[(r,c)] = {n for n in range(1,10) if n not in used}
    return domains

def forward_check(domains, var, value):
    """
    Apply forward checking: after assigning 'value' to cell 'var', remove
    that value from the domains of all neighbors of 'var'. Return False if
    any domain becomes empty (conflict), else True.
    """
    r, c = var
    peers = []
    # Row and column peers
    for i in range(9):
        if i != c and (r,i) in domains:
            peers.append((r,i))
        if i != r and (i,c) in domains:
            peers.append((i,c))
    # Box peers
    br, bc = 3*(r//3), 3*(c//3)
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if (i,j) != (r,c) and (i,j) in domains:
                peers.append((i,j))
    # Remove the assigned value from neighbors' domains
    for peer in peers:
        if value in domains.get(peer, {}):
            domains[peer].remove(value)
            if not domains[peer]:
                return False  # domain wiped out -> failure
    return True

def solve_sudoku(grid):
    """
    Solve the Sudoku puzzle using backtracking with MRV and forward-checking.
    Returns (solved_grid, steps) or (None, steps) if unsolvable.
    """
    domains = get_empty_domains(grid)
    # Global step counter (wrapped in a list to allow modification in nested scope)
    steps = [0]

    def backtrack():
        steps[0] += 1  # count this recursive call
        # If no unassigned vars, puzzle solved
        nonlocal domains
        if not domains:
            return True
        # MRV heuristic: pick the cell with fewest legal values
        var = min(domains, key=lambda v: len(domains[v]))
        choices = domains[var].copy()
        # If any domain is empty, backtrack
        if not choices:
            return False
        # Save and remove var from domains (we'll re-add on backtrack if needed)
        saved_domains = domains.copy()
        del domains[var]
        r, c = var
        for val in choices:
            # Assign value
            original_row, original_col = grid[r][c], grid[r][c]
            grid[r][c] = val
            # Make a deep copy of domains for this branch
            new_domains = copy.deepcopy(domains)
            # Forward check: prune neighbors' domains
            if forward_check(new_domains, var, val):
                # Continue with pruned domains
                domains_backup = domains
                domains = new_domains
                if backtrack():#recursive call
                    return True
                domains = domains_backup
            # Undo assignment on failure
            grid[r][c] = 0
            # Restore domains from before trying this value
            domains = saved_domains.copy()
            del domains[var]  # var is still unassigned for next try
        # No value worked, put var back into domains and fail
        grid[r][c] = 0
        domains.clear()
        domains.update(saved_domains)
        return False

    # Start the search
    success = backtrack()
    return (grid if success else None, steps[0])

def count_solutions(grid, limit=2):
    """
    Count up to 'limit' solutions of the Sudoku. Uses a simple backtracking.
    Stop early if count reaches limit. Return number of solutions found (<= limit).
    """
    count = [0]
    domains = get_empty_domains(grid)

    def backtrack():
        # If already found enough solutions, stop
        nonlocal domains
        if count[0] >= limit:
            return True
        if not domains:
            count[0] += 1
            return False  # found one solution; continue to find more
        var = min(domains, key=lambda v: len(domains[v]))
        choices = domains[var].copy()
        if not choices:
            return False
        saved_domains = domains.copy()
        del domains[var]
        r, c = var
        for val in choices:
            grid[r][c] = val
            new_domains = copy.deepcopy(domains)
            if forward_check(new_domains, var, val):
                domains_backup = domains
                domains = new_domains
                stop = backtrack()
                domains = domains_backup
                if stop:
                    grid[r][c] = 0
                    domains.clear()
                    domains.update(saved_domains)
                    return True  # reached limit
            grid[r][c] = 0
            if count[0] >= limit:
                domains.clear()
                domains.update(saved_domains)
                return True
        # restore
        domains.clear()
        domains.update(saved_domains)
        grid[r][c] = 0
        return False

    backtrack()
    return count[0]

def generate_full_solution(grid):
    """
    Fill the grid completely with a valid Sudoku solution using backtracking
    with random value ordering.
    Uses recursion to fill the grid.
    """
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                random_vals = list(range(1,10))
                random.shuffle(random_vals)
                for val in random_vals:
                    # Check if valid to place
                    block_vals = {grid[i][j] 
                                  for i in range(3*(r//3),3*(r//3)+3)
                                  for j in range(3*(c//3),3*(c//3)+3)}
                    if (val not in grid[r] and
                        all(grid[i][c] != val for i in range(9)) and
                        val not in block_vals):
                        grid[r][c] = val
                        if generate_full_solution(grid):
                            return True
                        grid[r][c] = 0
                return False
    return True

def generate_sudoku(difficulty):
    """
    Generate a Sudoku puzzle at the given difficulty ('easy', 'medium', 'hard').
    Returns the puzzle grid (0 for blanks).
    """
    # 1. Generate a complete grid
    grid = [[0]*9 for _ in range(9)]
    generate_full_solution(grid)
    # 2. Remove clues while maintaining unique solution
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    # Determine target number of clues by difficulty
    if difficulty == 'easy':
        min_clues = 36
    elif difficulty == 'medium':
        min_clues = 30
    else:  # hard
        min_clues = 24
    removed = 0
    for (r, c) in cells:
        if sum(1 for i in range(9) for j in range(9) if grid[i][j] != 0) <= min_clues:
            break
        backup = grid[r][c]
        grid[r][c] = 0
        # Check uniqueness: count solutions up to 2
        sol_count = count_solutions([row[:] for row in grid], limit=2)
        if sol_count != 1:
            # Not unique, restore
            grid[r][c] = backup
        else:
            removed += 1
    return grid

def export_to_csv(grid, filename):
    """Export the solved grid to a CSV file, one row per line."""
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in grid:
                writer.writerow(row)
        print(f"Solution exported to {filename}")
    except Exception as e:
        print(f"Error writing CSV: {e}")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print("Sudoku - Solver and Generator (MRV + CSP)")
    choice = input("Type 'solver' to solve a puzzle or 'generator' to create one: ").strip().lower()
    if choice == 'solver':
        # Get puzzle input from user
        #grid is a list containing puzzle
        grid = parse_grid_input()
        print("\nSolving the puzzle...")
        start = time.time()
        solution, steps = solve_sudoku(grid)
        elapsed = time.time() - start
        if solution:
            print("\nSolved Sudoku:")
            print_grid(solution)
            print(f"Solved in {elapsed:.4f} seconds, with {steps} steps.")
            export = input("Export solution to CSV? (y/n): ").strip().lower()
            if export == 'y':
                fname = input("Enter CSV filename (e.g. solution.csv): ").strip()
                folder = input("Enter directory path (leave empty for current folder): ").strip()
                if folder:
                    filepath = os.path.join(folder, fname)
                else:
                    folder="Sudoku\Output"
                    filepath = os.path.join(folder, fname)
                export_to_csv(solution, filepath)
        else:
            print("No solution found for the given puzzle.")
    elif choice == 'generator':
        diff = input("Enter difficulty (easy, medium, hard): ").strip().lower()
        if diff not in ('easy', 'medium', 'hard'):
            print("Invalid difficulty. Using 'easy' by default.")
            diff = 'easy'
        print(f"\nGenerating a {diff} puzzle...")
        puzzle = generate_sudoku(diff)
        print("\nGenerated Sudoku (. = blank):")
        print_grid(puzzle)
        solve_it = input("Would you like to solve this puzzle? (y/n): ").strip().lower()
        if solve_it == 'y':
            print("\nSolving the generated puzzle...")
            start = time.time()
            solution, steps = solve_sudoku(puzzle)
            elapsed = time.time() - start
            if solution:
                print("\nSolution:")
                print_grid(solution)
                print(f"Solved in {elapsed:.4f} seconds, with {steps} steps.")
                export = input("Export solution to CSV? (y/n): ").strip().lower()
                if export == 'y':
                    fname = input("Enter CSV filename (e.g. solution.csv): ").strip()
                    folder = input("Enter directory path (leave empty for output folder): ").strip()
                    if folder:
                        filepath = os.path.join(folder, fname)
                    else:
                        folder="Sudoku\Output"
                        filepath = os.path.join(folder, fname)
                    export_to_csv(solution, filepath)
            else:
                print("Unexpected: generated puzzle has no solution!")
    else:
        print("Invalid option. Please select a valid option.")
        input("Press Enter to continue...")
        main()

if __name__ == "__main__":
    main()
