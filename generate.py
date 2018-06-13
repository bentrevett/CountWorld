import argparse
import json
import countworld

parser = argparse.ArgumentParser(description='Generating countworld examples')
parser.add_argument('--n_examples',type=int,default=10)
parser.add_argument('--n_entities',type=int,default=2)
parser.add_argument('--n_objects',type=int,default=2)
parser.add_argument('--n_locations',type=int,default=2)
parser.add_argument('--n_questions',type=int,default=5)
parser.add_argument('--story_length',type=int,default=20)
parser.add_argument('--multi_answer', action='store_false', default=True)
parser.add_argument('--random_seed',type=int,
default=None)
args = parser.parse_args()

examples = countworld.generate_examples(args.n_examples, 
                                        args.n_entities, 
                                        args.n_objects, 
                                        args.n_locations,
                                        args.story_length,
                                        args.n_questions,
                                        args.multi_answer,
                                        args.random_seed)

"""
PyTorch expects JSON data to be one JSON object per line
We also split the story statements and question/answer pair into their own key-value pairs
"""

with open(f'example.json', 'w') as w:
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