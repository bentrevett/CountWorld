import torch
import utils
import random
import models
import torch.nn as nn
import torch.optim as optim

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Args():
    def __init__(self, epochs, batch_size, clip, emb_dim, hid_dim, out_dim, seed):
        self.epochs = epochs
        self.batch_size = batch_size
        self.clip = clip
        self.emb_dim = emb_dim
        self.hid_dim = hid_dim
        self.out_dim = out_dim
        self.seed = seed
    
args = Args(10, 32, 1, 64, 128, 11, 1234)

random.seed(args.seed)

#load data
train_data, valid_data, test_data, word2idx, idx2word = utils.load_data('data')

#get single example for shapes
s, q, a = train_data[0]

#set vars from data
vocab_size = len(word2idx)
story_len = torch.tensor(s).shape[0]
sent_len = torch.tensor(s).shape[1]
query_len = torch.tensor(q).shape[1]

model = models.RNN(vocab_size, args.emb_dim, args.hid_dim, args.out_dim)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters())


def train(data, batch_size, model, criterion, optimizer):

    model.train()

    epoch_loss = 0

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

        epoch_loss += loss.item()

    return epoch_loss / len(data)

def evaluate(data, batch_size, model, criterion):

    model.eval()

    with torch.no_grad():

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

            loss = criterion(fx, batch_a)

            epoch_loss += loss.item()

    return epoch_loss / len(data)

for epoch in range(args.epochs):

    train_loss = train(test_data, args.batch_size, model, criterion, optimizer)
    valid_loss = evaluate(valid_data, args.batch_size, model, criterion)

    print(f'| epoch: {epoch+1:03} | train loss: {train_loss:.3f} | valid loss: {valid_loss:.3f}')