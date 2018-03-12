import CountWorld

world = CountWorld.World(n_entities=2, n_objects=2, n_locations=2, story_length=15, n_questions=5)

examples = world.generate_examples(2)

print(examples)