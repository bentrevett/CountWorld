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

print("answer:counts", answer_values)

for answer, value in answer_values.items():
    values += value

for answer, value in answer_values.items():
    answer_dist[answer] = value/values

print("answer:percentages", answer_dist)
print("examples", values)

#count duplicates
buffer = ''
uniques = set()
answers = False
for c in contents:
    if c.startswith('s'):
        if answers:
            uniques.add(buffer)
            buffer = ''
            answers = False
        else:
            buffer += c
    if c.startswith('q'):
        buffer += c
    if c.startswith('a'):
        answers = True
        buffer += c

if buffer != '':
    uniques.add(buffer)

print("unique examples", len(uniques))
