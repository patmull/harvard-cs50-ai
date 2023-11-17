import sys

from crossword import *
from data_helpers import create_all_pairs_from_list, get_dict_shared_items


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }
        # <variable>: <number of words ruled out> (NOTE: This was added later by me, not an original class attribute)
        self.list_of_variables = {}
        self.constrained = {}
        self.constraints = set()

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP (Constraint Satisfaction Problem).
        """

        self.enforce_node_consistency()

        print("BEFORE AC3:")
        print(self.domains)

        self.ac3()

        print("AFTER AC3:")
        print(self.domains)
        self.constraints = self.create_constraints()

        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        domains_cpy_items = self.domains.copy().items()

        print("BEFORE ENFORCE NODE CONSISTENCY:")
        print_domains(self.domains)

        elements_to_remove = []  # Create a list to store elements to be removed

        # Unary constraint: making sure that every value in a variable’s domain
        # has the same number of letters as the variable’s length.
        for v, words in domains_cpy_items:
            for w in words:
                if len(w) != v.length:
                    elements_to_remove.append((v, w))

        # Remove elements outside the loop
        for (v, w) in elements_to_remove:
            self.domains[v].remove(w)

        print("AFTER ENFORCING NODE CONSISTENCY:")
        print_domains(self.domains)

    def revise(self, x, y):
        """
        x and y will both be Variable objects representing variables in the puzzle.

        :return The function should return True if a revision was made to the domain of x;
        otherwise return False

        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        """

        """
        To make x arc consistent with y, you’ll want to remove any value from the domain of x 
        that does not have a corresponding possible value in the domain of y.
        """
        overlap = self.crossword.overlaps[(x, y)]
        print("overlap")
        print(overlap)

        if overlap is None:
            return False
        else:
            self.solve_conflicting_chars(x, y, overlap)

            return False

    def solve_conflicting_chars(self, x, y, overlap):
        """
        remove any value from the domain of x that does not have
        #  a corresponding possible value in the domain of y.

        :param x:
        :param y:
        :param overlap:
        :return:
        """
        print("x, y:")
        print(x, y)

        x_words_list = list(self.domains[x])
        y_words_list = list(self.domains[y])

        for i in range(len(x_words_list)):
            for j in range(len(y_words_list)):
                if x_words_list[i] == y_words_list[j] and x_words_list[i][overlap[0]] != y_words_list[j][overlap[1]]:
                    # not equal => needs to be removed
                    print("x:")
                    print(self.domains[x])

                    if x_words_list[i] in self.domains[x]:
                        print("self.domains.", self.domains)
                        print("self.domains[x]:", self.domains[x])
                        print("x_words_list[i]:", x_words_list[i])
                        self.domains[x].remove(x_words_list[i])
                        print("self.domains:", self.domains)
                        # TODO: Too many variables gets eliminated. Some became empty sets, find out why
                    print(self.domains[x])

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = set()

        if arcs is None:
            self.list_of_variables = list(self.domains.keys())
            queue = create_all_pairs_from_list(self.list_of_variables)
        else:
            for arc in arcs:
                queue.add(arc)

        while len(queue) > 0:

            (X, Y) = queue.pop()

            if self.revise(X, Y):

                if len(self.domains) == 0:
                    return False

                for Z in (self.crossword.neighbors(X) - {Y}):
                    # print("queue:")
                    # print(queue)

                    if (Z, X) in queue:
                        queue.remove((Z, X))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(assignment) == len(self.list_of_variables):
            return True
        else:
            return False

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # The binary constraints on a variable are given by its overlap with neighboring variables
        for var_x, word_x in assignment.items():
            # proper length
            if var_x.length != len(word_x):  # check if assigned word is of the proper length for the variable
                return False

            for var_y, word_y in assignment.items():
                if var_x != var_y:
                    if word_x == word_y:
                        return False

                    overlap = self.crossword.overlaps[var_x, var_y]  # it returns indices where they overlap
                    if overlap:  # if there is an overlap, make sure that the certain character is the same
                        x_overlap, y_overlap = overlap
                        if word_x[x_overlap] != word_y[y_overlap]:  # if the characters are different, then it is inconsistent
                            return False

            # Only the assigned arcs
            if var_x not in assignment or word_x not in assignment:
                continue

            # Check whether all values distinct
            if assignment[var_x] == assignment[word_x]:
                return False

        # All conditions are met, consistency is OK
        return True

    def create_constraints(self):
        neighbors_pairs = []

        for var in self.list_of_variables:
            var_neighbors = self.crossword.neighbors(var)
            for var_neighbor in var_neighbors:
                neighbors_overlap = self.crossword.overlaps[(var, var_neighbor)]
                # pairs = create_all_pairs_from_list(list(neighbors_overlap))
                neighbors_pairs.append(neighbors_overlap)

                print("neighbors_pairs:")
                print(neighbors_pairs)

        return neighbors_pairs

    def order_domain_values(self, var):
        """
        var: Variable object, representing a variable in the puzzle.

        return: list of all the values (the actual words in the crossword) in the domain of var.
        """

        def order_not_assigned():

            # for the neighboring unassigned variables.

            # least-constraining values heuristic
            n = self.least_constraining_heuristic(var)  # this is used for ordering results in ascending order of n
            print("n:")
            print(n)

            if n > 0:
                constrained_vars_ordered = dict(sorted(self.list_of_variables.items(), key=lambda item: item[1]))
                return next(iter(constrained_vars_ordered.values()))

        # if self.consistent(not_assigned):
        returned_order = order_not_assigned()
        return returned_order

    def select_unassigned_variable(self, assignment):
        """
        return: an unassigned variable object not already part of `assignment`.

        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        for var in self.list_of_variables:
            """
            Note that any variable present in assignment already has a value, 
            and therefore shouldn’t be counted when computing the number of values ruled out 
            for neighboring unassigned variables.
            """
            # Not already part of the assignment and not none value
            # if var not in assignment and self.domains[var] is not None and len(self.domains[var]) > 0:

            if var in self.domains:
                if var not in assignment and len(self.domains[var]) > 0:

                    if var is None:
                        raise ValueError("var is None.")

                    return var
        return None

    def least_constraining_heuristic(self, var):
        """
        computed as the number of values ruled out for neighboring unassigned variables.

        :return:
        """
        return self.constrained[var]

    def backtrack(self, assignment):
        """
        :param assignment:
        :argument assignment partial assignment; {Variable: "word"}

        :return complete satisfactory assignment of variables to values (if it is possible to do so)

        SEE the HW video lecture for the pseudocode

        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        """
        If it is possible to generate a satisfactory crossword puzzle, your function should return the complete assignment: 
        a dictionary where each variable is a key and the value is the word that the variable should take on.
        """
        # Assignment complete
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        if var is None:
            # no more values to return
            return assignment

        print("self.domains")
        print(self.domains)
        domain_values = self.domains[var].copy()
        print("domain_values:")
        print(domain_values)

        for value in domain_values:

            if value not in assignment.values():
                new_assignment = assignment.copy()
                new_assignment[var] = value
                if self.consistent(new_assignment):
                    result = self.backtrack(new_assignment)

                    if result is not None:
                        return result

        return None


def print_domains(domains):
    for value, words in domains.items():
        print(f"{value}, num of words: {len(words)}")


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    print(f"assignment:", assignment)

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
