import random

ENTITY_NAMES = ['entityA', 'entityB', 'entityC']
OBJECT_NAMES = ['objectA', 'objectB', 'objectC']
LOCATION_NAMES = ['locationA', 'locationB', 'locationC']

class World():

    def __init__(self, n_entities, n_objects, n_locations):

        self.entities = Entities(n_entities)
        self.objects = Objects(n_objects)
        self.locations = Locations(n_locations)
    
    def generate_examples(self, n=100):

        pass

class Entities():
    """
    Holds multiple entities
    """

    def __init__(self, n):
        """
        n (int): the amount of entities to create
        """

class Entity():

    def __init__(self, name):

        self.name = name

class Objects():
    """
    Holds multiple objects
    """

    def __init__(self, n):
        """
        n (int): the amount of objects to create
        """

class Object():

    def __init__(self, name):

        self.name = name

class Locations():
    """
    Holds multiple locations
    """

    def __init__(self, n):
        """
        n (int): the amount of locations to create
        """

class Location():

    def __init__(self, name):

        self.name = name