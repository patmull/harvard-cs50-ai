import itertools
import random
import traceback
import iteration_utilities


class Minesweeper():
    """
    Minesweeper game representation
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
        return self.mines_found == self.mines


# We know the exact value of these cells
class Sentence():
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
        print("Sentence.cells: {}".format(cells))
        print(type(cells))
        if isinstance(cells, tuple):
            if cells not in self.cells:
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


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8, mines_flagged=None):

        # Set initial height and width
        if mines_flagged is None:
            self.mines_flagged = set()
        else:
            self.mines_flagged = mines_flagged

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

        # List of sentences about the game known to be true
        self.knowledge = []

    def get_minesweeper_board(self):
        board = [[0 for width_index in range(self.width)] for height_index in range(self.height)]

        for sentence in self.knowledge:
            for cell in sentence.cells:
                board[cell[0]][cell[1]] = sentence.count

        return board

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

    def add_cells_to_knowledge(self, cells, count):
        new_sentence = Sentence(cells, count)
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
            # print("cell: {}".format(cell))
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

    def get_neighbor_cells_sum(self, cell, types=None):

        # 1. iterate through knowledge for the counts
        # 2. check whether the cells in knowledge (sentence.cells) are neighbor cells of the input cell
        neighbor_cells = self.get_neighbor_cells(cell, types="All")
        neighbor_cells_sum = 0

        if len(neighbor_cells) > 0:

            for sentence in self.knowledge:
                for knowledge_cell in sentence.cells:
                    if knowledge_cell in neighbor_cells:
                        neighbor_cells_sum += sentence.count

        return neighbor_cells_sum

    def get_neighbor_cells(self, cell, types=None):

        if types is None:
            raise ValueError("types argument needs to be specified!")

        all_types = False
        if str.lower(types) == "all":
            all_types = True

        returned_cells = []
        if "bottom-neighbor" in types or all_types:
            # bottom neighbor
            if cell[0] < self.height - 1:
                # print(type(cell))
                # print("cell[0]: {}".format(cell[0]))
                # print("cell[1]: {}".format(cell[1]))

                safe_height = cell[0] + 1
                safe_width = cell[1]
                new_safe_cell = (safe_height, safe_width)
                # print("bottom neighbor")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if "upper-neighbor" in types or all_types:
            # upper neighbor
            if cell[0] > 0:
                safe_height = cell[0] - 1
                safe_width = cell[1]
                new_safe_cell = (safe_height, safe_width)

                # print("upper neighbor")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if "left-neighbor" in types or all_types:
            # left neighbor
            if cell[1] > 0:
                safe_height = cell[0]
                safe_width = cell[1] - 1
                new_safe_cell = (safe_height, safe_width)

                # print("left neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if "right-neighbor" in types or all_types:
            # right neighbor
            if cell[1] < self.width - 1:
                safe_height = cell[0]
                safe_width = cell[1] + 1
                new_safe_cell = (safe_height, safe_width)

                # print("right neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if "left-upper-corner" in types or all_types:
            # left upper corner neighbor
            if cell[0] > 0 and cell[1] > 0:
                safe_height = cell[0] - 1
                safe_width = cell[1] - 1
                new_safe_cell = (safe_height, safe_width)

                # print("left upper corner neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if "right-upper-corner" in types or all_types:
            # right upper corner neighbor
            if cell[0] > 0 and cell[1] < self.width - 1:
                safe_height = cell[0] - 1
                safe_width = cell[1] + 1
                new_safe_cell = (safe_height, safe_width)

                # print("right upper corner neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if type == "left-bottom-corner" or all_types:
            # left bottom corner neighbor
            if cell[0] < self.height - 1 and cell[1] > 0:
                safe_height = cell[0] + 1
                safe_width = cell[1] - 1
                new_safe_cell = (safe_height, safe_width)

                # print("left bottom corner neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)
                # new_sentence = Sentence(new_safe_cell, 0)
                # self.knowledge.append(new_sentence)

        if type == "right-bottom-corner" or all_types:
            # right bottom corner neighbor
            if cell[0] < self.height - 1 and cell[1] < self.width - 1:
                safe_height = cell[0] + 1
                safe_width = cell[1] + 1
                new_safe_cell = (safe_height, safe_width)

                # print("right bottom corner neighbor:")
                # print("cell: {}".format(cell))
                # print("new_safe_cell: {}".format(new_safe_cell))

                returned_cells.append(new_safe_cell)

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

        # Simplest strategy: pick the cells around the zero
        if count == 0:

            # new_sentence = Sentence(new_safe_cell, 0)
            # self.knowledge.append(new_sentence)
            # TODO:
            new_safe_cells = self.get_neighbor_cells(cell, "all")

            print("new_safe_cells")
            print(new_safe_cells)
            print("set(new_safe_cells)")
            print(set(new_safe_cells))

            self.add_cells_to_knowledge(set(new_safe_cells), 0)

            for cell in new_safe_cells:
                print("Marking safe cells picked on the simple neighbor zeros strategy")
                self.mark_safe(cell)

        self.update_knowledge(cell)

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

        for sentence in self.knowledge:
            if sentence.count == 0:
                # THE NEIGHBOR ZEROS STRATEGY
                # This should do the trick for not uncovering unnecessary cells
                if len(sentence.cells) > 0:
                    for cell in sentence.cells:
                        if (cell not in self.mines_known_by_ai and cell not in self.mines_known
                                and cell not in self.moves_made):
                            print("THE NEIGHBOR ZEROS STRATEGY")
                            return cell

                # IF CANNOT BE CONCLUDED, DO PREP FOR ANOTHER STRATEGIES
                if len(sentence.cells) > 0:
                    print("if sentence.count:sentence.cells {}".format(sentence.cells))
                    new_safe_cells = list(sentence.cells)[0]
                    safes_known_from_knowledge.add(new_safe_cells)

        print("safes_known_from_knowledge: {}".format(safes_known_from_knowledge))
        print("self.safes_known: {}".format(self.safes_known))
        print("self.moves_made")
        print(self.moves_made)

        if len(safes_known_from_knowledge) == 0:
            return None

        # Filter moves already made
        safe_choices = set()
        for safe_cell in safes_known_from_knowledge:
            if safe_cell not in self.moves_made:
                safe_choices.add(safe_cell)

        for safe_cell in self.safes_known:
            if safe_cell not in self.moves_made:
                safe_choices.add(safe_cell)

        print("safe_choices")
        print(safe_choices)

        if len(safe_choices) > 0:
            safes_set_length = len(safe_choices) - 1
            print("safe_choices")
            print(safe_choices)

            for safe_choice in safe_choices:

                if safe_choice not in self.moves_made:
                    # print("safe_choice:")
                    # print(safe_choice)
                    # print("sentence.cells:")
                    # print(sentence.cells)
                    for sentence_2 in self.knowledge:
                        # print("safe_choice[0], safe_choice[1] - 1:")
                        # print(safe_choice[0], safe_choice[1] - 1)

                        # THE CROSS OF ZEROS STRATEGY

                        tested_tuple = (safe_choice[0], safe_choice[1] - 1)
                        cells = self.cross_strategy(sentence_2, tested_tuple)
                        if cells is not None:
                            return cells

                        tested_tuple = (safe_choice[0], safe_choice[1] + 1)
                        cells = self.cross_strategy(sentence_2, tested_tuple)
                        if cells is not None:
                            return cells

                        tested_tuple = (safe_choice[0] + 1, safe_choice[1])
                        cells = self.cross_strategy(sentence_2, tested_tuple)
                        if cells is not None:
                            return cells

                        tested_tuple = (safe_choice[0] - 1, safe_choice[1])
                        cells = self.cross_strategy(sentence_2, tested_tuple)
                        if cells is not None:
                            return cells

            for sentence in self.knowledge:
                # If we know it's zero, then make the move
                print("sentence.cells[0]")
                print(list(sentence.cells)[0])
                print("self.moves_made: {}".format(self.moves_made))
                if list(sentence.cells)[0] not in self.moves_made:
                    if sentence.count == 0:
                        print("Based on the pick zero immediately strategy, AI chose:")
                        print(sentence.cells)
                        return tuple(list(sentence.cells)[0])

            # RANDOM FROM SAFES STRATEGY
            print("")
            safe_choices = [[item for item in pair] for pair in safe_choices]

            if len(safe_choices) > 0:

                try:
                    random_index_from_set = random.randrange(safes_set_length)
                except ValueError:
                    random_index_from_set = 0

                random_element_from_set = list(safe_choices)[random_index_from_set]
                print("Making random move from safe choices.")
                print(random_element_from_set)
                return tuple(random_element_from_set)

            # RANDOM FROM NON-MINES STRATEGY
            # last resort is simply choose random from non-mines, because there is no other way to choose
            # This differs from the pure random move below
            random_move = self.make_random_move()

            if random_move not in self.mines_known_by_ai:
                print("Making random move from known non-mines.")
                return random_move

        else:
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines_known
        """
        print("make_random_move")
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
                        return (random_move_i, random_move_j)

                # We pick randomly but only those which are in safe

                if ((random_move_i, random_move_j) not in self.moves_made
                        and (random_move_i, random_move_j) in self.safes_known):
                    print("Random move:")
                    print("random_move_i, random_move_j")
                    added_move = (random_move_i, random_move_j)

                    return added_move
                else:
                    options_tried.add((random_move_i, random_move_j))

    def update_knowledge(self, cell):
        # self.print_knowledge()
        knowledge = self.knowledge.copy()
        print("----------------------")
        print("knowledge:")
        for sentence in knowledge:
            print(sentence)
        print("-----------------------")
        count_control = 0

        for i in range(len(knowledge)):
            for j in range(len(knowledge)):
                # count_control += 1
                if len(knowledge[i].cells) > 0 and len(knowledge[j].cells) > 0:
                    if knowledge[i].cells.issubset(knowledge[j].cells):
                        # self.print_knowledge()
                        # print("knowledge[j].cells: {}".format(knowledge[j].cells))
                        # print("knowledge[i].cells: {}".format(knowledge[i].cells))
                        new_cells = knowledge[j].cells.difference(knowledge[i].cells)
                        print("new_cells: {}".format(new_cells))
                        print(len(new_cells))
                        if len(new_cells) >= 0:
                            self.add_new_knowledge_with_new_cells(new_cells, knowledge[i].count, knowledge[j].count,
                                                                  True)
                            new_count = knowledge[j].count - knowledge[i].count

                            # print("new_cells {}".format(new_cells))
                            # print("new_count {}".format(new_count))

                            # print("update_knowledge.type(new_cells):")
                            # print(type(new_cells))

                            if new_count > 0:
                                new_sentence = Sentence(new_cells, new_count)
                                if new_sentence not in self.knowledge:
                                    print("Adding the calculated cells based on the cell counts:")
                                    self.knowledge.append(new_sentence)
                                print("Updated knowledge:")
                                # self.print_knowledge()
                        else:
                            raise ValueError("Unexpected length of the cells.")
                """
                if count_control > (self.width * self.height):
                    break
                """
        # Searching for the cell in the knowledge
        found_cell = tuple()
        cell_count = None
        for sentence in self.knowledge:
            if sentence.cells == cell:
                found_cell = sentence.cells
                cell_count = sentence.count

        # SUM OF NEIGHBORS STRATEGY
        # IF SUM OF THE CELL'S NEIGHBORS IS EQUAL TO THE COUNT, NEIGHBOUR ARE MINES

        neighbor_cells_sum = self.get_neighbor_cells_sum(cell)
        neighbor_cells = self.get_neighbor_cells(cell, "all")

        if neighbor_cells_sum == cell_count:
            print("Marking mines_known by the sum of neighbors strategy")
            for neighbor_cell in neighbor_cells:
                self.mines_known_by_ai.add(neighbor_cell)

        # THE CALCULATIONS FROM HW ABOUT SAFES AND MINES:
        for sentence in self.knowledge:
            known_mines = sentence.known_mines()
            for known_mine_cell in known_mines:
                self.mines_known_by_ai.add(known_mine_cell)

        for sentence in self.knowledge:
            known_safes = sentence.known_safes()
            for known_safe_cell in known_safes:
                self.safes_known.add(known_safe_cell)

        # FLAGGED NEIGHBOR STRATEGY
        # IF CELL HAS FLAGGED NEIGHBOR
        # AND THE CELL COUNT IS EQUAL TO THE FLAGGED NEIGHBOR COUNT
        # ALL OTHER NEIGHBORS ARE SAFE

        print("self.mines_flagged:")
        print(self.mines_flagged)
        for mine_cell in self.mines_flagged:
            if mine_cell in neighbor_cells:
                sentence_about_mine_cell = self.find_sentence_by_cell(mine_cell)
                sentence_about_cell = self.find_sentence_by_cell(cell)

                if sentence_about_mine_cell is not None and sentence_about_cell is not None:

                    if sentence_about_cell.count == sentence_about_mine_cell.count:
                        print("Marking safe by the FLAGGED NEIGHBOR STRATEGY strategy")
                        print("neighbor_cells")
                        print(neighbor_cells)
                        for neighbor_cell in neighbor_cells:
                            self.mark_safe(neighbor_cell)

        # Patterns finding strategy (https://www.youtube.com/watch?v=6vcSO7h6Nt0)
        self.search_patterns()

    def search_patterns(self):
        board = self.get_minesweeper_board()

        from scipy.ndimage import convolve

        # 2 3 2 pattern
        """
        kernel = [[1, 1, 1],
                  [0, 0, 0],
                  [0, 0, 0]]
        convolution = convolve(board, kernel, mode='constant')
        print("convolution:")
        print(convolution)
        """

        pattern = [[2, 3, 2]]
        self.check_pattern(board, pattern)

    def check_pattern(self, matrix, pattern):
        # TODO: Return the cells, not the boolean!

        # Check horizontally
        for row in matrix:
            for i in range(len(row) - 2):
                if row[i:i + 3] == pattern[0]:
                    return True

        # Check vertically
        for col in range(len(matrix[0])):
            for i in range(len(matrix) - 2):
                column_slice = [matrix[j][col] for j in range(i, i + 3)]
                if column_slice == pattern[0]:
                    return True

        return False

    def cross_strategy(self, sentence, tested_neighbor_tuple):
        tested_cells = list(sentence.cells)
        for tested_cell in tested_cells:
            if tested_cell == tested_neighbor_tuple:
                if tested_cell not in self.moves_made:
                    if sentence.count == 0:
                        print("Based on the cross strategy, AI chose:")
                        print(tested_cell)
                        return tuple(list(sentence.cells)[0])
                else:
                    print("Can't choose based on the cross strategy because the move has been already made.")
                    return None
            else:
                # print("Tested neighbor cell is not equal to the sentence cell.")
                return None

    def add_new_knowledge_with_new_cells(self, new_cells, count1, count2, individual=True):

        new_count = count2 - count1

        print("new_cells {}".format(new_cells))
        print("new_count {}".format(new_count))

        if new_count >= 0:
            new_sentence = Sentence(new_cells, new_count)

            print("add_new_knowledge_with_new_cells.new_sentence:")
            print(new_sentence)

            if new_sentence not in self.knowledge:
                print("Adding the calculated cells based on the cell counts:")
                self.knowledge.append(new_sentence)
            print("Updated knowledge:")
            # self.print_knowledge()

    def print_knowledge(self):
        print("------------------------")
        print("self.knowledge:")
        for sentence in self.knowledge:
            print(sentence)
        print("------------------------")


class Helpers:

    def powerset(self, iterable):
        s = list(iterable)
        return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s) + 1))
