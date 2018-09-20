import torch
import utils
import random
import models
import torch.nn as nn
import torch.optim as optim

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Args():
    def __init__(self, epochs, batch_size, clip, emb_dim, sent_hid_dim, story_hid_dim, out_dim, dropout, seed):
        self.epochs = epochs
        self.batch_size = batch_size
        self.clip = clip
        self.emb_dim = emb_dim
        self.sent_hid_dim = sent_hid_dim
        self.story_hid_dim = story_hid_dim
        self.out_dim = out_dim
        self.dropout = dropout
        self.seed = seed
    
args = Args(epochs=500, batch_size=256, clip=100, emb_dim=128, sent_hid_dim=256, story_hid_dim=256, out_dim=10, dropout=0.0, seed=1234)

#for deterministic results
torch.backends.cudnn.deterministic = True
random.seed(args.seed)
torch.manual_seed(args.seed)
torch.cuda.manual_seed(args.seed)

#load data
train_data, valid_data, test_data, word2idx, idx2word = utils.load_data('data')

#get single example for shapes
s, q, a = train_data[0]

#set vars from data
vocab_size = len(word2idx)
story_len = torch.tensor(s).shape[0]
sent_len = torch.tensor(s).shape[1]
query_len = torch.tensor(q).shape[1]

print(f'vocab size: {vocab_size}')

model = models.RNN(vocab_size, args.emb_dim, args.sent_hid_dim, args.story_hid_dim, args.out_dim, args.dropout)

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
    for b in range(n_batches+1):

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
        for b in range(n_batches+1):

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

for epoch in range(args.epochs):

    train_loss, train_acc = train(test_data, args.batch_size, model, criterion, optimizer)
    valid_loss, valid_acc = evaluate(valid_data, args.batch_size, model, criterion)

    print(f'| epoch: {epoch+1:03} | train loss: {train_loss:.3f} | train acc: {train_acc:.2f} | valid loss: {valid_loss:.3f} | valid acc: {valid_acc:.2f}')
