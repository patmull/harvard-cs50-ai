from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

general_knowledge_1 = Or(AKnight, AKnave)
general_knowledge_2 = Or(BKnight, BKnave)
general_knowledge_3 = Not(And(AKnight, AKnave))
general_knowledge_4 = Not(And(BKnight, BKnave))

# The general knowledge needs to be there, otherwise there is too much of possibilities from
# which it can be concluded.
general_knowledge = And(
    general_knowledge_1, general_knowledge_2, general_knowledge_3, general_knowledge_4
)

# ASaid = Or(AKnight, AKnave)

# Puzzle 0
# A says "I am both a knight and a knave."
ASaid = And(AKnight, AKnave)

# Encoding of the fact that Knave lies and knight not
general_knowledge_with_sentence_1 = Implication(AKnight, ASaid)
general_knowledge_with_sentence_2 = Implication(AKnave, Not(ASaid))

knowledge0 = And(
    # TODO
    general_knowledge,

    general_knowledge_with_sentence_1,
    general_knowledge_with_sentence_2
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
ASaid = And(AKnave, BKnave)

general_knowledge_with_sentence_1_a = Implication(AKnight, ASaid)
general_knowledge_with_sentence_2_a = Implication(AKnave, Not(ASaid))

knowledge1 = And(
    # TODO
    general_knowledge,

    general_knowledge_with_sentence_1_a,
    general_knowledge_with_sentence_2_a,

)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
ASaid = Biconditional(AKnight, BKnight)
BSaid_1 = Not(Biconditional(AKnave, BKnave))
BSaid_2 = Not(Biconditional(AKnight, BKnight))
BSaid = And(BSaid_1, BSaid_2)

general_knowledge_with_sentence_1_a = Implication(AKnight, ASaid)
general_knowledge_with_sentence_2_a = Implication(AKnave, Not(ASaid))
general_knowledge_with_sentence_1_b = Implication(BKnight, BSaid)
general_knowledge_with_sentence_2_b = Implication(BKnave, Not(BSaid))

knowledge2 = And(
    general_knowledge,

    general_knowledge_with_sentence_1_a,
    general_knowledge_with_sentence_2_a,
    general_knowledge_with_sentence_1_b,
    general_knowledge_with_sentence_2_b
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
ASaid = Or(AKnight, AKnave)
BSaid1 = And(ASaid, AKnave)
BSaid2 = CKnave
BSaid = And(BSaid1, BSaid2)
CSaid = AKnight

general_knowledge_with_sentence_1_a = Implication(AKnight, ASaid)
general_knowledge_with_sentence_2_a = Implication(AKnave, Not(ASaid))
# TODO:
general_knowledge_with_sentence_1_b = Implication(BKnight, CKnave)
general_knowledge_with_sentence_2_b = Implication(BKnave, Not(CKnave))
# OK:
general_knowledge_with_sentence_1_c = Implication(CKnight, CSaid)
general_knowledge_with_sentence_2_c = Implication(CKnave, Not(CSaid))

knowledge3 = And(
    general_knowledge,

    general_knowledge_with_sentence_1_a,
    general_knowledge_with_sentence_2_a,
    general_knowledge_with_sentence_1_b,
    general_knowledge_with_sentence_2_b,
    general_knowledge_with_sentence_1_c,
    general_knowledge_with_sentence_2_c
)

"""
PROBABLY RIGHT SOLUTION:

# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO
    Implication(ASaid, And(AKnight, AKnave))
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO
    Implication(ASaid, And(AKnave, BKnave)),
    Not(BSaid)
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO
    Implication(ASaid, Biconditional(AKnight, BKnight)),
    Implication(BSaid, Biconditional(AKnight, Not(BKnight)))
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    Biconditional(ASaid, Or(AKnight, AKnave)),
    Biconditional(BSaid, ASaid),
    Biconditional(BSaid, CKnave),
    Biconditional(CSaid, AKnight)
)
"""


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
