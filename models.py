import torch
import torch.nn as nn
import torch.nn.functional as F

class RNN(nn.Module):
    def __init__(self, vocab_size, emb_dim, hid_dim, out_dim):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.s_rnn = nn.LSTM(emb_dim, hid_dim, batch_first=True)
        self.q_rnn = nn.LSTM(emb_dim, hid_dim, batch_first=True)
        self.out = nn.Linear(hid_dim, out_dim)

        self.emb_dim = emb_dim
        self.hid_dim = hid_dim

    def forward(self, s, q):

        #s = [bsz, story_len, sent_len]
        #q = [bsz, query_len]

        #calculate word embeddings
        emb_s = self.embedding(s)
        emb_q = self.embedding(q)

        #emb_s = [bsz, story_len, sent_len, emb_dim]
        #emb_q = [bsz, query_len, emb_dim]

        #embedding for sentence is just average of word embeddings
        emb_s = torch.mean(emb_s, dim=2)

        #emb_s = [bsz, story_len, emb_dim]

        #run rnns over story and query
        o_s, (_, _) = self.s_rnn(emb_s)
        _, (h_q, _) = self.q_rnn(emb_q)

        #o_s = [bsz, story_len, hid_dim]
        #h_q = [1, bsz, hid_dim]

        #reshape query hidden state
        h_q = h_q.squeeze(0)
        h_q = h_q.unsqueeze(2)

        #h_q = [bsz, hid_dim, 1]

        #calculate energy
        e = torch.bmm(o_s, h_q).squeeze(2)

        #e = [bsz, story_len]

        #calculate attention
        a = F.softmax(e, dim=1)

        #e = [bsz, story_len]

        assert e.shape == a.shape
        assert a.sum() == a.shape[0], a.sum()

        #apply attention
        w = torch.sum(o_s * a.unsqueeze(2), dim=1)

        #w = [bsz, hid_dim]

        o = self.out(w)

        #o = [bsz, out_dim]

        return o