answer_values = dict()
answer_dist = dict()

with open('data/train.txt', 'r') as f:
    contents = f.readlines()

for c in contents:
    if not c.startswith('a'):
        continue
    else:
        answer = int(c.split(' ')[-1])
        if answer in answer_values:
            answer_values[answer] += 1
        else:
            answer_values[answer] = 1

values = 0

print(answer_values)

for answer, value in answer_values.items():
    values += value

for answer, value in answer_values.items():
    answer_dist[answer] = value/values

print(answer_dist)