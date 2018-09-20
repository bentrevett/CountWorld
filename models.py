import torch
import torch.nn as nn
import torch.nn.functional as F

class RNN(nn.Module):
    def __init__(self, vocab_size, emb_dim, sent_hid_dim, story_hid_dim, out_dim, dropout):
        super().__init__()

        self.embedding = nn.Embedding(vocab_size, emb_dim)
        self.sent_rnn = nn.LSTM(emb_dim, sent_hid_dim, batch_first=True)
        self.story_rnn = nn.LSTM(sent_hid_dim+story_hid_dim, story_hid_dim, batch_first=True)
        self.query_rnn = nn.LSTM(emb_dim, story_hid_dim, batch_first=True)
        self.out = nn.Linear(story_hid_dim, out_dim)
        self.do = nn.Dropout(dropout)

        self.sent_hid_dim = sent_hid_dim

    def forward(self, s, q):

        #s = [bsz, story_len, sent_len]
        #q = [bsz, query_len]

        #calculate word embeddings
        emb_s = self.do(self.embedding(s))
        emb_q = self.do(self.embedding(q))

        #emb_s = [bsz, story_len, sent_len, emb_dim]
        #emb_q = [bsz, query_len, emb_dim]

        batch_size = emb_s.shape[0]
        story_len = emb_s.shape[1]

        h_s = torch.zeros(batch_size, story_len, self.sent_hid_dim).to(s.device)

        for i in range(story_len):
            _, (h, _) = self.sent_rnn(emb_s[:,i,:]) 
            h_s[:,i,:] = h.squeeze(0)

        #h_s = [bsz, story_len, emb_dim]

        #run rnns over story and query
        _, (h_q, _) = self.query_rnn(emb_q)

        story_rnn_input = torch.cat((h_s, h_q.squeeze(0).unsqueeze(1).expand(-1,h_s.shape[1] ,-1)),dim=2)

        o_s, (h_s, _) = self.story_rnn(story_rnn_input)

        #o_s = self.do(o_s)
        #h_q = self.do(h_q)

        #o_s = [bsz, story_len, hid_dim]
        #h_q = [1, bsz, hid_dim]

        #reshape query hidden state
        #h_q = h_q.squeeze(0)
        #h_q = h_q.unsqueeze(2)

        #h_q = [bsz, hid_dim, 1]

        #calculate energy
        #e = torch.bmm(o_s, h_q).squeeze(2)

        #e = [bsz, story_len]

        #calculate attention
        #a = F.softmax(e, dim=1)

        #e = [bsz, story_len]

        #assert e.shape == a.shape

        #apply attention
        #w = torch.sum(o_s * a.unsqueeze(2), dim=1)

        #w = [bsz, hid_dim]

        #o = self.out(w)

        #o = [bsz, out_dim]

        o = self.out(h_s.squeeze(0))

        return o

class MemoryNetwork(nn.Module):
    def __init__(self, vocab_size, emb_dim, out_dim, sent_len, story_len, pos_enc, temp_enc, n_hops):
        super().__init__()
        
        self.vocab_size = vocab_size
        self.emb_dim = emb_dim
        self.sent_len = sent_len
        self.story_len = story_len
        self.pos_enc = pos_enc
        self.temp_enc = temp_enc
        self.n_hops = n_hops
        
        #input, query and output embeddings
        #for nn.ModuleList, see: 
        #  https://discuss.pytorch.org/t/when-should-i-use-nn-modulelist-and-when-should-i-use-nn-sequential/5463
        self.embeddings = nn.ModuleList([nn.Embedding(self.vocab_size, self.emb_dim, padding_idx=0) for _ in range(self.n_hops+1)])
        for e in self.embeddings:
            e.weight.data.normal_(0, 0.1)
            e.weight.data[0].fill_(0)
                
        #calculate position encoding
        if self.pos_enc:
            J = self.sent_len
            d = self.emb_dim
            self.l = torch.zeros(J, d)
            for j in range(1, J+1):
                for k in range(1, d+1):
                    self.l[j-1][k-1] = (1 - j/J) - (k/d) * (1 - 2*j/J)
            self.l = self.l.unsqueeze(0).repeat(self.story_len, 1, 1) # l = [story len, sent len, emb dim]
        
        #initialize temporal encoding parameters
        if self.temp_enc:
            self.T_A = nn.Parameter(torch.randn(self.story_len, self.emb_dim).normal_(0, 0.1))
            self.T_C = nn.Parameter(torch.randn(self.story_len, self.emb_dim).normal_(0, 0.1))
        
        self.out = nn.Linear(emb_dim, out_dim)

    def forward(self, S, Q, linear):

        self.l = self.l.to(S.device)
        
        # S = [bsz, story len, sent len]
        # Q = [bsz, q len]
        
        #make sure input is the correct size
        assert S.shape[1] == self.story_len and S.shape[2] == self.sent_len
        
        #embed the query 
        # B is the first embedding
        U = self.embeddings[0](Q) # U = [bsz, q len, emb dim]
        U = torch.sum(U, 1) # U = [bsz, emb dim]
        
        for k in range(self.n_hops):
        
            #embed the story
            # A is embedding k, A^k, where k is the current hop number
            M = self.embeddings[k](S) # M = [bsz, story len, sent_len, emb dim]

            #apply position encoding
            if self.pos_enc:
                l = self.l.unsqueeze(0).repeat(M.shape[0], 1, 1, 1) # l = [bsz, story len, sent len, emb dim]
                M *= l

            M = torch.sum(M, 2) # M = [bsz, story len, emb dim]

            #apply temporal encoding
            if self.temp_enc:
                T_A = self.T_A.unsqueeze(0).repeat(M.shape[0], 1, 1)
                M += T_A

            #calculate attention
            P = torch.bmm(M, U.unsqueeze(2)).squeeze(2) # P = [bsz, story len]
            if not linear:
                P = F.softmax(P, dim=1) # P = [bsz, story len]

            #output embedding of story
            # C is embedding k+1, A^(k+1), where k is the current hop number
            C = self.embeddings[k+1](S) # C = [bsz, story len, sent_len, emb dim]
            
            #apply position encoding
            if self.pos_enc:
                l = self.l.unsqueeze(0).repeat(C.shape[0], 1, 1, 1) # l = [bsz, story len, sent len, emb dim]
                C *= l
            
            C = torch.sum(C, 2) # C = [bsz, story len, emb dim]

            #apply temporal encoding
            if self.temp_enc:
                T_C = self.T_C.unsqueeze(0).repeat(C.shape[0], 1, 1)
                C += T_C

            #apply attention to output embedding
            O = torch.bmm(P.unsqueeze(1), C).squeeze(1) # O = [bsz, emb dim]
            
            #the next embedded query is the sum of the previous embedded query and the output
            U = U + O
                
        A = self.out(U) # A = [bsz, out_dim]
        
        return A
