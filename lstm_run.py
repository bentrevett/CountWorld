import torch
import utils
import random
import models
import torch.nn as nn
import torch.optim as optim

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int, default=32)
parser.add_argument('--clip', type=float, default=1)
parser.add_argument('--emb_dim', type=int, default=64)
parser.add_argument('--sent_hid_dim', type=int, default=256)
parser.add_argument('--query_hid_dim', type=int, default=256)
parser.add_argument('--story_hid_dim', type=int, default=512)
parser.add_argument('--dropout', type=float, default=0.5)
args = parser.parse_args()

seed = random.randint(1000, 9999)

model_name = f'bsz={args.batch_size}-clip={args.clip}-ed={args.emb_dim}-sed={args.sent_hid_dim}-qd={args.query_hid_dim}-std={args.story_hid_dim}-do={args.dropout}-s={seed}.pt'

#for deterministic results
torch.backends.cudnn.deterministic = True
random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)

#load data
train_data, valid_data, test_data, word2idx, idx2word = utils.load_data('data')

#get single example for shapes
s, q, a = train_data[0]

#set vars from data
vocab_size = len(word2idx)
sent_len = torch.tensor(s).shape[1]
query_len = torch.tensor(q).shape[1]
story_len = torch.tensor(s).shape[0]

print(f'vocab size: {vocab_size}')
print(f'sent len: {sent_len}')
print(f'query len: {query_len}')
print(f'story len: {story_len}')

print(f'train examples: {len(train_data)}')
print(f'valid examples: {len(valid_data)}')
print(f'test examples: {len(test_data)}')

model = models.RNNx(vocab_size, args.emb_dim, args.sent_hid_dim, args.query_hid_dim, args.story_hid_dim, 10, args.dropout)

model = model.to(device)

print(f'{model}')

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())

criterion = criterion.to(device)

def train(data, batch_size, model, criterion, optimizer):

    model.train()

    epoch_loss = 0
    epoch_acc = 0

    random.shuffle(data)

    n_batches = len(data) // batch_size

    #last batch may be smaller than batch_size
    for b in range(n_batches):

        optimizer.zero_grad()

        batch_s, batch_q, batch_a = zip(*data[b*batch_size:(b+1)*batch_size])
        batch_s = torch.tensor(batch_s).to(device)
        batch_q = torch.tensor(batch_q).to(device).squeeze(1)
        batch_a = torch.tensor(batch_a).to(device).squeeze(1).squeeze(1)

        #batch_s = [bsz, story_len, sent_len]
        #batch_q = [bsz, n_queries, query_len]
        #batch_a = [bsz, n_queries, story_len if supporting_answers else 1]

        fx = model(batch_s, batch_q)

        loss = criterion(fx, batch_a)

        loss.backward()

        optimizer.step()

        pred = fx.max(1, keepdim=True)[1] # get the index of the max log-probability
        correct = pred.eq(batch_a.view_as(pred)).sum().item()

        epoch_loss += loss.item()
        epoch_acc += correct

    return epoch_loss / n_batches, epoch_acc / len(data)

def evaluate(data, batch_size, model, criterion):

    model.eval()

    with torch.no_grad():
        
        epoch_acc = 0
        epoch_loss = 0

        n_batches = len(data) // batch_size

        #last batch may be smaller than batch_size
        for b in range(n_batches):

            batch_s, batch_q, batch_a = zip(*data[b*batch_size:(b+1)*batch_size])
            batch_s = torch.tensor(batch_s).to(device)
            batch_q = torch.tensor(batch_q).to(device).squeeze(1)
            batch_a = torch.tensor(batch_a).to(device).squeeze(1).squeeze(1)

            #batch_s = [bsz, story_len, sent_len]
            #batch_q = [bsz, n_queries, query_len]
            #batch_a = [bsz, n_queries, story_len if supporting_answers else 1]

            fx = model(batch_s, batch_q)
            pred = fx.max(1, keepdim=True)[1]
            correct = pred.eq(batch_a.view_as(pred)).sum().item()
            loss = criterion(fx, batch_a)
            epoch_acc += correct
            epoch_loss += loss.item()

    return epoch_loss / n_batches, epoch_acc / len(data)

best_valid_loss = float('inf')

for epoch in range(100):

    train_loss, train_acc = train(test_data, args.batch_size, model, criterion, optimizer)
    valid_loss, valid_acc = evaluate(valid_data, args.batch_size, model, criterion)

    if valid_loss < best_valid_loss:
        best_valid_loss = valid_loss
        torch.save(model.state_dict(), f'saves/{model_name}')

    log = f'| epoch: {epoch+1:03} | train loss: {train_loss:.3f} | train acc: {train_acc:.2f} | valid loss: {valid_loss:.3f} | valid acc: {valid_acc:.2f}'

    print(log)

model.load_state_dict(torch.load(f'saves/{model_name}'))

test_loss, test_acc = evaluate(test_data, args.batch_size, model, criterion)

with open(f'results/{model_name[:-3]}.txt', 'w') as w:
    w.write(f'{test_loss} {test_acc}')