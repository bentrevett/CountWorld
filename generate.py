import countworld
import argparse

parser = argparse.ArgumentParser(description='Generate countworld examples')
parser.add_argument('--n_examples', default=100_000, type=int, help='Number of (S,Q,A) examples')
parser.add_argument('--n_entities', default=2, type=int, help='Number of entities per story')
parser.add_argument('--n_objects', default=2, type=int, help='Number of objects per story')
parser.add_argument('--n_locations', default=2, type=int, help='Number of locations per story')
parser.add_argument('--story_length', default=20, type=int, help='Number of sentences in a story')
parser.add_argument('--n_questions', default=1, type=int, help='Number of questions for each story')
parser.add_argument('--multi_answer', action='store_false', help='Use this flag to get answer for every sentence in a story')
parser.add_argument('--seed', default=1234, type=int, help='Random seed for generation')
parser.add_argument('--ratio', default=[0.8,0.1,0.1], nargs='+', help='Train/Valid/Test example split ratio')
args = parser.parse_args()

N_EXAMPLES = args.n_examples #examples
N_ENTITIES = args.n_entities #entities per story
N_OBJECTS = args.n_objects #objects per story
N_LOCATIONS = args.n_locations #locations per story
STORY_LENGTH = args.story_length #story length
N_QUESTIONS = args.n_questions #questions per story
SINGLE_ANSWER = args.multi_answer #single answer
RANDOM_SEED = args.seed #random seed
TRAIN_VALID_TEST_RATIO = args.ratio

assert (len(TRAIN_VALID_TEST_RATIO) == 3) and (sum(TRAIN_VALID_TEST_RATIO) == 1)

examples = countworld.generate_examples(N_EXAMPLES, 
                                        N_ENTITIES, 
                                        N_OBJECTS, 
                                        N_LOCATIONS, 
                                        STORY_LENGTH, 
                                        N_QUESTIONS, 
                                        SINGLE_ANSWER, 
                                        RANDOM_SEED) 

N_TRAIN_EXAMPLES = int(N_EXAMPLES*TRAIN_VALID_TEST_RATIO[0])
N_VALID_EXAMPLES = int(N_EXAMPLES*TRAIN_VALID_TEST_RATIO[1])
N_TEST_EXAMPLES = int(N_EXAMPLES*TRAIN_VALID_TEST_RATIO[2])

train_examples = examples[:N_TRAIN_EXAMPLES]
valid_examples = examples[N_TRAIN_EXAMPLES:N_TRAIN_EXAMPLES+N_VALID_EXAMPLES]
test_examples = examples[N_TRAIN_EXAMPLES+N_VALID_EXAMPLES:]

def examples_to_file(name, examples):

    with open(f'data/{name}.txt', 'w+') as f:
        for ex in examples:
            story = ex['story']
            for s in story:
                f.write(f's {s}\n')
            questions = ex['questions']
            for (q, _) in questions:
                f.write(f'q {q}\n')
            for (_, a) in questions:
                f.write(f'a {a}\n')

examples_to_file('train', train_examples)
examples_to_file('valid', valid_examples)
examples_to_file('test', test_examples)