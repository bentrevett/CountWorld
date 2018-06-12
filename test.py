import countworld

world = countworld.World(n_entities=2, n_objects=2, n_locations=2, story_length=20, n_questions=5)

examples = world.generate_examples(1)

story = examples[0]['story']

questions = examples[0]['questions']

for s in story:
    print(s)

for q in questions:
    print(q)