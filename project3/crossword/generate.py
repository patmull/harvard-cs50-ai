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
            print()

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

        def satisfies_constraint(word, y):
            """
            x is arc consistent with y when every value in the domain of x has a possible value
            in the domain of y that does not cause a conflict. (A conflict in the context of the crossword puzzle
            is a square for which two variables disagree on what character value it should take on.)
            :param word:
            :param y:
            :return:
            """

            print(self.crossword.overlaps)
            # Finding corresponding possible values of x in the domain of y
            if word in self.domains[y]:
                return True
            else:
                return False

        for word in domain_cpy:
            """
            To make x arc consistent with y, you’ll want to remove any value from the domain of x 
            that does not have a corresponding possible value in the domain of y.
            """
            if not satisfies_constraint(word, y):
                if len(self.domains[x]) > 0:
                    self.domains[x].pop()
                    revision_made = True

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

            list_of_variables = list(self.domains.keys())
            queue = create_all_pairs_from_list(list_of_variables)

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
        for variable, words in assignment:
            if len(words) == 0:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        all_words = set()

        if self.assignment_complete(assignment):
            # TODO: An assignment is consistent if it satisfies all of the constraints of the problem:
            #  that is to say, all values are distinct, every value is the correct length,
            #  and there are no conflicts between neighboring variables.

            for variable, words in assignment:
                all_words = all_words.union(words)
                for word in words:
                    # Check whether all values distinct
                    if word in all_words:
                        return False

                # Check whether every value is the correct length
                if variable.length != len(words):
                    return False

            # TODO: Check whether there are conflicts between neighbouring variables

            return True
        else:
            return False

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # the least-constraining values heuristic is computed
        # as the number of values ruled out for neighboring unassigned variables.
        # That is to say, if assigning var to a particular value results in eliminating n possible choices
        # for neighboring variables, you should order your results in ascending order of n.

        if self.consistent(assignment):
            return assignment[var]
        else:
            self.enforce_node_consistency()
            if self.consistent(assignment):
                return assignment[var]
            else:
                raise Exception("Unexpected state of the program. "
                                "Assignment is still not consistent even after enforcing consistency.")

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """


        raise NotImplementedError

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        raise NotImplementedError


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
