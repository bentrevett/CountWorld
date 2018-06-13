import json
import countworld
import os
from collections import Counter

N_EXAMPLES = 100_000 #examples
N_ENTITIES = 2 #entities per story
N_OBJECTS = 2 #objects per story
N_LOCATIONS = 2 #locations per story
STORY_LENGTH = 20 #story length
N_QUESTIONS = 5 #questions per story
SINGLE_ANSWER = True #single answer
RANDOM_SEED = 1234 #random seed

print('Generating examples...')

examples = countworld.generate_examples(N_EXAMPLES, 
                                        N_ENTITIES, 
                                        N_OBJECTS, 
                                        N_LOCATIONS, 
                                        STORY_LENGTH, 
                                        N_QUESTIONS, 
                                        SINGLE_ANSWER, 
                                        RANDOM_SEED) 

"""
PyTorch expects JSON data to be one JSON object per line
We also split the story statements and question/answer pair into their own key-value pairs
"""

train_examples = examples[:80_000]
val_examples = examples[80_000:90_000]
test_examples = examples[90_000:]

cnt = Counter()

for example in examples:
    questions = example['questions']
    for (q, a) in questions:
        cnt.update([a])

total_answers = sum(cnt.values())

assert total_answers == N_EXAMPLES*N_QUESTIONS

for k, v in cnt.items():
    print(f'answer {k}, count {v}, pct:{v/total_answers:.2f}')

del examples

if not os.path.isdir('data'):
    os.mkdir('data')

def create_datasets(name, examples):
    with open(f'data/{name}.json', 'w') as w:
        for example in examples:
            temp = dict()
            story = example['story']
            for i, s in enumerate(story):
                temp[f'story_{i}'] = s
            questions = example['questions']
            for i, (q, a) in enumerate(questions):
                temp[f'question_{i}'] = q
                temp[f'answer_{i}'] = a
            json.dump(temp, w)
            w.write('\n')

create_datasets('train', train_examples)
create_datasets('val', val_examples)
create_datasets('test', test_examples)