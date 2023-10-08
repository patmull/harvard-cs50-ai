import csv
import itertools
import random
import sys
import numpy as np

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():
    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # TEST joint_probability
    test_one_gene = {"Harry"}
    test_two_gene = {"James"}
    test_has_trait = {"James"}

    test_individual = 'Harry'
    test_characteristics = {'mother': 'Lily', 'father': 'James', 'name': 'Harry'}
    test_p = joint_probability(people, test_one_gene, test_two_gene, test_has_trait)
    print("test_p")
    print(test_p)

    assert round(test_p, 4) == round(0.0026643247488, 4)

    test_one_gene = {"Harry"}
    test_two_gene = {"James"}

    test_p = asses_inherited_probability(people, test_one_gene, test_two_gene, test_characteristics)
    print("test_p")
    print(test_p)

    # assert round(test_p, 4) == round(0.9801, 4)

    test_one_gene = {}
    test_two_gene = {"James"}
    test_p = asses_inherited_probability(people, test_one_gene, test_two_gene, test_characteristics)
    print("test_p")
    print(test_p)

    # assert round(test_p, 4) == round(0.0099, 4)

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):
                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def inherited_probability(people_genes, parent):
    """
    For anyone with parents in the data set, each parent will pass one of their two genes on to their child randomly,
    and there is a PROBS["mutation"] chance that it mutates (goes from being the gene to not being the gene, or vice versa).
    """

    if people_genes[parent] == 0:
        prob_of_parent_gene = PROBS["mutation"]
        prob_of_not_getting_parent_gene = 1 - PROBS["mutation"]
    elif people_genes[parent] == 1:
        prob_of_parent_gene = 0.5
        prob_of_not_getting_parent_gene = 0.5
    elif people_genes[parent] == 2:
        prob_of_parent_gene = 1 - PROBS["mutation"]
        prob_of_not_getting_parent_gene = PROBS["mutation"]
    else:
        raise ValueError("This number of people gene not allowed. Must be 0, 1 or 2.")

    return prob_of_parent_gene, prob_of_not_getting_parent_gene


# I tried probability_of_current_copy_from_parents = ((prob_of_father_gene * prob_of_mother_gene))
# and no addition of random mutation for 0.5
# This is working for family0.csv!!!

def asses_inherited_probability(people, one_gene, two_genes, characteristics):
    people_genes = {}
    individual = characteristics['name']

    for _individual, _characteristics in people.items():
        if _individual in one_gene:
            people_genes[_individual] = 1
        elif _individual in two_genes:
            people_genes[_individual] = 2
        else:
            people_genes[_individual] = 0

    parent_mother = characteristics['mother']
    parent_father = characteristics['father']

    # probability_of_current_copy += probability_of_current_copy_from_parents
    prob_of_mother_gene, prob_of_not_mother_gene = inherited_probability(people_genes, parent_mother)
    prob_of_father_gene, prob_of_not_father_gene = inherited_probability(people_genes, parent_father)
    if people_genes[individual] == 0:
        """
        There is only one way this can happen.
        Person does not receive the gene from the parents
        """
        probability_of_current_copy_from_parents = prob_of_not_mother_gene * prob_of_not_father_gene

    elif people_genes[individual] == 1:
        """
        There are two ways this can happen. 
        Either he gets the gene from his mother AND not his father, 
        OR he gets the gene from his father AND not his mother.
        """
        probability_of_current_copy_from_parents = (prob_of_mother_gene * prob_of_not_father_gene
                                                    + prob_of_father_gene * prob_of_not_mother_gene)

    elif people_genes[individual] == 2:
        """
        He gets the genes from his father AND his mother 
        OR both from father AND not mother
        OR both from mother
        """
        probability_of_current_copy_from_parents = prob_of_father_gene * prob_of_mother_gene
        # + prob_of_father_gene**2
        # + prob_of_mother_gene**2)
    else:
        raise ValueError("This number of people gene not allowed. Must be 0, 1 or 2.")

    return probability_of_current_copy_from_parents


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    print(people)
    print(one_gene)
    print(two_genes)
    print(have_trait)

    joint_probability_of_trait = 0
    gene_probability_distributions = {}
    people_genes = {}

    for individual, characteristics in people.items():
        if individual in one_gene:
            people_genes[individual] = 1
        elif individual in two_genes:
            people_genes[individual] = 2
        else:
            people_genes[individual] = 0

    for individual, characteristics in people.items():
        """
            # For anyone with no parents listed in the data set, use the probability distribution PROBS["gene"] 
            # to determine the probability that they have a particular number of the gene.
        """

        if characteristics['mother'] is None or characteristics['father'] is None:
            if people_genes[individual] == 0:
                probability_of_current_copy = PROBS["gene"][0]
            elif people_genes[individual] == 1:
                probability_of_current_copy = PROBS["gene"][1]
            elif people_genes[individual] == 2:
                probability_of_current_copy = PROBS['gene'][2]
            else:
                raise ValueError("This number of people gene not allowed. Must be 0, 1 or 2.")

            gene_probability_distributions[individual] = probability_of_current_copy
        else:

            """
            if people_genes[parent_mother] == 0 and people_genes[parent_father] == 0:
                probability_of_current_copy_from_parents = PROBS["mutation"]
            else:
            """
            probability_of_current_copy = asses_inherited_probability(people, one_gene, two_genes, characteristics)
            gene_probability_distributions[individual] = probability_of_current_copy

    # ** HERE WAS RANDOM MANIPULATION WITH GENES** ADDED, PROBABLY NOT NEEDED

    print("people_genes:")
    print(people_genes)

    people_traits = {}
    trait_probability = {}

    # TODO: Switch back to count not only parents after it is resolved
    for individual, gene in people_genes.items():
        # **HERE WAS MY OWN RANDOM MUTATION FEATURE**
        # NOTE: I added this to take into a fact the distribution. The results will differ based on the random choice,
        # but on average should correspond to the right result of example on HW:
        # {'Harry': 0.4313, 'James': 0.0065, 'Lily': 0.9504}

        if individual in have_trait:
            individual_has_trait = True
        else:
            individual_has_trait = False

        trait_probability[individual] = PROBS["trait"][gene][individual_has_trait]
        trait_probability[individual] = round(trait_probability[individual], 4)

    print("people_traits:")
    print(people_traits)

    print("trait_probability")
    print(trait_probability)

    # Calculate joint probability. Return the joint probability of all of
    # those events taking place (how many copies of each of the genes, and who exhibits the trait).
    # copies = numer 0, 1 or 2

    joint_probability_result = 1

    assert len(gene_probability_distributions) == len(trait_probability)
    for individual, prob_value in gene_probability_distributions.items():
        joint_probability_result *= (gene_probability_distributions[individual] * trait_probability[individual])

    return joint_probability_result


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for individual, characteristics in probabilities.items():

        if individual in two_genes:
            probabilities[individual]["gene"][2] += p
        elif individual in one_gene:
            probabilities[individual]["gene"][1] += p
        else:
            probabilities[individual]["gene"][0] += p

        if individual in have_trait:
            probabilities[individual]["trait"][True] += p
        else:
            probabilities[individual]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    print("probabilities:")
    print(probabilities)

    for individual, person_attributes in probabilities.items():
        for attribute_name, attribute_value_names in person_attributes.items():
            factor = 1.0 / sum(probabilities[individual][attribute_name].values())
            for attribute_value_name in attribute_value_names:
                probabilities[individual][attribute_name][attribute_value_name] \
                    = probabilities[individual][attribute_name][attribute_value_name] * factor


if __name__ == "__main__":
    main()
