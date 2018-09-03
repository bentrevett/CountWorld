import random
from collections import defaultdict
from tqdm import tqdm

ENTITY_NAMES = ['ruben', 'jane', 'eric', 'eve', 'adam', 'claire', 'liam', 'emma', 'oliver', 'sophie']
OBJECT_NAMES = ['leaves', 'rocks', 'flowers', 'insects', 'sticks', 'mushrooms', 'eggs', 'feathers', 'shells', 'berries']
LOCATION_NAMES = ['park', 'forest', 'mountains', 'town', 'station', 'bridge', 'river', 'beach', 'school', 'stadium']

def generate_examples(n_examples, 
                      n_entities, 
                      n_objects, 
                      n_locations, 
                      story_length, 
                      n_questions,
                      answer_values,
                      supporting_answers,
                      pick_max,
                      random_seed=None):
    """
    n_examples (int): number of examples to generate
    n_entities (tuple[int]): 2 element tuple with (min, max) number of unique entities in the story, selected uniformly
    n_objects (tuple[int]): 2 element tuple with (min, max) number of unique objects in the story, selected uniformly
    n_locations (tuple[int]): 2 element tuple with (min, max) number of unique locations in the story, selected uniformly
    story_length (tuple[int]): 2 element tuple with (min, max) number of statements that make up story, selected uniformly
    n_questions (tuple[int]): 2 element tuple with (min, max) number of questions asked at the end of the story, selected uniformly
    answer_values (tuple[int]): 2 element tuple with (min, max) the minimum and maximum values an answer can be
    supporting_answers (bool): if False, the answers are a single integer which is the answer at the end of the story
                          if True, the answers are lists equal to length of the story, with each element being
                          the answer at that point in the story
    pick_max (int): when picking up items, picks up between [1, pick_max] items, selected uniformly
    random_seed (int): random seed for reproducibility, leave None for random random seed
    """

    #use a random seed is we specify it, if not then leave random
    if random_seed is not None:
        random.seed(random_seed)

    #make sure we don't have min > max for entities/objects/locations/questions/story_length/answer_vals
    assert n_entities[0] <= n_entities[1]
    assert n_objects[0] <= n_objects[1]
    assert n_locations[0] <= n_locations[1]
    assert n_questions[0] <= n_questions[1]
    assert story_length[0] <= story_length[1]
    assert answer_values[0] <= answer_values[1]

    #make sure we don't have more than max number of entities/objects/locations
    assert n_entities[1] <= len(ENTITY_NAMES)
    assert n_objects[1] <= len(OBJECT_NAMES)
    assert n_locations[1] <= len(LOCATION_NAMES)

    #make sure we don't want to ask more questions than there are possible questions
    #THIS MUST BE HARD CODED
    assert n_questions[1] <= 20

    #must be able to pick up at least 1 object
    assert pick_max > 0

    #list to store each story/question dict
    examples = []

    #generate examples
    for _ in tqdm(range(n_examples)):

        #make sure entities/objects/locations are random for each story
        random.shuffle(ENTITY_NAMES)
        random.shuffle(OBJECT_NAMES)
        random.shuffle(LOCATION_NAMES)

        #selecting the amount of entities/objects/locations/questions/story length for this example
        example_n_entities = random.randint(n_entities[0], n_entities[1])
        example_n_objects = random.randint(n_objects[0], n_objects[1])
        example_n_locations = random.randint(n_locations[0], n_locations[1])
        example_n_questions = random.randint(n_questions[0], n_questions[1])
        example_story_length = random.randint(story_length[0], story_length[1])

        #create lists of entities/objects/locations
        entities = [Entity(ENTITY_NAMES[i]) for i in range(example_n_entities)]
        objects = [Object(OBJECT_NAMES[i]) for i in range(example_n_objects)]
        locations = [Location(LOCATION_NAMES[i]) for i in range(example_n_locations)]

        #generate story/questions
        story = []
        questions = defaultdict(list)

        while len(story) < example_story_length:

            story, entities, objects, locations = generate_story(story, entities, objects, locations, pick_max)
            questions = generate_questions(questions, entities, objects, locations)  

        #questions will be a dict where key is the string of the question and the value is the answer
        #which is a list of the answer to the question at each step of the story
        #want to transform into tuple, where if we only want a single answer, the answer is the last 
        #value in the answer list
        #also makes sure answers are within specified range
        if supporting_answers:
            questions = [(k, v) for k, v in questions.items() if min(v) >= answer_values[0] and max(v) <= answer_values[1]]
        else:
            questions = [(k, v[-1]) for k, v in questions.items() if v[-1] >= answer_values[0] and v[-1] <= answer_values[1]]

        #check if pruning meant we don't have enough questions
        assert len(questions) >= example_n_questions

        #randomly shuffle so questions are different
        random.shuffle(questions)

        #only get n_questions questions
        questions = questions[:example_n_questions]

        #append example to list
        examples.append({'story': story, 'questions': questions})

    return examples

def generate_story(story, entities, objects, locations, pick_max):
    """
    Takes in a partial story, list of entities, list of objects and list of locations
    
    Generates the next sentence in the story by randomly picking an entity and then
      randomly picking an action for that entity, also updates the stats for each
      entity, object and location, i.e. amount of times location was visited by that entity
    
    Available actions are: moving, picking and dropping.
    - moving takes the entity from one location to another
    - picking makes the entity pick up an object at their current location
    - dropping makes the entity drop an object at their current location
    
    All entities start off with no location specified so their first move must
      be to move to a location
    Entities can only perform a drop action if they are carrying at least one object
    When an entity picks up an object they pick up between 1-3 of a single object
    """

    #select entity at random
    actor = random.choice(entities)
            
    #if it's position is none, needs to go somewhere before it can act
    if actor.position == None:
        actor.position = random.choice(locations).name
        for l in locations:
            if l.name == actor.position:
                l.entity_visits[actor.name] += 1
    
        story.append(f'{actor.name} went to the {actor.position}')

        return story, entities, objects, locations

    #else, options are:
    # moving somewhere else
    # picking up objects
    # dropping objects

    action_choices = ['move', 'pick', 'drop']

    #if only have one available location (i.e. n_locations=1), 
    # cannot move anywhere else after initial move
    if len(locations) < 2:
        action_choices.remove('move')

    #can only drop items if carrying any
    if sum(actor.inventory.values()) < 1:
        action_choices.remove('drop')

    #randomly pick an available action to carry out
    action = random.choice(action_choices)

    if action == 'move':

        #make sure we're already at a location
        assert actor.position is not None

        #make sure there is another location to actually go to
        assert len(locations) > 1

        #only want to move to locations not already at
        available_locations = [l.name for l in locations if l.name is not actor.position]
        
        #pick location
        new_location = random.choice(available_locations)

        #make sure it isn't the current location
        assert actor.position != new_location

        #update new position
        actor.position = new_location
        
        #update location's visited count
        for l in locations:
            if l.name == new_location:
                l.entity_visits[actor.name] += 1

        #update story
        story.append(f'{actor.name} went to the {new_location}')

        return story, entities, objects, locations

    elif action == 'pick':

        #make sure we're at a location
        assert actor.position is not None

        #select which object to pick up
        picked_object = random.choice(objects).name

        #select how many to pick up
        n_picked = random.randint(1,pick_max)

        #update actor's inventory
        actor.inventory[picked_object] += n_picked

        #update objects picked count
        for o in objects:
            if o.name == picked_object:
                o.n_picked.append(n_picked)
                o.picked_entity[actor.name].append(n_picked)
                o.picked_location[actor.position].append(n_picked)

        #update locations pick count
        for l in locations:
            if l.name == actor.position:
                l.picked_objects[picked_object].append(n_picked)

        #update story
        story.append(f'{actor.name} picked up {n_picked} {picked_object}')
        
        return story, entities, objects, locations

    else:

        #can only have picked drop if actor is carrying any items
        assert sum(actor.inventory.values()) > 0

        #select which objects to drop
        available_objects = [obj for obj in actor.inventory.keys() if actor.inventory[obj] > 0]

        #get dropped object
        dropped_object = random.choice(available_objects)

        #select how many to drop
        n_dropped = random.randint(1, actor.inventory[dropped_object])

        #update actor's inventory
        actor.inventory[dropped_object] -= n_dropped

        #update objects drop count
        for o in objects:
            if o.name == dropped_object:
                o.n_dropped.append(n_dropped)
                o.dropped_entity[actor.name].append(n_dropped)
                o.dropped_location[actor.position].append(n_dropped)

        #update locations drop count
        for l in locations:
            if l.name == actor.position:
                l.dropped_objects[dropped_object].append(n_dropped)

        #make sure it hasn't gone negative
        assert actor.inventory[dropped_object] >= 0

        #update story
        story.append(f'{actor.name} dropped {n_dropped} {dropped_object}')

        return story, entities, objects, locations

def generate_questions(questions, entities, objects, locations):
    """
    Takes in: a question dict that has the key being the string of the question and the 
      value being a list of the answers at each sentence in the story, a list of entities
      a list of objects and a list of locations.

    Generates the next answer for each question using the attributes of the entities, objects
    and locations
    """

    #1. how many <object> is <entity> carrying ?
    for ent in entities:
        for obj in objects:
            question = f'how many {obj.name} is {ent.name} carrying ?'
            answer = ent.inventory[obj.name]
            questions[question].append(answer)

    #2. how many entities picked up <object> ?
    for obj in objects:
        question = f'how many entities picked up {obj.name} ?'
        answer = len([x for x in obj.picked_entity.values() if len(x) > 0])
        questions[question].append(answer)

    #3. how many times were <object> picked up in total ?
    for obj in objects:
        question = f'how many times were {obj.name} picked up in total ?'
        answer = len(obj.n_picked)
        questions[question].append(answer)

    #4. how many <object> were picked up in total ?
    for obj in objects:
        question = f'how many {obj.name} were picked up in total ?'
        answer = sum(obj.n_picked)
        questions[question].append(answer)

    #5. how many entities dropped <object> ?
    for obj in objects:
        question = f'how many entities dropped {obj.name} ?'
        answer = len([x for x in obj.dropped_entity.values() if len(x) > 0])
        questions[question].append(answer)

    #6. how many times were <object> dropped in total ?
    for obj in objects:
        question = f'how many times were {obj.name} dropped in total ?'
        answer = len(obj.n_dropped)
        questions[question].append(answer)

    #7. how many <object> were dropped in total ?
    for obj in objects:
        question = f'how many {obj.name} were dropped in total ?'
        answer = sum(obj.n_dropped)
        questions[question].append(answer)

    #8. how many different objects were picked up from the <location> ?
    for loc in locations:
        question = f'how many different objects were picked up from the {loc.name} ?'
        answer = len([x for x in obj.picked_location.values() if len(x) > 0])
        questions[question].append(answer)

    #9. how many times were <object> picked up from the <location> ?
    for obj in objects:
        for loc in locations:
            question = f'how many times were {obj.name} picked up from the {loc.name} ?'
            answer = len(obj.picked_location[loc.name])
            questions[question].append(answer)

    #10. how many <object> were picked up from the <location> ?
    for obj in objects:
        for loc in locations:
            question = f'how many {obj.name} were picked up from the {loc.name} ?'
            answer = sum(obj.picked_location[loc.name])
            questions[question].append(answer)

    #11. how many times did <entity> pick up <object> ?
    for obj in objects:
        for ent in entities:
            question = f'how many times did {ent.name} pick up {obj.name} ?'
            answer = len(obj.picked_entity[ent.name])
            questions[question].append(answer)

    #12. how many <object> did <entity> pick up ?
    for obj in objects:
        for ent in entities:
            question = f'how many {obj.name} did {ent.name} pick up ?'
            answer = sum(obj.picked_entity[ent.name])
            questions[question].append(answer)

    #13. how many different objects were dropped at the <location> ?
    for loc in locations:
        question = f'how many different objects were dropped at the {loc.name} ?'
        answer = len([x for x in obj.dropped_location.values() if len(x) > 0])
        questions[question].append(answer)

    #14. how many times were <object> dropped at the <location> ?
    for obj in objects:
        for loc in locations:
            question = f'how many times were {obj.name} dropped at the {loc.name} ?'
            answer = len(obj.dropped_location[loc.name])
            questions[question].append(answer)

    #15. how many <object> were dropped at the <location> ?
    for obj in objects:
        for loc in locations:
            question = f'how many {obj.name} were dropped at the {loc.name} ?'
            answer = sum(obj.dropped_location[loc.name])
            questions[question].append(answer)

    #16. how many times did <entity> drop <object> ?
    for obj in objects:
        for ent in entities:
            question = f'how many times did {ent.name} drop {obj.name} ?'
            answer = len(obj.dropped_entity[ent.name])
            questions[question].append(answer)

    #17. how many <object> did <entity> drop ?
    for obj in objects:
        for ent in entities:
            question = f'how many {obj.name} did {ent.name} drop ?'
            answer = len(obj.dropped_entity[ent.name])
            questions[question].append(answer)

    #18. how many entities visited the <location> ?
    for loc in locations:
        question = f'how many entities visited the {loc.name} ?'
        answer = len([x for x in loc.entity_visits.values() if x > 0])
        questions[question].append(answer)

    #19. how many times did <entity> visit <location> ?
    for ent in entities:
        for loc in locations:
            question = f'how many times did {ent.name} visit the {loc.name} ?'
            answer = loc.entity_visits[ent.name]
            questions[question].append(answer)

    #20. how many times was the <location> visited in total ?
    for loc in locations:
        question = f'how many times was the {loc.name} visited in total ?'
        answer = sum([x for x in loc.entity_visits.values()])
        questions[question].append(answer)

    return questions

class Entity:

    def __init__(self, name):

        self.name = name
        self.position = None
        self.inventory = defaultdict(int) #number of each object entity is carrying

class Object:

    def __init__(self, name):

        self.name = name
        self.n_picked = [] #count of how many of object was picked up in all locations, length gives number of times this object was picked up, sum gives total count of objects picked up
        self.n_dropped = [] #count of how many of object was picked up in all locations
        self.picked_location = defaultdict(list) #how many times item was picked at each location, length gives number of times this object was picked up at each location, sum gives total number of objects picked up at this location
        self.picked_entity = defaultdict(list) #how many times item was picked by each entity, length gives number of times entity picked up this object, sum gives total of this object was picked up by entity
        self.dropped_location = defaultdict(list) #how many times item was picked at each location
        self.dropped_entity = defaultdict(list) #how many times item was picked at each location

class Location:

    def __init__(self, name):

        self.name = name
        self.entity_visits = defaultdict(int) #times each entity visted, sum to get total visits
        self.picked_objects = defaultdict(list) #count of how many of each object picked up here, length gives number of times object x was picked up at this location, sum gives total number of object x picked up at this location
        self.dropped_objects = defaultdict(list) #count of how many of each object dropped here  