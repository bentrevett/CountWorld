import random
from collections import defaultdict

ENTITY_NAMES = ['entityA', 'entityB', 'entityC']
OBJECT_NAMES = ['objectA', 'objectB', 'objectC']
LOCATION_NAMES = ['locationA', 'locationB', 'locationC']

class World:

    def __init__(self, n_entities, n_objects, n_locations):

        assert n_entities <= len(ENTITY_NAMES)
        assert n_objects <= len(OBJECT_NAMES)
        assert n_locations <= len(LOCATION_NAMES)

        self.entities = [Entity(ENTITY_NAMES[i]) for i in range(n_entities)]
        self.objects = [Object(OBJECT_NAMES[i]) for i in range(n_objects)]
        self.locations = [Location(LOCATION_NAMES[i]) for i in range(n_locations)]

    def generate_examples(self, n=100):
        pass

    def generate_example(self, example_length):

        example = []

        while len(example) < example_length:
            
            #select entity at random
            actor = random.choice(self.entities)
            
            #if it's position is none, needs to go somewhere before it can act
            if actor.position == None:
                actor.position = random.choice(self.locations).name
                for l in self.locations:
                    if l.name == actor.position:
                        l.entity_visits[actor.name] += 1
                example.append(f'{actor.name} went to the {actor.position}')
                continue

            #options are:
            #  moving somewhere else
            #  pick objects
            #  drop objects

            action = random.choice(['move', 'pick', 'drop'])

            if action == 'move':
                #only want to move to locations not already at
                available_locations = [l.name for l in self.locations if l.name is not actor.position]
                
                #pick location
                new_location = random.choice(available_locations)

                #update new position
                actor.position = new_location
                
                #update location's visited count
                for l in self.locations:
                    if l.name == new_location:
                        l.entity_visits[actor.name] += 1

                #update example
                example.append(f'{actor.name} went to the {new_location}')

            elif action == 'pick':
                #select which object to pick up
                picked_object = random.choice(self.objects).name

                #select how many to pick up
                n_picked = random.randint(1,3)

                #update actor's inventory
                actor.inventory[picked_object] += n_picked

                #update objects picked count
                for o in self.objects:
                    if o.name == picked_object:
                        o.n_picked.append(n_picked)
                        o.picked_entity[actor.name].append(n_picked)
                        o.picked_location[actor.position].append(n_picked)

                #update locations pick count
                for l in self.locations:
                    if l.name == actor.position:
                        l.picked_objects[picked_object].append(n_picked)

                #update example
                example.append(f'{actor.name} picked up {n_picked} {picked_object}')
                
            else:
                #can only drop items if carrying any
                if sum(actor.inventory.values()) < 1:
                    continue

                #select which objects to drop
                available_objects = [obj for obj in actor.inventory.keys() if actor.inventory[obj] > 0]

                #get dropped object
                dropped_object = random.choice(available_objects)

                #select how many to drop
                n_dropped = random.randint(1, actor.inventory[dropped_object])

                #update actor's inventory
                actor.inventory[dropped_object] -= n_dropped

                #update objects drop count
                for o in self.objects:
                    if o.name == dropped_object:
                        o.n_dropped.append(n_dropped)
                        o.dropped_entity[actor.name].append(n_dropped)
                        o.dropped_location[actor.position].append(n_dropped)

                #update locations drop count
                for l in self.locations:
                    if l.name == actor.position:
                        l.dropped_objects[dropped_object].append(n_dropped)

                #make sure it hasn't gone negative
                assert actor.inventory[dropped_object] >= 0

                #update example
                example.append(f'{actor.name} dropped {n_dropped} {dropped_object}')

        print(example)

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