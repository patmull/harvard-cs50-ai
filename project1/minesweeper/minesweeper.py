import itertools
import random
import traceback
import iteration_utilities


class Minesweeper:
    """
    Minesweeper game representation

    Good resource for the moves: https://minesweeper.online/help/patterns
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines_known
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines_known
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines_known randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines_known
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines_known are located.
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
        Returns the number of mines_known that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines_known
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
        if self.mines_found == self.mines:
            return True


# We know the exact value of these cells
class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines_known.
    """

    def __init__(self, cells, count):

        if count < 0:
            raise ValueError("Count cannot be negative! If it is negative by the sum calculation, then do not create "
                             "the Sentence object in the first place!")

        self.cells = set()
        # print("Sentence.cells: {}".format(cells))
        print(type(cells))
        if isinstance(cells, tuple):
            if cells not in self.cells and len(cells) > 0:
                self.cells.add(cells)
                print("self.cells {}".format(self.cells))
        elif isinstance(cells, set):
            if len(cells) == 0:
                print("Set empty. Not adding anything.")
            elif len(cells) > 0:
                if cells not in self.cells:
                    self.cells.update(cells)
            else:
                raise ValueError("Unexpected length of a cell!")
        else:
            raise ValueError("Unexpected length of a cell!")

        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines_known.
        """
        if self.count == 0:
            return set()

        # generally, any time the number of cells is equal to the count,
        # we know that all of that sentence’s cells must be mines.
        if self.count == len(self.cells):
            print("Known mines")
            print("self.count: {}".format(self.count))
            print("len(self.cells): {}".format(self.cells))
            print("len(self.cells): {}".format(len(self.cells)))
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
                # print("cell: {}".format(cell))

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if len(self.cells) == self.count + 1:
            if cell in self.cells:
                print("cell to remove: {}".format(cell))
                print("cells before the removal:")
                print(self.cells)
                self.cells.remove(cell)
                self.count -= 1
                # if we were told that C were safe, we could remove C from the sentence altogether,
                print("mark_safe:self.cells")
                print(self.cells)

    """
    def identify_safe_cell(self):

        safe_cells = []
        for cell in self.cells:
            if not cell:
                safe_cells.append(self.cells.pop())

        if len(safe_cells) == 1:
            return safe_cells
    """


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8, mines=8, mines_flagged=None):

        # Set initial height and width
        if mines_flagged is None:
            self.mines_flagged = set()
        else:
            self.mines_flagged = mines_flagged

        self.board = [[None] * width for i in range(height)]
        self.mines = mines
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines_known
        self.mines_known = set()
        # Keep track of cells known to be safe or mines
        self.mines_known_by_ai = set()
        # We know these are safe, but don't know the exact value of those
        self.safes_known = set()

        # Column or row in which consecutive ones pattern was found
        self.consecutive_ones_found_horizontally = []
        self.consecutive_ones_found_vertically = []

        # neighbourhoods around cells with high values
        # TODO: Add another set for >0
        self.suspected_mines_small_danger = set()
        self.suspected_mines_mild_danger = set()
        self.suspected_mines_big_danger = set()
        self.suspected_mines_very_big_danger = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def get_minesweeper_board(self):
        # print("get_minesweeper_board:self.board: {}".format(self.board))
        return self.board

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        print("mark_mine.type(cell):")
        print(type(cell))
        self.mines_known.add(cell)

        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def won(self):
        if len(self.moves_made) == self.width*self.height-self.mines:
            return True
        else:
            return False

    def add_cells_to_knowledge(self, cells, count):
        new_sentence = Sentence(cells, count)
        print("add_cells_to_knowledge.new_sentence: {}".format(new_sentence))
        self.knowledge.append(new_sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        # print("cell in mark_safe: {}".format(cell))
        # print("mark_safe.type(cell):")
        # print(type(cell))
        if isinstance(cell, set):
            print("mark_safe.type(cell):")
            print(type(cell))
            if len(cell) == 1:
                self.safes_known.add(tuple(iteration_utilities.first(cell)))
            else:
                print("THIS IS NOT A VALID CELL!!!")
                print("cell:")
                print(cell)
                traceback.print_stack()
        else:
            # print("THIS IS NOT A SET!!!")
            # print("mark_safe.type(cell):")
            # print(type(cell))
            # # print("cell: {}".format(cell))
            # traceback.print_stack()
            if isinstance(cell, tuple):
                # print("Variable is already a tuple. Not converting.")
                self.safes_known.add(tuple(cell))
            else:
                print("Variable is neither a tuple, neither a set.")
                print(type(cell))
                traceback.print_stack()

        # UPDATING THE KNOWLEDGE

        # Add new knowledge (multiple cells sentences)

        # remove the empty sets from the knowledge
        updated_knowledge = []
        for sentence in self.knowledge:
            if len(sentence.cells) > 0:
                updated_knowledge.append(sentence)

        self.knowledge = updated_knowledge

    def get_neighbor_cells_sum(self, cell, types="all"):

        # 1. iterate through knowledge for the counts
        # 2. check whether the cells in knowledge (sentence.cells) are neighbor cells of the input cell
        neighbor_cells = self.get_neighbor_cells(cell, types=types)
        neighbor_cells_sum = 0

        if len(neighbor_cells) > 0:

            for sentence in self.knowledge:
                for knowledge_cell in sentence.cells:
                    if knowledge_cell in neighbor_cells:
                        neighbor_cells_sum += sentence.count

        return neighbor_cells_sum

    def get_neighbor_cells(self, cell, types=None):
        # print("Searching neighbors for the cell: {}".format(cell))

        if types is None:
            raise ValueError("types argument needs to be specified!")

        all_neighbors = False
        if str.lower(types) == 'all' or str.lower(types) == 'only-known':
            all_neighbors = True

        returned_cells = []
        if "bottom-neighbor" in types or all_neighbors:
            # bottom neighbor
            if cell[0] < self.height - 1:
                # print(type(cell))
                # print("cell[0]: {}".format(cell[0]))
                # print("cell[1]: {}".format(cell[1]))

                safe_height = cell[0] + 1
                safe_width = cell[1]
                neighbor_cell = (safe_height, safe_width)
                # print("bottom neighbor")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if "upper-neighbor" in types or all_neighbors:
            # upper neighbor
            if cell[0] > 0:
                safe_height = cell[0] - 1
                safe_width = cell[1]
                neighbor_cell = (safe_height, safe_width)

                # print("upper neighbor")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if "left-neighbor" in types or all_neighbors:
            # left neighbor
            if cell[1] > 0:
                safe_height = cell[0]
                safe_width = cell[1] - 1
                neighbor_cell = (safe_height, safe_width)

                # print("left neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if "right-neighbor" in types or all_neighbors:
            # right neighbor
            if cell[1] < self.width - 1:
                safe_height = cell[0]
                safe_width = cell[1] + 1
                neighbor_cell = (safe_height, safe_width)

                # print("right neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if "left-upper-corner" in types or all_neighbors:
            # left upper corner neighbor
            if cell[0] > 0 and cell[1] > 0:
                safe_height = cell[0] - 1
                safe_width = cell[1] - 1
                neighbor_cell = (safe_height, safe_width)

                # print("left upper corner neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if "right-upper-corner" in types or all_neighbors:
            # right upper corner neighbor
            if cell[0] > 0 and cell[1] < self.width - 1:
                safe_height = cell[0] - 1
                safe_width = cell[1] + 1
                neighbor_cell = (safe_height, safe_width)

                # print("right upper corner neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if type == "left-bottom-corner" or all_neighbors:
            # left bottom corner neighbor
            if cell[0] < self.height - 1 and cell[1] > 0:
                safe_height = cell[0] + 1
                safe_width = cell[1] - 1
                neighbor_cell = (safe_height, safe_width)

                # print("left bottom corner neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        if type == "right-bottom-corner" or all_neighbors:
            # right bottom corner neighbor
            if cell[0] < self.height - 1 and cell[1] < self.width - 1:
                safe_height = cell[0] + 1
                safe_width = cell[1] + 1
                neighbor_cell = (safe_height, safe_width)

                # print("right bottom corner neighbor:")
                # print("cell: {}".format(cell))
                # print("neighbor_cell: {}".format(neighbor_cell))

                if types == "only-known":
                    if neighbor_cell in self.moves_made:
                        returned_cells.append(neighbor_cell)
                else:
                    returned_cells.append(neighbor_cell)

        return returned_cells

    def find_sentence_by_cell(self, cell):
        for sentence in self.knowledge:
            for sentence_cell in sentence.cells:
                if sentence_cell == cell:
                    return sentence
        return None

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines_known in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines_known
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        if isinstance(cell, tuple):
            print("if isinstance:add_knowledge.type(cell):")
            print(type(cell))
            self.moves_made.add(cell)
        else:
            print("Variable NOT TUPLE!")
            print(cell)
            print(type(cell))
            traceback.print_stack()
        # 2) mark the cell as safe
        print("cell in add_knowledge")
        print(cell)
        print("add_knowledge.type(cell)")
        print(type(cell))
        self.mark_safe(cell)
        """
        3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
        """
        new_sentence = Sentence(cell, count)

        if new_sentence not in self.knowledge:
            self.knowledge.append(new_sentence)
            print("new_sentence")
            print(new_sentence)

        """
        4) mark any additional cells as safe or as mines_known
               if it can be concluded based on the AI's knowledge base
        """
        print("4) mark any additional cells as safe or as mines_known "
              "if it can be concluded based on the AI's knowledge base")
        # # self.print_knowledge()

        self.update_knowledge()

        #  TODO: Add multiple cells to knowledge sentences

        # Note that any time that you make any change to your AI’s knowledge,
        # it may be possible to draw new inferences that weren’t possible before.
        # Be sure that those new inferences are added to the knowledge base if it is possible to do so.

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines_known, self.safes_known
        and self.moves_made, but should not modify any of those values.
        """

        # The moves made needs to be a superset of the safe moves, otherwise something went wrong.
        """
        if len(self.moves_made) < len(self.safes_known):
            raise ValueError("Safes known are bigger than moves_made. This is obviously an error.")
        """

        safes_known_from_knowledge = set()

        print("self.safes_known:")
        print(self.safes_known)

        print("self.mines_known_by_ai:")
        print(self.mines_known_by_ai)

        if len(self.safes_known) > 0:
            for safe_known_cell in self.safes_known:
                print("self.moves_made: {}".format(self.moves_made))
                print("safe_known_cell: {}".format(safe_known_cell))
                if safe_known_cell not in self.moves_made:
                    safes_known_from_knowledge.add(safe_known_cell)

        for sentence in self.knowledge:

            # PREP FOR STRATEGIES
            if len(sentence.cells) > 0:
                # print("if sentence.count:sentence.cells {}".format(sentence.cells))
                new_safe_cells = list(sentence.cells)[0]
                safes_known_from_knowledge.add(new_safe_cells)

        # print("safes_known_from_knowledge: {}".format(safes_known_from_knowledge))
        # print("self.safes_known: {}".format(self.safes_known))
        # print("self.moves_made")
        # print(self.moves_made)

        # Filter moves already made
        safe_choices = set()

        if len(safes_known_from_knowledge) > 0:

            for safe_cell in safes_known_from_knowledge:
                if safe_cell not in self.moves_made:
                    safe_choices.add(safe_cell)

        if len(self.safes_known) > 0:
            for safe_cell in self.safes_known:
                if safe_cell not in self.moves_made:
                    safe_choices.add(safe_cell)

        else:
            print("safes_known_from_knowledge is zero, cannot use any knowledge.")
            return None

        print("safe_choices:")
        print(safe_choices)

        if len(self.moves_made) > 0:

            # NEIGHBOUR CELLS STRATEGY (IF NOT CROSS, WILL DO CORNERS OF ZERO)
            for sentence in self.knowledge:

                if sentence.count == 0:
                    # THE CROSS OF ZEROS STRATEGY

                    for safe_cell in sentence.cells:

                        tested_tuple = (safe_cell[0], safe_cell[1] - 1)
                        neighbour_cells = self.cross_strategy(sentence, tested_tuple)
                        if neighbour_cells is not None:
                            print("THE CROSS OF ZEROS STRATEGY")
                            return neighbour_cells

                        tested_tuple = (safe_cell[0], safe_cell[1] + 1)
                        neighbour_cells = self.cross_strategy(sentence, tested_tuple)
                        if neighbour_cells is not None:
                            print("THE CROSS OF ZEROS STRATEGY")
                            return neighbour_cells

                        tested_tuple = (safe_cell[0] + 1, safe_cell[1])
                        neighbour_cells = self.cross_strategy(sentence, tested_tuple)
                        if neighbour_cells is not None:
                            print("THE CROSS OF ZEROS STRATEGY")
                            return neighbour_cells

                        tested_tuple = (safe_cell[0] - 1, safe_cell[1])
                        neighbour_cells = self.cross_strategy(sentence, tested_tuple)
                        if neighbour_cells is not None:
                            print("THE CROSS OF ZEROS STRATEGY")
                            return neighbour_cells

                    # CORNERS NEIGHBOURS OF ZERO CELLS STRATEGY

                    print(sentence)
                    print("sentence.cells[0]")
                    if len(sentence.cells) > 0:
                        print(list(sentence.cells)[0])
                        print("self.moves_made: {}".format(self.moves_made))
                        if sentence.count == 0:
                            for safe_cell in sentence.cells:
                                if safe_cell in self.moves_made:
                                    neighbour_cells = self.get_neighbor_cells(safe_cell, 'all')
                                    print("safe_cell: {}".format(safe_cell))
                                    print("neighbour_cells: {}".format(neighbour_cells))
                                    if neighbour_cells is not None:
                                        for cell in neighbour_cells:
                                            if cell not in self.moves_made:
                                                print("CORNERS NEIGHBOURS OF ZERO CELLS STRATEGY:")
                                                return cell

        if len(safe_choices) > 0:
            # RANDOM FROM SAFES STRATEGY
            safe_choices = [[item for item in pair] for pair in safe_choices]

            if len(safe_choices) > 0:
                print("Making a move based on the RANDOM FROM SAFES STRATEGY.")
                return get_random_item_from_set(safe_choices)

        # LOW PROBABILITY AROUND
        safer_random = self.get_cell_with_lowest_probability_of_mine_in_neighborhood()
        if safer_random:
            print(safer_random)
            return safer_random

        # LOWEST SUM OF NEIGHBORS STRATEGY
        safer_random = self.get_cell_with_lowest_sum_of_neighbourhood(1.33)
        if safer_random:
            print(safer_random)
            return safer_random

        # RANDOM FROM NON-SUSPECTED AND SAFES
        safer_random = self.get_from_safes_and_non_suspected(self.suspected_mines_mild_danger)
        if safer_random:
            return safer_random

        safer_random = self.get_from_safes_and_non_suspected(self.suspected_mines_big_danger)
        if safer_random:
            return safer_random

        safer_random = self.get_cell_with_lowest_sum_of_neighbourhood(1.5)
        if safer_random:
            print("Found by the lowest sum of neighbourhood cells strategy.")
            print(safer_random)
            return safer_random

        # RANDOM BUT NOT FROM NOT KNOWN MINES
        # last resort is simply choose random from non-mines, because there is no other way to choose
        # This differs from the pure random move below
        safer_random = self.get_safer_random({})
        if safer_random:
            return safer_random

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines_known
        """
        if len(self.moves_made) < self.width * self.height:

            options_tried = set()
            while True:
                random_move_i = random.randrange(0, self.height)
                random_move_j = random.randrange(0, self.width)
                # print("random_move_i: {}".format(random_move_i))
                # print("random_move_j: {}".format(random_move_j))

                # print("options_tried: {}".format(options_tried))

                # We do not known at all whether it mine or not, so we just pick completely random
                if len(options_tried) == (self.width * self.height):
                    if (random_move_i, random_move_j) not in self.moves_made:
                        return random_move_i, random_move_j

                # We pick randomly but only those which are in safe
                if ((random_move_i, random_move_j) not in self.moves_made
                        and (random_move_i, random_move_j) in self.safes_known):
                    print("Random move:")
                    print("random_move_i, random_move_j")
                    added_move = (random_move_i, random_move_j)

                    return added_move
                else:
                    options_tried.add((random_move_i, random_move_j))

    def update_knowledge(self):
        self.print_knowledge()

        """
        for sentence in knowledge:
            for sentence_j in knowledge:
                # count_control += 1
                if len(sentence.cells) > 0 and len(sentence_j.cells) > 0 and sentence.cells.issubset(sentence_j.cells):
                    # self.print_knowledge()
                    # print("sentence_j.cells: {}".format(sentence_j.cells))
                    # print("knowledge[i].cells: {}".format(knowledge[i].cells))
                    new_cells = sentence_j.cells.difference(sentence.cells)
                    new_count = sentence_j.count - sentence.count
                    if new_count > 0 and len(new_cells) >= 0:
                        print("new_cells: {}".format(new_cells))
                        print(len(new_cells))
                        self.add_new_knowledge_with_new_cells(new_cells, new_count)

                        new_sentence = Sentence(new_cells, new_count)
                        if new_sentence not in self.knowledge:
                            print("Adding the calculated cells based on the cell counts:")
                            print(new_sentence)
                            self.knowledge.append(new_sentence)
                        # print("Updated knowledge:")
                        # self.print_knowledge()
                        else:
                            raise ValueError("Unexpected length of the cells.")
        """

        # Searching for the cell in the knowledge
        cell_count = None
        for sentence in self.knowledge:

            if len(sentence.cells) == 1:
                for sentence_cell in sentence.cells:
                    neighbor_cells = self.get_neighbor_cells(sentence_cell, "all")
                    neighbor_cells_known = self.get_neighbor_cells(sentence_cell, 'only-known')
                    neighbor_cells_open = set(neighbor_cells) - set(neighbor_cells_known)

                    # COUNT EQUAL TO OPEN strategy
                    # https://youtu.be/8j7bkNXNx4M?si=lE4n4ORCcImYpszw&t=93 STRATEGY 2:

                    print("cell: {}".format(sentence_cell))
                    print("neighbor_cells_open: {}".format(neighbor_cells_open))

                    print("cell_count: {}".format(cell_count))
                    if len(neighbor_cells_open) == sentence.count:
                        for neighbor_cell in neighbor_cells_open:
                            if not self.mine_is_not_false_negative({neighbor_cell}):
                                print("{} cell is a false negative. Not a mines!".format(neighbor_cell))
                            else:
                                if neighbor_cell not in self.moves_made:
                                    print("Marking mines_known by the COUNT EQUAL TO OPEN strategy")
                                    print("neighbor_cell_open: {}".format(neighbor_cell))
                                    self.mines_known_by_ai.add(neighbor_cell)

                    for neighbor_cell in neighbor_cells_open:
                        if sentence.cells == {neighbor_cell}:
                            cell_count = sentence.count

                            # BASIC MINES CALCULATION STRATEGY
                            # If a number is touching the same number of cells,
                            # then these cells are all mines.
                            print("cell_count: {}".format(cell_count))
                            print("neighbor cells: {}".format(neighbor_cells))
                            free_neighbor_cells = set(neighbor_cells) - self.moves_made
                            print("free_neighbor_cells: {}".format(free_neighbor_cells))
                            if cell_count == len(free_neighbor_cells) and len(free_neighbor_cells) > 0:
                                print("Adding to mines: {}".format(free_neighbor_cells))
                                for free_neighbor_cell in free_neighbor_cells:
                                    self.add_mine_known_by_ai(free_neighbor_cell)

                    # IF CELL HAS FLAGGED NEIGHBOR
                    # AND THE CELL COUNT IS EQUAL TO THE NUMBER OF FLAGGED NEIGHBORS
                    # ALL OTHER NEIGHBORS ARE SAFE

                    neighbors = self.get_neighbor_cells(sentence_cell, 'all')
                    known_or_flagged = self.mines_known.union(self.mines_known_by_ai)
                    flagged_neighbors = known_or_flagged.intersection(neighbors)
                    print("sentence_cell: {}".format(sentence_cell))
                    print("neighbors: {}".format(neighbors))
                    print("known_or_flagged: {}".format(known_or_flagged))
                    print("flagged_neighbors: {}".format(flagged_neighbors))
                    if flagged_neighbors:
                        sentence_about_cell = self.find_sentence_by_cell(sentence_cell)

                        if sentence_about_cell.count > 0:

                            if sentence_about_cell.count == len(flagged_neighbors):
                                for neighbor in neighbors:
                                    if neighbor not in self.moves_made and neighbor not in known_or_flagged:
                                        print("Marking safe by the FLAGGED NEIGHBOR strategy")
                                        print("neighbor")
                                        print(neighbor)
                                        self.mark_safe(neighbor)

                    # SUM OF NEIGHBORS STRATEGY
                    # IF SUM OF THE CELL'S NEIGHBORS IS EQUAL TO THE NUMBER OF OPEN CELLS IN NEIGHBOURHOOD,
                    # OPEN NEIGHBOURS ARE MINES
                    # TODO: Review. Not working properly.

                    """
                    neighbor_cells_sum = self.get_neighbor_cells_sum(sentence_cell)

                    print("sentence_cell: {}".format(sentence_cell))
                    print("neighbor_cells_sum: {}".format(neighbor_cells_sum))
                    print("neighbor_cells: {}".format(neighbor_cells_open))

                    print("cell_count: {}".format(cell_count))
                    if neighbor_cells_sum == len(neighbor_cells_open):
                        for neighbor_cell in neighbor_cells_open:
                            if not self.mine_is_not_false_negative({neighbor_cell}):
                                print("{} cell is a false negative. Not a mines!".format(neighbor_cell))
                            else:
                                print("Marking mines_known by the sum of neighbors strategy")
                                print(neighbor_cells)
                                if neighbor_cell not in self.moves_made:
                                    print("neighbor_cell_known: {}".format(neighbor_cell))
                                    self.mines_known_by_ai.add(neighbor_cell)
                """

            # PROBABILITIES STRATEGIES

            if len(sentence.cells) == 1:
                sentence_cell = list(sentence.cells)[0]

                # SUSPECTED
                suspected_neighbour_cells_cell_from_knowledge = self.get_neighbor_cells(sentence_cell, "all")

                if sentence.count < 2:
                    for neighbor_cell_suspected in suspected_neighbour_cells_cell_from_knowledge:
                        print("neighbor_cell_suspected: {}".format(neighbor_cell_suspected))
                        if (neighbor_cell_suspected not in self.moves_made
                                and neighbor_cell_suspected not in self.mines_known
                                and neighbor_cell_suspected not in self.mines_known_by_ai
                        ):
                            self.suspected_mines_mild_danger.add(neighbor_cell_suspected)
                            print("self.suspected_mines_mild_danger: {}".format(self.suspected_mines_mild_danger))

                if sentence.count < 3:
                    for neighbor_cell_suspected in suspected_neighbour_cells_cell_from_knowledge:
                        print("neighbor_cell_suspected: {}".format(neighbor_cell_suspected))
                        if (neighbor_cell_suspected not in self.moves_made
                                and neighbor_cell_suspected not in self.mines_known
                                and neighbor_cell_suspected not in self.mines_known_by_ai
                        ):
                            self.suspected_mines_big_danger.add(neighbor_cell_suspected)
                            print("self.suspected_mines_big_danger: {}".format(self.suspected_mines_mild_danger))

                if sentence.count < 4:
                    for neighbor_cell_suspected in suspected_neighbour_cells_cell_from_knowledge:
                        print("neighbor_cell_suspected: {}".format(neighbor_cell_suspected))
                        if (neighbor_cell_suspected not in self.moves_made
                                and neighbor_cell_suspected not in self.mines_known
                                and neighbor_cell_suspected not in self.mines_known_by_ai
                        ):
                            self.suspected_mines_very_big_danger.add(neighbor_cell_suspected)
                            print(
                                "self.suspected_mines_very_big_danger: {}".format(self.suspected_mines_very_big_danger))

            # THE CALCULATIONS FROM HARVARD ABOUT SAFES AND MINES:
            """
            known_mines = sentence.known_mines()

            if known_mines.intersection(self.moves_made) or known_mines.intersection(self.safes_known):
                print(known_mines)
                print("These are false negative. Not a mines!")
            else:
                for known_mine_cell in known_mines:
                    print("Marking mines by the HW calculations")
                    print("known_mine_cell: {}".format(known_mine_cell))
                    self.mines_known_by_ai.add(known_mine_cell)

                    known_safes = sentence.known_safes()
                    for known_safe_cell in known_safes:
                        self.safes_known.add(known_safe_cell)
                        
            """

        # Patterns finding strategy (https://www.youtube.com/watch?v=6vcSO7h6Nt0)
        self.search_patterns()
        """
        self.update_mines_known_by_ai()
        print("self.mines_known_by_ai: {}".format(self.mines_known_by_ai))
        self.mines_known_by_ai = self.mines_known_by_ai - self.moves_made - self.safes_known
        print("self.mines_known_by_ai: {}".format(self.mines_known_by_ai))
        """

    def get_count_for_cell(self, searched_cell):
        for sentence in self.knowledge:
            for cell in sentence.cells:
                if searched_cell == cell:
                    return sentence.count

        return -1

    def get_probabilities(self, move=None, num_of_neighbor_cells_open=None):
        count_for_cell = self.get_count_for_cell(move)
        if count_for_cell < 1:
            count_for_cell = self.get_neighbor_cells_sum(move, 'only-known')
        random_move_mine_probability = 8 / ((self.width * self.height) - len(self.moves_made))

        if move is not None and num_of_neighbor_cells_open is not None:
            safer_random_mine_probability = count_for_cell / num_of_neighbor_cells_open
            return random_move_mine_probability, safer_random_mine_probability
        else:
            return random_move_mine_probability

    def get_safer_random(self, suspected_cells):
        cells_tried = set()
        num_of_cells_tried_repeatedly = 0
        REPEATED_LIMIT = 300
        previous_added = None
        print("Searching for an option safer than a random move.")
        while len(cells_tried) < ((self.width * self.height) - len(self.moves_made)):
            safer_random_move = self.make_random_move()

            if (
                    safer_random_move not in self.mines_known_by_ai
                    and safer_random_move not in self.mines_known
                    and safer_random_move not in self.mines_flagged
                    and safer_random_move not in suspected_cells
                    and safer_random_move not in cells_tried
                    and safer_random_move not in self.moves_made
            ):

                neighbor_cells_known = self.get_neighbor_cells(safer_random_move, 'only-known')
                neighbor_cells_all = self.get_neighbor_cells(safer_random_move, 'all')
                num_of_neighbor_cells_open = len(neighbor_cells_all) - len(neighbor_cells_known)

                if num_of_neighbor_cells_open > 0:
                    random_move_mine_probability, safer_random_mine_probability \
                        = self.get_probabilities(safer_random_move, num_of_neighbor_cells_open)

                    print("safer_random_mine_probability: {}".format(safer_random_mine_probability))
                    print("random_move_mine_probability: {}".format(random_move_mine_probability))

                    if safer_random_mine_probability < random_move_mine_probability:
                        print(safer_random_mine_probability)
                        print(random_move_mine_probability)
                        print("Making a move based on the SAFER RANDOM strategy. Using suspected cells: {}"
                              .format(str(suspected_cells)))
                        return safer_random_move
                    else:
                        print("Skipping the SAFER RANDOM strategy. Random move has a greater probability to succeed.")
                        if safer_random_move not in cells_tried:
                            cells_tried.add(safer_random_move)
                            num_of_cells_tried_repeatedly += 1
                        continue
                else:
                    if safer_random_move not in cells_tried:
                        cells_tried.add(safer_random_move)
                        num_of_cells_tried_repeatedly += 1
                    continue
            else:
                if safer_random_move not in cells_tried:
                    cells_tried.add(safer_random_move)
                    num_of_cells_tried_repeatedly += 1

        return False

    def search_patterns(self):
        board = self.get_minesweeper_board()
        print("board: {}".format(board))
        pattern = [1, 2, 1]
        self.check_pattern(board, pattern)
        pattern = [1, 2, 2, 1]
        self.check_pattern(board, pattern)

        if self.width != self.height:
            raise ValueError("This algorithm is expecting the width and height to be the same size!!!")

        self.consecutive_ones_found_horizontally = []
        self.consecutive_ones_found_vertically = []
        for max_length in range(self.width, 2, -1):
            pattern = [1 for i in range(0, max_length)]
            self.check_pattern(board, pattern)

        # from scipy.ndimage import convolve

        # 2 3 2 pattern
        """
        kernel = [[1, 1, 1],
                  [0, 0, 0],
                  [0, 0, 0]]
        convolution = convolve(board, kernel, mode='constant')
        print("convolution:")
        print(convolution)
        """

        """
        
        pattern = [[2, 3, 2]]
        self.check_pattern(board, pattern)
        neighbors = self.find_pattern_indices(board, pattern)
        if len(neighbors) > 0:
            print("neighbors:")
            print(neighbors)

        pattern = [[2, 2, 1, 1]]
        self.check_pattern(board, pattern)
        neighbors = self.find_pattern_indices(board, pattern)
        if len(neighbors) > 0:
            print("neighbors:")
            print(neighbors)

        pattern = [[1, 1, 1]]
        self.check_pattern(board, pattern)
        neighbors = self.find_pattern_indices(board, pattern)
        if len(neighbors) > 0:
            print("neighbors:")
            print(neighbors)
        """

    def add_mine_known_by_ai(self, new_mine_cell, pattern_to_print=None):

        if pattern_to_print is not None:
            print("Found by the {} pattern, adding cell: {}".format(pattern_to_print, new_mine_cell))

        print("add_mines_known_by_ai:self.safes_known: {}".format(self.safes_known))

        if (0 < new_mine_cell[0] < self.height < self.height
                and new_mine_cell[1] > 0
                and new_mine_cell is not None):
            if new_mine_cell not in self.mines_known_by_ai and self.mine_is_not_false_negative(new_mine_cell):
                print("add_mines_known_by_ai:self.moves_made: {}".format(self.moves_made))
                print("Adding new known mine cell: {}".format(new_mine_cell))
                self.mines_known_by_ai.add(new_mine_cell)
        else:
            print("Cell is out of the canvas or None. Not doing anything.")

    def remove_mine_known_by_ai(self, new_mine_cell, row_or_column, vertically=False, pattern_to_print=None):
        if new_mine_cell not in self.moves_made:
            if (0 < new_mine_cell[0] < self.height < self.height
                    and new_mine_cell[1] > 0
                    and new_mine_cell is not None):

                print(
                    "Found by the pattern {}, removing the cell {} from the mines known by ai.".format(pattern_to_print,
                                                                                                       new_mine_cell))
                if new_mine_cell not in self.safes_known:
                    print("Adding the {} cell to safes known.".format(new_mine_cell))
                    self.safes_known.add(new_mine_cell)

                if new_mine_cell in self.mines_known_by_ai:
                    print("Removing the {} cell from known by ai".format(new_mine_cell))
                    self.mines_known_by_ai.remove(new_mine_cell)

                if vertically is False:
                    self.consecutive_ones_found_horizontally.append(row_or_column)
                else:
                    self.consecutive_ones_found_vertically.append(row_or_column)
            else:
                print("Cell is out of the canvas or None. Not doing anything.")

    def mine_is_not_false_negative(self, cells_to_check):
        try:
            if isinstance(cells_to_check, tuple):
                cells = set()
                cells.add(cells_to_check)
            elif isinstance(cells_to_check, list):
                cells = list(cells_to_check)
            elif isinstance(cells_to_check, set):
                cells = cells_to_check
            else:
                print(type(cells_to_check))
                raise ValueError("Unexpected type of the 'cells_to_check' variable.")

            print("cells: {}".format(cells))
            intersection_1 = set(cells).intersection(self.moves_made)
            intersection_2 = set(cells).intersection(self.safes_known)
            print("intersection_1: {}".format(intersection_1))
            print("intersection_2: {}".format(intersection_2))

            if intersection_1 or intersection_2 or cells_to_check in self.moves_made or cells_to_check in self.safes_known:
                return False
            else:
                return True

        except TypeError as e:
            print("cells_to_check: {}".format(cells_to_check))
            raise e

    def check_pattern(self, matrix, pattern):
        print("Checking pattern {}".format(pattern))

        # Check horizontally
        for row_number, row in enumerate(matrix):
            # print("row: {}, len(row): {}, len(pattern)-1: {}".format(row, len(row), len(pattern) - 1))
            for i in range(len(row) - len(pattern) - 1):
                if row_number not in self.consecutive_ones_found_horizontally:

                    # BOTH 22 in 1221 PATTERN ARE NOT ADDED TO THE MINES!!!

                    if row[i:i + len(pattern)] == pattern:
                        print("Pattern found horizontally")

                        # UPPER
                        if pattern == [1, 2, 1]:
                            new_mine_cell = (row_number - 1, i)
                            self.add_mine_known_by_ai(new_mine_cell, pattern)
                            new_mine_cell = (row_number - 1, i + (len(pattern) - 1))
                            self.add_mine_known_by_ai(new_mine_cell, pattern)
                        elif pattern == [1, 2, 2, 1]:
                            new_mine_cell = (row_number - 1, i + (len(pattern) - 2))
                            self.add_mine_known_by_ai(new_mine_cell, pattern)
                            new_mine_cell = (row_number - 1, i + 1)
                            self.add_mine_known_by_ai(new_mine_cell, pattern)
                        elif all(a in pattern for a in [1, 1, 1]):
                            # Add this to safes
                            # Remove this from ai_mines_known
                            new_mine_cell = (row_number - 1, i + (len(pattern) - 1))
                            # TODO: GET BACK OR NOT
                            # self.remove_mine_known_by_ai(new_mine_cell, row_number, pattern_to_print=pattern)
                        else:
                            raise ValueError("Pattern is not valid.")

                        # TODO: Rework this in the style of neighbors lower

                        # LOWER
                        if new_mine_cell is not None:

                            if pattern == [1, 2, 1]:
                                new_mine_cell = (row_number + 1, i)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (row_number + 1, i + (len(pattern) - 1))
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif pattern == [1, 2, 2, 1]:
                                new_mine_cell = (row_number + 1, i + (len(pattern) - 2))
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (row_number + 1, i + (len(pattern) - 3))
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif all(a in pattern for a in [1, 1, 1]):
                                new_mine_cell = (row_number + 1, i + (len(pattern) - 1))
                                # TODO: GET BACK OR NOT
                                # self.remove_mine_known_by_ai(new_mine_cell, row_number, pattern_to_print=pattern)
                            else:
                                raise ValueError("Pattern is not valid.")

        # Check vertically
        for col_num in range(len(matrix[0])):

            if col_num not in self.consecutive_ones_found_vertically:
                # print("len(matrix):")
                # print(len(matrix))
                for i in range(len(matrix) - (len(pattern) - 1)):

                    column_slice = [matrix[j][col_num] for j in range(i, i + len(pattern))]
                    # print("col_num: {}, i: {}, i + len(pattern): {}".format(col_num, i, i + len(pattern)))
                    # print("column_slice: {}".format(column_slice))
                    if col_num not in self.consecutive_ones_found_vertically:
                        # NEIGHBORS LEFT
                        if column_slice == pattern:

                            if pattern == [1, 2, 1]:
                                new_mine_cell = (i, col_num - 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (i + len(pattern) - 1, col_num - 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif pattern == [1, 2, 2, 1]:
                                new_mine_cell = (i + len(pattern) - 2, col_num - 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (i + 1, col_num - 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif all(a in pattern for a in [1, 1, 1]):
                                new_mine_cell = (i + len(pattern) - 1, col_num - 1)
                                # TODO: GET BACK OR NOT
                                # self.remove_mine_known_by_ai(new_mine_cell, col_num, True, pattern)
                            else:
                                raise ValueError("Pattern is not valid.")

                            """
                            print("col_num: {}, i: {}".format(col_num, i))
                            print("col_num: {}, i + len(pattern): {}".format(col_num, i + len(pattern)))
        
                            print("Neighbors right")
                            """

                            # NEIGHBORS RIGHT

                            if pattern == [1, 2, 1]:
                                new_mine_cell = (i, col_num + 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (i + len(pattern) - 1, col_num + 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif pattern == [1, 2, 2, 1]:
                                new_mine_cell = (i + len(pattern) - 2, col_num + 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                                new_mine_cell = (i + 1, col_num + 1)
                                self.add_mine_known_by_ai(new_mine_cell, pattern)
                            elif all(a in pattern for a in [1, 1, 1]):
                                new_mine_cell = (i + len(pattern) - 1, col_num + 1)
                                # TODO: GET BACK OR NOT
                                # self.remove_mine_known_by_ai(new_mine_cell, col_num, True, pattern)
                            else:
                                raise ValueError("Pattern is not valid.")

    def find_pattern_indices(self, matrix, pattern):
        pattern_height = len(pattern)
        pattern_width = len(pattern[0])

        # Initialize a list to store the indices of matching cells
        matching_indices = []

        # Check horizontally
        for row_index, row in enumerate(matrix):
            for i in range(len(row) - pattern_width + 1):
                if row[i:i + pattern_width] == pattern[0]:
                    # Add indices of matching cells in the current row
                    matching_indices.extend([(row_index, col_index) for col_index in range(i, i + pattern_width)])

        # Check vertically
        for col_index in range(len(matrix[0])):
            for i in range(len(matrix) - pattern_height + 1):
                column_slice = [matrix[j][col_index] for j in range(i, i + pattern_height)]
                if column_slice == pattern[0]:
                    # Add indices of matching cells in the current column
                    matching_indices.extend([(row_index, col_index) for row_index in range(i, i + pattern_height)])

        return matching_indices

    """
    def check_pattern(self, matrix, pattern):
        # TODO: Return the cells, not the boolean!

        cells_found = set()
        # Check horizontally
        width = self.width - 1
        height = self.height - 1

        for height_index, row in enumerate(matrix):
            for width_index in range(len(row) - 2):
                if row[width_index:width_index + len(pattern)] == pattern:
                    if pattern == [2, 3, 2]:
                        for width_coordinate in range(width_index, width_index + len(pattern)):
                            if height_index + 1 < height - 1 and width_coordinate < width - 1:
                                cells_found.add((height_index + 1, width_coordinate))

                            if height_index - 1 < 0 and width_coordinate < height - 1:
                                cells_found.add((height_index - 1, width_coordinate))
                    if pattern == [2, 2, 1, 1]:
                        if height_index + 1 < height and width_index < height:
                            print("These mines were found by the {} pattern: {}".format(str(pattern), cells_found))
                            self.mines_known_by_ai.add((height_index + 1, width_index))
                        if height_index + 1 < height and len(pattern) < height:
                            self.safes_known.add((height_index + 1, len(pattern)))
                        if height_index - 1 > 0 and width_index < height:
                            print("These mines were found by the {} pattern: {}".format(str(pattern), cells_found))
                            self.mines_known_by_ai.add((height_index - 1, width_index))
                        if height_index + 1 > 0 and width_index + len(pattern) < height:
                            self.safes_known.add((height_index + 1, width_index + len(pattern)))

        # Check vertically
        for width_index in range(len(matrix[0])):
            for height_index in range(len(matrix) - 2):
                print("height_index:")
                print(height_index)
                print("height_index + len(pattern):")
                print(height_index + len(pattern))
                if height_index + len(pattern) <= height:
                    max_height_index = height_index + len(pattern)
                else:
                    max_height_index = height

                column_slice = [matrix[j][width_index] for j in range(height_index, max_height_index)]
                if column_slice == pattern:
                    for j in range(height_index, height_index + len(pattern)):
                        if height_index < self.height and width_index + 1 < self.width:
                            if pattern == [2, 3, 2]:
                                cells_found.add((j, width_index + 1))
                            elif pattern == [2, 2, 1, 1]:
                                print("These mines were found by the {} pattern: {}".format(str(pattern), cells_found))
                                self.mines_known_by_ai.add((height_index, width_index + 1))

                        if height_index < self.height and width_index - 1 < self.width:
                            if pattern == [2, 3, 2]:
                                cells_found.add((j, width_index - 1))
                            elif pattern == [2, 2, 1, 1]:
                                print("These mines were found by the {} pattern: {}".format(str(pattern), cells_found))
                                self.mines_known_by_ai.add((height_index, width_index - 1))

        if len(cells_found) > 0:
            if pattern == [2, 3, 2]:
                print("These mines were found by the {} pattern: {}".format(str(pattern), cells_found))
                for cell in cells_found:
                    self.mines_known_by_ai.add(cell)
    """

    def cross_strategy(self, sentence, tested_neighbor_tuple):
        if (tested_neighbor_tuple[0] < self.height and tested_neighbor_tuple[0] > 0
                and tested_neighbor_tuple[1] < self.width and tested_neighbor_tuple[1] > 0):

            print("tested_neighbor_tuple: {}".format(tested_neighbor_tuple))
            print("self.moves_made: {}".format(self.moves_made))
            if tested_neighbor_tuple not in self.moves_made:
                if sentence.count == 0:
                    print("Based on the cross strategy, AI chose:")
                    print(tested_neighbor_tuple)
                    return tested_neighbor_tuple
                else:
                    print("Can't choose based on the cross strategy because the move has been already made.")
                    return None
            else:
                # print("Tested neighbor cell is not equal to the sentence cell.")
                return None
        else:
            print("Tested tuple {} is out of canvas.".format(tested_neighbor_tuple))

    def add_new_knowledge_with_new_cells(self, new_cells, new_count):

        print("new_cells {}".format(new_cells))
        print("new_count {}".format(new_count))

        if new_count >= 0:
            new_sentence = Sentence(new_cells, new_count)

            print("add_new_knowledge_with_new_cells.new_sentence:")
            print(new_sentence)

            if new_sentence not in self.knowledge:
                print("Adding the calculated cells based on the cell counts:")
                self.knowledge.append(new_sentence)
            # print("Updated knowledge:")
            # self.print_knowledge()

    def print_knowledge(self):
        print("------------------------")
        print("self.knowledge:")
        for sentence in self.knowledge:
            print(sentence)
        print("------------------------")

    def update_board(self, move, count):
        # print("Old board: {}".format(self.board))

        self.board[move[0]][move[1]] = count
        # print("New board: {}".format(self.board))

    def update_mines_known_by_ai(self):

        intersection = self.mines_known_by_ai.intersection(self.mines_known)
        self.mines_known_by_ai = self.mines_known_by_ai - intersection

        intersection = self.mines_known_by_ai.intersection(self.moves_made)
        self.mines_known_by_ai = self.mines_known_by_ai - intersection

        intersection = self.mines_known_by_ai.intersection(self.safes_known)
        self.mines_known_by_ai = self.mines_known_by_ai - intersection

        intersection = self.mines_known_by_ai.intersection(self.mines_flagged)
        self.mines_known_by_ai = self.mines_known_by_ai - intersection

    def get_from_safes_and_non_suspected(self, suspected_cells):
        print("safe_choices: {}".format(self.safes_known))
        print("self.suspected_mines_mild_danger: {}".format(suspected_cells))
        safe_and_non_suspected_choices = self.safes_known - suspected_cells - self.moves_made
        print("safe_and_non_suspected_choices: {}".format(safe_and_non_suspected_choices))
        print(suspected_cells)
        suspected_cells_filtered_from_moves_made = set()
        for cell in safe_and_non_suspected_choices:
            print("cell: {}".format(cell))
            print("self.moves_made: {}".format(self.moves_made))
            if cell not in self.moves_made:
                suspected_cells_filtered_from_moves_made.add(cell)
        if len(suspected_cells_filtered_from_moves_made) > 0:
            print("Making a move based on the RANDOM FROM NON-SUSPECTED strategy.")
            random_cell_from_non_suspected = get_random_item_from_set(suspected_cells_filtered_from_moves_made)
            return random_cell_from_non_suspected

        return False

    def get_cell_with_lowest_sum_of_neighbourhood(self, threshold, subset=None):
        sum_of_cells_and_neighbourhoods = []
        cell_and_neighborhood_sum = {}
        mine_probability_of_sum_of_neighbors = None
        this_cell_in_subset = False
        for i in range(0, self.width):
            for j in range(0, self.height):
                if ((i, j) not in self.moves_made and (i, j) not in self.mines_known and (i, j)
                        not in self.mines_known_by_ai):
                    if subset is not None:
                        if (i, j) not in subset:
                            continue
                    # print((i, j))
                    # print(self.moves_made)
                    # print(self.mines_known)
                    cell_and_neighborhood_sum['cell'] = (i, j)
                    neighbor_cells = self.get_neighbor_cells((i, j), 'only-known')
                    if len(neighbor_cells) == 0:
                        continue
                    cell_and_neighborhood_sum['sum'] \
                        = (self.get_neighbor_cells_sum((i, j), 'only-known')
                           / len(neighbor_cells))
                    if cell_and_neighborhood_sum not in sum_of_cells_and_neighbourhoods:
                        sum_of_cells_and_neighbourhoods.append(cell_and_neighborhood_sum)
                        # calculate probability
                        neighbor_cells_to_consider = []
                        for neighbor_cell in neighbor_cells:
                            if neighbor_cell not in self.moves_made:
                                neighbor_cells_to_consider.append(neighbor_cell)
                                mine_probability_of_sum_of_neighbors = self.get_probabilities(neighbor_cell,
                                                                                              len(neighbor_cells_to_consider))[
                                    1]

        if mine_probability_of_sum_of_neighbors is not None:
            if len(sum_of_cells_and_neighbourhoods) > 0:
                sorted_sums_of_cells = sorted(sum_of_cells_and_neighbourhoods, key=lambda d: d['sum'])
                print("sorted_sums_of_cells:")
                for item in sorted_sums_of_cells:
                    print(item)
                if sorted_sums_of_cells[0]['sum'] < threshold:
                    mine_probability_of_random = self.get_probabilities()
                    if mine_probability_of_sum_of_neighbors < mine_probability_of_random:
                        print(
                            "Found by the lowest sum of neighbourhood cells strategy. Threshold: {}".format(threshold))
                        return sorted_sums_of_cells[0]['cell']
                    else:
                        print("Random has greater probability to succeed. Skipping SUM OF NEIGHBOUR strategy.")
                else:
                    return False
            else:
                return False

    def get_cell_with_lowest_probability_of_mine_in_neighborhood(self):

        options = []
        for move_made in self.moves_made:
            neighbor_cells_known = self.get_neighbor_cells(move_made, 'only-known')
            neighbor_cells_all = self.get_neighbor_cells(move_made, 'all')
            neighbor_cells_open = set(neighbor_cells_all) - set(neighbor_cells_known)
            print("neighbor_cells_open: {}".format(neighbor_cells_open))
            num_of_neighbor_cells_open = len(neighbor_cells_open)
            if num_of_neighbor_cells_open < 1:
                continue
            random_move_mine_probability, safer_random_mine_probability \
                = self.get_probabilities(move_made, num_of_neighbor_cells_open)

            if safer_random_mine_probability < random_move_mine_probability:
                for open_cell in neighbor_cells_open:
                    if open_cell not in self.moves_made:
                        option = {'cell': open_cell, 'probability': safer_random_mine_probability}
                        options.append(option)
                        print("Probability for {}, neighbor of: {}:".format(open_cell, move_made))
                        print(safer_random_mine_probability)
                        print(random_move_mine_probability)

        if len(options) > 0:
            sorted_cells_with_probabilities = sorted(options, key=lambda d: d['probability'])

            # IF CANNOT BE CONCLUDED, DO LOWEST SUM
            last_probability = None

            subset = min(sorted_cells_with_probabilities, key=lambda x: x['probability'])

            if len(subset) > 1:
                second_strategy = self.get_cell_with_lowest_sum_of_neighbourhood(1.33, subset)
                if second_strategy is not None:
                    print("Using CELL WITH THE LOWEST PROBABILITY + SUM OF NEIGHBOUR strategy")
                    return second_strategy

                second_strategy = self.get_cell_with_lowest_sum_of_neighbourhood(1.5, subset)
                if second_strategy is not None:
                    print("Using CELL WITH THE LOWEST PROBABILITY + SUM OF NEIGHBOUR strategy")
                    return second_strategy
            else:
                print("Used the CELL WITH THE LOWEST PROBABILITY OF A MINE strategy.")
                print("From options:")
                print(options)
                return subset[0]['cell']

        return False


def powerset(iterable):
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))


def get_random_item_from_set(cells):
    set_length = len(cells) - 1
    try:
        random_index_from_set = random.randrange(set_length)
    except ValueError:
        random_index_from_set = 0

    random_element_from_set = list(cells)[random_index_from_set]
    print(random_element_from_set)
    return tuple(random_element_from_set)
