from typing import Tuple, List, Any, Optional

ids = ["325281459, 324697549"]


def to_CNF(input) -> Tuple[list, List[List[Tuple[Any, bool]]]]:

    # parsing the input
    rectangle_size,fixed,pairs= input
    rectangle_length=rectangle_size[0]
    rectangle_width=rectangle_size[1]
    N=rectangle_width*rectangle_length #total grid size is N*N

    # Translating to CNF
    # Each variable is represented as a tuple (row, column, value)
    # At the begining, we create a list of all possible variables, we will reduce it afterwards
    variables = []
    for r in range(N):
        for c in range(N):
            for v in range(1, N + 1):
                variables.append((r, c, v))

    CNF_formula = []

    # A. Regular Sudoku constraints:
    # 1. Each cell contains exactly one number
    for r in range(N):
        for c in range(N):
            # 1.1 At least one number in each cell
            clause = []
            for v in range(1, N + 1):
                clause.append(((r, c, v), True)) # Reminder: or between clauses
            CNF_formula.append(clause)
            # 1.2 At most one number in each cell
            for v1 in range(1, N + 1):
                for v2 in range(v1 + 1, N + 1):
                    CNF_formula.append([((r, c, v1), False), ((r, c, v2), False)]) # not v1 or not v2 in (r,c)
    
    # 2. Each number appears exactly once in each row
    for r in range(N):
        for v in range(1, N + 1):
            for c1 in range(N):
                for c2 in range(c1 + 1, N):
                    CNF_formula.append([((r, c1, v), False), ((r, c2, v), False)]) # no v in (r,c1) or no v in (r,c2) -> v cannot apeear twice in row r
    
    # 3. Each number appears exactly once in each column
    for c in range(N):
        for v in range(1, N + 1):
            for r1 in range(N):
                for r2 in range(r1 + 1, N):
                    CNF_formula.append([((r1, c, v), False), ((r2, c, v), False)]) # no v in (r1,c) or no v in (r2,c) -> v cannot appear twice in column c

    # 4. each number appears exactly once in each rectangle
    num_rectangles_row = N // rectangle_length # rectangles per row (=rectangle_width)
    num_rectangles_col = N // rectangle_width # rectangles per column (=rectangle_length)
    for vr in range(num_rectangles_row):
        for vc in range(num_rectangles_col):
            for v in range(1, N + 1):
                cells = []
                for r in range(vr * rectangle_length, (vr + 1) * rectangle_length):
                    for c in range(vc * rectangle_width, (vc + 1) * rectangle_width):
                        cells.append((r, c))
                for i in range(len(cells)):
                    for j in range(i + 1, len(cells)):
                        r1, c1 = cells[i]
                        r2, c2 = cells[j]
                        CNF_formula.append([((r1, c1, v), False), ((r2, c2, v), False)]) # no v in (r1,c1) or no v in (r2,c2)

    # 5. Pre-assigned numbers
    for r, c, val in fixed:
        CNF_formula.append([((r, c, val), True)])

    # B. Additional constraints for the pairs 
    #6. neighboring cells with a given sum

    for r1, c1, r2, c2, target_sum in pairs:
        for v1 in range(1, N + 1):
            for v2 in range(1, N + 1):
                if v1 + v2 != target_sum: # Illegal!
                    CNF_formula.append([
                        ((r1, c1, v1), False), 
                        ((r2, c2, v2), False)
                    ])
    
    return variables, CNF_formula
        

def solve_SAT(
        variables: list,
        CNF_formula: List[List[Tuple[Any, bool]]],
        assignment: dict
) -> Tuple[bool, Optional[dict]]:
    # DPLL algorithm implementation
    curr_assignment = assignment.copy() 
    #Unit Propagation
    while True:
        new_unit_found = False
        all_satisfied = True # assumption
        
        for clause in CNF_formula:
            status, result = clause_status(clause, curr_assignment)
            if status == "conflict":
                return False, None # dead end
            if status == "unresolved":
                all_satisfied = False 
            if status == "unit":
                # This clause must be satisfied by assigning the only unassigned literal accordingly
                var, val = result
                curr_assignment[var] = val
                new_unit_found = True
                all_satisfied = False 
                break 

        if all_satisfied:
            return True, curr_assignment
            
        # Condition to stop: we've gone through everything, no conflicts, but no new unit found
        # Time to start guessing (:
        if not new_unit_found:
            break

    # If we got here it means that we need to choose a variable to guess
    # Choose the first unassigned variable
    for var in variables:
        if var not in curr_assignment:
            # Try both assignments (True and False)
            curr_assignment[var] = True
            is_satisfiable, result = solve_SAT(variables, CNF_formula, curr_assignment)
            if is_satisfiable:
                return True, result

            curr_assignment[var] = False
            is_satisfiable, result = solve_SAT(variables, CNF_formula, curr_assignment)
            if is_satisfiable:
                return True, result

            return False, None

    return False, None


def clause_status(
        clause: List[Tuple[Any, bool]],
        assignment: dict
) -> Tuple[str, Optional[Tuple[Any, bool]]]:
    unassigned_literal = []
    for literal, required_sign in clause:
        if literal in assignment:
            if assignment[literal] == required_sign:
                return "satisfied", None
        else:
            unassigned_literal.append((literal, required_sign))
    if len(unassigned_literal) == 0: # all literals are assigned but none satisfied the clause (otherwise we would have returned "satisfied" earlier)
        return "conflict", None
    elif len(unassigned_literal) == 1:
        return "unit", unassigned_literal[0] #only one unassigned literal, in order to satisfy the clause, this literal must be assigned accordingly
    else:
        return "unresolved", None # We don't have enought information to decide yet
        


def numbers_assignment(
        variables: list,
        assignment: dict,
        input: Any
) -> List[List[int]]:
    # parsing the input as in to_CNF function
    rectangle_size,_,_= input
    rectangle_length=rectangle_size[0]
    rectangle_width=rectangle_size[1]
    N=rectangle_width*rectangle_length #total grid size is N*N
    grid = [[0 for _ in range(N)] for _ in range(N)]
    for (row,col,val), assigned_value in assignment.items():
        if assigned_value:
            grid[row][col] = val
    return grid
