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
        self.variables_constraints = {}
        self.list_of_variables = None
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

        # making sure that every value in a variable’s domain has the same number of letters as the variable’s length.

        for v, words in domains_cpy_items:
            for w in words:
                if len(w) != v.length:
                    elements_to_remove.append((v, w))  # = self.domains[v].remove(x)

        # Remove elements outside the loop
        for v, w in elements_to_remove:
            self.domains[v].remove(w)

        print("AFTER ENFORCING NODE CONSISTENCY:")
        print_domains(self.domains)

    def revise(self, x, y, domain_cpy):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision_made = False

        def satisfies_constraint(x, y):
            """
            x is arc consistent with y when every value in the domain of x has a possible value
            in the domain of y that does not cause a conflict. (A conflict in the context of the crossword puzzle
            is a square for which two variables disagree on what character value it should take on.)
            :param word:
            :param y:
            :return:
            """

            # Finding corresponding possible values of x in the domain of y
            if x in self.domains[y]:
                # TODO: What correct role here an overlap plays? get the overlap, if any, between two variables.
                """
                if len(self.crossword.overlaps(x, y)) == 0:
                    return False
                """
                return True
            else:
                return False

        """
        To make x arc consistent with y, you’ll want to remove any value from the domain of x 
        that does not have a corresponding possible value in the domain of y.
        """
        if not satisfies_constraint(x, y):
            if len(self.domains[x]) > 0:
                self.domains[x].pop()
                revision_made = True
                # Find the variable and note to the self.variables_constraints
                # that this variable contains a word that it is constraining
                if x in self.variables_constraints:
                    self.variables_constraints[x] += 1
                else:
                    self.variables_constraints[x] = 1

        # constraints update: make the pairs from the constraint
        self.constraints = create_all_pairs_from_list(self.variables_constraints)

        return revision_made

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

        domain_cpy = self.domains.copy()

        while len(queue) > 0:
            (X, Y) = queue.pop()

            if self.revise(X, Y, domain_cpy):
                # TODO: Finish the AC-3 algorithm
                if X.length == 0:
                    """
                    If, in the process of enforcing arc consistency, you remove all of the remaining values from a domain, 
                    return False (this means it’s impossible to solve the problem, 
                    since there are no more possible values for the variable). 
                    Otherwise, return True.
                    """
                    return False

                """
                print("self.crossword.neighbors(X):")
                print(self.crossword.neighbors(X))
                print("Y:")
                print({Y})
                print(self.crossword.neighbors(X) - {Y})
                """
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
        if self.select_unassigned_variable(assignment) is None:
            return True

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for (x, y) in self.constraints:

            # Only the assigned arcs
            if x not in assignment or y not in assignment:
                continue

            # Check whether all values distinct
            if assignment[x] == assignment[y]:
                return False

            # Check whether there are conflicts between neighbouring variables
            domains_cpy = self.domains.copy()

            self.revise(x, y, domains_cpy)
                #return False

        # All conditions are met, it is OK
        return True


    def order_domain_values(self, var, not_assigned):
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
                # TODO: This should contain the actual value
                constrained_vars_ordered = dict(sorted(self.variables_constraints.items(), key=lambda item: item[1]))
                return next(iter(constrained_vars_ordered.values()))

        # if self.consistent(not_assigned):
        returned_order = order_not_assigned()
        return returned_order
        """
        else:
            self.enforce_node_consistency()
            if self.consistent(not_assigned):
                returned_order = order_not_assigned()
                return returned_order
            else:
                raise Exception("Unexpected state of the program. "
                                "Assignment is still not consistent even after enforcing consistency.")
        """

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
            # Not already part of the assignment
            if var not in assignment:
                return var
        return None

    def least_constraining_heuristic(self, var):
        """
        computed as the number of values ruled out for neighboring unassigned variables.

        :return:
        """
        return self.variables_constraints[var]

    def backtrack(self, assignment):
        """
        :argument assignment partial assignment; {Variable: "word"}

        :return complete satisfactory assignment of variables to values (if it is possible to do so)

        SEE the HW video lecture for the pseudocode

        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # TODO: An assignment is a dictionary where the keys are Variable objects and the values are strings
        #  representing the words those variables will take on. The input assignment may not be complete
        #  (not all variables will necessarily have values).
        # TODO: If you would like, you may find that your algorithm is more efficient if you interleave search with inference (as by maintaining arc consistency every time you make a new assignment). You are not required to do this, but you are permitted to, so long as your function still produces correct results. (It is for this reason that the ac3 function allows an arcs argument, in case you’d like to start with a different queue of arcs.)

        """
        If it is possible to generate a satisfactory crossword puzzle, your function should return the complete assignment: 
        a dictionary where each variable is a key and the value is the word that the variable should take on.
        """
        # Assignment complete
        if len(assignment) == len(self.variables_constraints):
            return assignment

        var = self.select_unassigned_variable(assignment)

        # TODO: var should be the Variable but the value should be the word!
        domain_values = self.domains[var].copy()
        for value in domain_values:
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)

                if result is not None:
                    return result

            # del assignment[var]
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

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
