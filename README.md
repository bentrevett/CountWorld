# CountWorld

## Introduction

An environment/dataset creator that deals with counting.

The environment consists of:

- a `world` made up of `entities`, `objects`, `locations` and `actions`
- `entities` are the "actors" or "agents" within the `world`
- `objects` are what the `entities` interact with
- `locations` where `entities` "visit" and perform `actions`
- `actions` are what the `entities` perform in `locations` which involve sometimes interact with `objects`

## Examples

Each example is made up of `(S,Q,A)` triplets.

- `S` is the `story`, made up on `sentences`, which details the `world`
- `Q` is the `query`, which asks questions about the `story`
- `A` is the `answer`, which provides the answers for the `query`

An example triplet:

``` markdown
s liam went to the town
s liam picked up 2 eggs
s eric went to the river
s eric went to the town
s liam went to the river
s liam picked up 3 insects
s eric picked up 1 eggs
s eric dropped 1 eggs
s liam went to the town
s eric went to the river
q how many eggs were picked up from the town ?
a 3
```

All of the lines beginning with `s` make up the `story`, each beginning with `q` make up the query and the same with `a` for answer.

## Generation

The CountWorld dataset generation has numerous parameters can be set by passing them as command line arguments to the `generate.py` file:

- `n_examples` sets the number of `(S,Q,A)` examples to generate, these are automatically split 80/10/10.
- `n_entities_{min/max}` sets the min/max number of entities that can appear in a `story`
- `n_objects_{min/max}` sets the min/max number of objects that can appear in a `story`
- `n_locations_{min/max}` sets the min/max number of locations that can appear in a `story`
- `story_length_{min/max}` sets the min/max number of sentences within a `story`
- `n_questions_{min/max}` sets the min/max number of `queries` for each `story`
- `answer_values_{min/max}` sets the min/max values the `answers` can be for each `query`
- `supporting_answers` this is explained below
- `pick_max` sets the maximum quanity of an object that an entity can pick up at once
- `seed` sets the random seed to reproducible data generation

Running `python generate.py -h` shows the default value for each command line argument.

When a parameter has a minimum and maximum value these are selected uniformly at random for each example generated.

When the `supporting_answers` command line flag is used, `answers` are no longer the single integer `answer` at the end of a `story`, but a sequence where each integer is the `answer` to the `query` at the end of each `sentence`.

Using the same example as previous, but now using `supporting_answers` we get:

``` markdown
s liam went to the town
s liam picked up 2 eggs
s eric went to the river
s eric went to the town
s liam went to the river
s liam picked up 3 insects
s eric picked up 1 eggs
s eric dropped 1 eggs
s liam went to the town
s eric went to the river
q how many eggs were picked up from the town ?
a 0 2 2 2 2 2 3 3 3 3
```

Whenever an example has multiple questions they are ordered so that all of the questions are stated first, followed by the corresponding answers in the same order.

``` markdown
s liam went to the town
s liam picked up 2 eggs
s eric went to the river
s eric went to the town
s liam went to the river
s liam picked up 3 insects
s eric picked up 1 eggs
s eric dropped 1 eggs
s liam went to the town
s eric went to the river
q how many eggs were picked up from the town ?
q how many times did eric pick up eggs ?
q how many times did liam pick up eggs ?
q how many times was the river visited in total ?
q how many insects is eric carrying ?
a 0 2 2 2 2 2 3 3 3 3
a 0 0 0 0 0 0 1 1 1 1
a 0 1 1 1 1 1 1 1 1 1
a 0 0 1 1 2 2 2 2 2 3
a 0 0 0 0 0 0 0 0 0 0
```

When the examples are generated they are automatically split into train/validation/test splits using a ratio of 80:10:10 and are placed in `data/{train/valid/test}.txt`.

## Questions

There are currently 20 different types of questions that can be asked about a story:

- how many \<object> is \<entity> carrying ?
- how many entities picked up \<object> ?
- how many times were \<object> picked up in total ?
- how many \<object> were picked up in total ?
- how many entities dropped \<object> ?
- how many times were \<object> dropped in total ?
- how many \<object> were dropped in total ?
- how many different objects were picked up from the \<location> ?
- how many times were \<object> picked up from the \<location> ?
- how many \<object> were picked up from the \<location> ?
- how many times did \<entity> pick up \<object> ?
- how many \<object> did \<entity> pick up ?
- how many different objects were dropped at the \<location> ?
- how many times were \<object> dropped at the \<location> ?
- how many \<object> were dropped at the \<location> ?
- how many times did \<entity> drop \<object> ?
- how many \<object> did \<entity> drop ?
- how many entities visited the \<location> ?
- how many times did \<entity> visit \<location> ?
- how many times was the \<location> visited in total ?

Most of these questions can be asked about each entity/location/object or a combination of. For example the first question can be asked about every object and entity combination.