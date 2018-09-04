import countworld
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description='Generate countworld examples', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--n_examples', default=10_000, type=int, help='Number of (S,Q,A) examples')
parser.add_argument('--n_entities_min', default=2, type=int, help='Minimum number of entities per story')
parser.add_argument('--n_entities_max', default=2, type=int, help='Maximum number of entities per story')
parser.add_argument('--n_objects_min', default=2, type=int, help='Minimum number of objects per story')
parser.add_argument('--n_objects_max', default=2, type=int, help='Maximum number of objects per story')
parser.add_argument('--n_locations_min', default=2, type=int, help='Minimum number of locations per story')
parser.add_argument('--n_locations_max', default=2, type=int, help='Maximm number of locations per story')
parser.add_argument('--story_length_min', default=20, type=int, help='Minimum number of sentences in a story')
parser.add_argument('--story_length_max', default=20, type=int, help='Maximum number of sentences in a story')
parser.add_argument('--n_questions_min', default=1, type=int, help='Minimum number of questions for each story')
parser.add_argument('--n_questions_max', default=1, type=int, help='Maximum number of questions for each story')
parser.add_argument('--answer_values_min', default=0, type=int, help='Minimum value that an answer can be')
parser.add_argument('--answer_values_max', default=10, type=int, help='Maximum value that an answer can be')
parser.add_argument('--supporting_answers', action='store_true', help='Use this flag to get answer for every sentence in a story')
parser.add_argument('--pick_max', default=3, type=int, help='Maximum number of objects an entity picks up during a pick action')
parser.add_argument('--seed', default=1234, type=int, help='Random seed for generation')
parser.add_argument('--balance', action='store_true', help='#TODO')
args = parser.parse_args()

N_EXAMPLES = args.n_examples #examples
N_ENTITIES = (args.n_entities_min, args.n_entities_max) #(min, max) entities per story
N_OBJECTS = (args.n_objects_min, args.n_objects_max) #(min, max) objects per story
N_LOCATIONS = (args.n_locations_min, args.n_locations_max) #(min, max) locations per story
STORY_LENGTH = (args.story_length_min, args.story_length_max) #(min, max) story length
N_QUESTIONS = (args.n_questions_min, args.n_questions_max) #(min, max) questions per story
ANSWER_VALUES = (args.answer_values_min, args.answer_values_max) #(min, max) value of answers
SUPPORTING_ANSWERS = args.supporting_answers #supporting answers
PICK_MAX = args.pick_max #maximum items to pick up at once
RANDOM_SEED = args.seed #random seed

examples = countworld.generate_examples(N_EXAMPLES, 
                                        N_ENTITIES, 
                                        N_OBJECTS, 
                                        N_LOCATIONS, 
                                        STORY_LENGTH, 
                                        N_QUESTIONS,
                                        ANSWER_VALUES,
                                        SUPPORTING_ANSWERS,
                                        PICK_MAX,
                                        RANDOM_SEED) 

if args.balance:
    raise NotImplementedError('Balancing of answers not yet implemented!')

N_TRAIN_EXAMPLES = int(N_EXAMPLES*0.8)
N_VALID_EXAMPLES = int(N_EXAMPLES*0.1)
N_TEST_EXAMPLES = int(N_EXAMPLES*0.1)

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
                if isinstance(a, list):
                    a = ' '.join([str(_a) for _a in a])
                    f.write(f'a {a}\n')
                else:
                    f.write(f'a {a}\n')

examples_to_file('train', train_examples)
examples_to_file('valid', valid_examples)
examples_to_file('test', test_examples)