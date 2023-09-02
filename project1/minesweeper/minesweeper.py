import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        if self.count == 0:
            return set()

        # generally, any time the number of cells is equal to the count,
        # we know that all of that sentence’s cells must be mines.
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        # Intuitively, we can infer from that sentence that all of the cells must be safe.
        # By extension, any time we have a sentence whose count is 0,
        # we know that all of that sentence’s cells must be safe.
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """

        # Likewise, if our AI knew the sentence {A, B, C} = 2, and we were told that C is a mine, we could remove
        # C from the sentence and decrease the value of count
        if len(self.cells) == self.count + 1:
            if cell in self.cells:
                self.cells.remove(cell)
                self.count -= 1
                print("mark_mine:self.cells")
                print(self.cells)
                print("cell: {}".format(cell))

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if len(self.cells) == self.count + 1:
            if cell in self.cells:
                self.cells.remove(cell)
                self.count -= 1
                # if we were told that C were safe, we could remove C from the sentence altogether,
                print("mark_safe:self.cells")
                print(self.cells)
                print("cell: {}".format(cell))

    """
    def identify_safe_cell(self):

        safe_cells = []
        for cell in self.cells:
            if not cell:
                safe_cells.append(self.cells.pop())

        if len(safe_cells) == 1:
            return safe_cells
    """


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        print("cell in mark_safe: {}".format(cell))
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        print("cell in add_knowledge")
        print(cell)
        self.mark_safe(cell)
        """
        3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
        """
        new_sentence = Sentence(cell, count)
        self.knowledge.append(new_sentence)
        print("new_sentence")
        print(new_sentence)

        """
        4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
        """
        print("4) mark any additional cells as safe or as mines "
              "if it can be concluded based on the AI's knowledge base")
        for sentence in self.knowledge:
            known_safes = sentence.known_safes()
            known_mines = sentence.known_mines()
            print("known_safes: {}".format(known_safes))
            print("known_mines: {}".format(known_mines))
            if len(known_safes) > 0:
                for safe_cell in known_safes.copy():
                    print("safe_cell: {}".format(safe_cell))

                    self.mark_safe(safe_cell)
                    # 5) add any new sentences to the AI's knowledge base
                    # if they can be inferred from existing knowledge
                    print("5) add any new sentences to the AI's "
                          "knowledge base if they can be inferred from existing knowledge")
                    print("mark_safe")

                    self.update_knowledge()

            if len(known_mines) > 0:
                for mine_cell in known_mines.copy():
                    self.mark_mine(mine_cell)
                    # 5) add any new sentences to the AI's knowledge base
                    # if they can be inferred from existing knowledge
                    print("5) add any new sentences to the AI's "
                          "knowledge base if they can be inferred from existing knowledge")
                    print("mark_mine")

                    self.update_knowledge()
        # We know this by an inference described in the exercise description
        self.update_knowledge()

        # Note that any time that you make any change to your AI’s knowledge,
        # it may be possible to draw new inferences that weren’t possible before.
        # Be sure that those new inferences are added to the knowledge base if it is possible to do so.

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # TODO:
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        print("make_random_move")
        if len(self.moves_made) < self.width*self.height:

            options_tried = set()
            while True:
                random_move_i = random.randrange(0, self.height)
                random_move_j = random.randrange(0, self.width)
                print("random_move_i: {}".format(random_move_i))
                print("random_move_j: {}".format(random_move_j))
                print("self.moves_made:")
                print(self.moves_made)
                print("self.safes:")
                print(self.safes)

                print("options_tried: {}".format(options_tried))

                # We do not known at all whether it mine or not, so we just pick completely random
                if len(options_tried) == (self.width*self.height):
                    if (random_move_i, random_move_j) not in self.moves_made:
                        return (random_move_i, random_move_j)

                # We pick randomly but only those which are in safe

                if ((random_move_i, random_move_j) not in self.moves_made
                        and (random_move_i, random_move_j) in self.safes):
                    print("Random move:")
                    print("random_move_i, random_move_j")
                    return random_move_i, random_move_j
                else:
                    options_tried.add(((random_move_i, random_move_j)))

    def update_knowledge(self):
        knowledge = self.knowledge
        print(knowledge)
        print(self.knowledge)
        count_control = 0
        for i in range(len(knowledge)):
            for j in range(len(knowledge)):
                print("knowledge[i]: {}".format(knowledge[i]))
                print("knowledge[j]: {}".format(knowledge[j]))
                count_control += 1
                if len(knowledge[i].cells) > 0 and len(knowledge[j].cells) > 0:
                    if knowledge[i].cells.issubset(knowledge[j].cells):
                        new_cells = knowledge[j].cells - knowledge[i].cells
                        new_count = knowledge[j].count - knowledge[i].count
                        print("new_cells {}".format(new_cells))
                        print("new_count {}".format(new_count))
                        self.knowledge.append(Sentence(new_cells, new_count))
                        print("Knowledge after update:")
                        print(self.knowledge)

                if count_control > (self.width*self.height):
                    break


class Helpers:

    def powerset(self, iterable):
        s = list(iterable)
        return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))
