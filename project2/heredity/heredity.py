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

    test_p = joint_probability(people, test_one_gene, test_two_gene, test_has_trait)
    print("test_p")
    print(test_p)

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

                # TODO: TRAIT OK FOR JAMES AND LILY, REST IS WRONG

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


def probability_of_parent_gene(people_genes, parent, parents):
    # TODO: This does not hold universally. This holds only if one parent has zero copies!

    probs_of_parent_genes = {}
    one_parent_zero_copies = False

    for parent in parents:
        if people_genes[parent] == 0:
            one_parent_zero_copies = True

    # if one_parent_zero_copies:

    if people_genes[parent] == 0:
        prob_of_parent_gene = PROBS["mutation"]
        prob_of_not_getting_parent_gene = 1-PROBS["mutation"]
    else:
        prob_of_parent_gene = 1 - PROBS["mutation"]
        prob_of_not_getting_parent_gene = PROBS["mutation"]

    return prob_of_parent_gene, prob_of_not_getting_parent_gene

    """
    else:
        raise NotImplementedError
    """

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

        # TODO: When this should be adopted?
        # if characteristics['mother'] is None and characteristics['father'] is None:

        if individual in one_gene:
            probability_of_current_copy = PROBS["gene"][1]
            people_genes[individual] = 1
        elif individual in two_genes:
            probability_of_current_copy = PROBS["gene"][2]
            people_genes[individual] = 2
        else:
            probability_of_current_copy = PROBS['gene'][0]
            people_genes[individual] = 0

        gene_probability_distributions[individual] = probability_of_current_copy

    for individual, characteristics in people.items():
        if characteristics['mother'] is not None and characteristics['father'] is not None:

            parent_mother = characteristics['mother']
            parent_father = characteristics['father']

            prob_of_mother_gene, prob_of_not_mother_gene = probability_of_parent_gene(people_genes, parent_mother, {parent_mother, parent_father})
            prob_of_father_gene, prob_of_not_father_gene = probability_of_parent_gene(people_genes, parent_father, {parent_mother, parent_father})

            probability_of_current_copy = (prob_of_not_mother_gene * prob_of_not_father_gene
                                           + prob_of_father_gene * prob_of_mother_gene)

            gene_probability_distributions[individual] = probability_of_current_copy

    people_copy_probability = {}

    # genes for the individual considering the probability of having the gene
    for individual, gene_by_distribution in gene_probability_distributions.items():
        """
        gene_by_distribution = np.random.choice(list(gene_probability_distribution), 1,
                                                p=list(gene_probability_distribution), replace=False)
        gene_by_distribution = int(gene_by_distribution[0])
        """

        people_copy_probability[individual] = PROBS["gene"][people_genes[individual]]

        """
        # TODO: Get this back
        
        if random_mutation():
            people_genes[individual] = random.choice(list(PROBS["gene"].keys()))
        """

    print("people_genes:")
    print(people_genes)

    people_traits = {}
    trait_probability = {}

    for individual, gene in people_genes.items():

        """
        probability_distribution = PROBS["trait"][gene]
        individual_has_trait = np.random.choice(list(probability_distribution.keys()), 1,
                                                p=list(probability_distribution.values()), replace=False)
        individual_has_trait = bool(individual_has_trait[0])

        people_traits[individual] = individual_has_trait
        trait_probability[individual] = people_copy_probability[individual] * PROBS["trait"][gene][individual_has_trait]
        """

        # NOTE: I added this to take into a fact the distribution. The results will differ based on the random choice,
        # but on average should correspond to the right result of example on HW:
        # {'Harry': 0.4313, 'James': 0.0065, 'Lily': 0.9504}

        # TODO: Add also option to include Trait like on HW: Lily and Harry False, James. True. ???
        """
        probability_distribution = PROBS["trait"][gene]
        individual_has_trait = np.random.choice(list(probability_distribution.keys()), 1,
                                                p=list(probability_distribution.values()), replace=False)
        individual_has_trait = bool(individual_has_trait[0])
        """

        if individual in have_trait:
            individual_has_trait = True
        else:
            individual_has_trait = False

        trait_probability[individual] = (gene_probability_distributions[individual]
                                         * PROBS["trait"][gene][individual_has_trait])

        trait_probability[individual] = round(trait_probability[individual], 4)

        # TODO: Joint probability:
        # 0.9504 * 0.0065 * 0.431288 = 0.0026643247488

    print("people_traits:")
    print(people_traits)

    print("trait_probability")
    print(trait_probability)

    # Calculate joint probability. Return the joint probability of all of
    # those events taking place (how many copies of each of the genes, and who exhibits the trait).
    # copies = numer 0, 1 or 2

    joint_probability_result = 1

    for prob in trait_probability.values():
        joint_probability_result *= prob

    return joint_probability_result


def random_mutation():
    prob_of_mutation = PROBS["mutation"]
    gene_mutation = [True, False]
    random_gene_mutation = np.random.choice(gene_mutation, 1, p=[prob_of_mutation, 1-prob_of_mutation])
    random_gene_mutation = bool(random_gene_mutation[0])
    return random_gene_mutation


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
                probabilities[individual][attribute_name][attribute_value_name] = probabilities[individual][attribute_name][attribute_value_name] * factor


if __name__ == "__main__":
    main()
