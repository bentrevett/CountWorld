import os
import torch.utils.data

def data_from_files(file):
    """
    From a list of files, get all the parsed data from each concatenated into a list of (story, query, answer) tuples
    """
    
    with open(file, 'r') as f:
        raw_data = f.readlines()

    data = []
    answers = False
    temp_s = []
    temp_q = []
    temp_a = []

    for rd in raw_data:
        if rd.startswith('s'): #sentence
            if answers:
                data.append((temp_s, temp_q, temp_a))
                temp_s = []
                temp_q = []
                temp_a = []
                answers = False
            sent = rd[:-1].split(' ')[1:]
            temp_s.append(sent)
        if rd.startswith('q'): #question
            question = rd[:-1].split(' ')[1:]
            temp_q.append(question)
        if rd.startswith('a'): #answer
            answer = rd[:-1].split(' ')[1:]
            temp_a.append(answer)
            answers = True

    return data

def get_max_lengths(all_data):
    """
    Given a list of list of (story, query, answer) tuples, get the maximum story, sentence and query lengths
    """
    max_story_len = 0
    max_sent_len = 0
    max_query_len = 0
    
    for data in all_data:
        for story, query, _ in data:
            if len(story) > max_story_len:
                max_story_len = len(story)
            for sentence in story:
                if len(sentence) > max_sent_len:
                    max_sent_len = len(sentence)
            for q in query:
                if len(q) > max_query_len:
                    max_query_len = len(q)
                
    return max_story_len, max_sent_len, max_query_len
            
def pad_data(data, max_story_len, max_sent_len, max_query_len):
    """
    Given a list of (story, query, answer) tuples, pad them all to the maximum lenghts provided
    """
    for i, (story, query, _) in enumerate(data):
        for j, sentence in enumerate(story):
            if len(sentence) < max_sent_len:
                data[i][0][j].extend(['<pad>'] * (max_sent_len - len(sentence)))
        while len(story) < max_story_len:
            data[i][0].append(['<pad>'] * max_sent_len)
        for j, q in enumerate(query):
            if len(q) < max_query_len:
                data[i][1][j].extend(['<pad>'] * (max_query_len - len(q)))
    return data
    
def create_vocab(all_data):
    """
    Given a list of list of (story, query, answer) tuples, create the vocabulary word-to-index and index-to-word mappings
    Makes sure the padding token is index 0
    """
    unique_words = set()
    
    for data in all_data:
        for s, q, _ in data:
            for sent in s:
                unique_words.update(sent)
            for query in q:
                unique_words.update(query)

    if '<pad>' in unique_words:
        unique_words.remove('<pad>')
    
    word2idx = {'<pad>': 0}
    idx2word = {0: '<pad>'}
    
    for i, w in enumerate(unique_words, start=1):
        word2idx[w] = i
        idx2word[i] = w
    
    return word2idx, idx2word
        
def vectorize(data, word2idx):
    """
    Given a list of (story, query, answer) tuples and a word-to-index mapping, convert all to integers
    """
    temp = []
    for story, query, answer in data:
        temp_story = []
        temp_query = []
        temp_answer = []
        for sent in story:
            temp_story += [[word2idx[w] for w in sent]]
        for q in query:
            temp_query += [[word2idx[w] for w in q]]
        for a in answer:
            temp_answer += [[int(w) for w in a]]
        temp.append([temp_story, temp_query, temp_answer])
        
    return temp
  
def to_dataset(data, device):
    """
    Converts the data which is a list of lists into a PyTorch Dataset object which can be fed to an iterator using PyTorch DataLoaders
    """
    data_s, data_q, data_a = zip(*data)
    data_s, data_q, data_a = torch.LongTensor(data_s).to(device), torch.LongTensor(data_q).to(device), torch.LongTensor(data_a).to(device)
    data = torch.utils.data.TensorDataset(data_s, data_q, data_a)
    return data
    
def load_data(data_dir, device):
     
    #get (s,q,a) for each file
    train_data = data_from_files(os.path.join(data_dir, 'train.txt'))
    valid_data = data_from_files(os.path.join(data_dir, 'valid.txt'))
    test_data = data_from_files(os.path.join(data_dir, 'test.txt'))

    #get sizes for padding
    max_story_len, max_sent_len, max_query_len = get_max_lengths([train_data, valid_data, test_data])

    #now do padding
    train_data = pad_data(train_data, max_story_len, max_sent_len, max_query_len)
    valid_data = pad_data(valid_data, max_story_len, max_sent_len, max_query_len)
    test_data = pad_data(test_data, max_story_len, max_sent_len, max_query_len)
        
    #create vocab
    word2idx, idx2word = create_vocab([train_data, valid_data, test_data])
    
    #vectorize
    train_data = vectorize(train_data, word2idx)
    valid_data = vectorize(valid_data, word2idx)
    test_data = vectorize(test_data, word2idx)

    #turn from list into PyTorch Dataset object
    train_data = to_dataset(train_data, device)
    valid_data = to_dataset(valid_data, device)
    test_data = to_dataset(test_data, device)
    
    #the Dataset objects just need to be passed to an iterator, e.g.:
    # train_iterator = torch.utils.data.DataLoader(train_data, batch_size=32)
    # for s, q, a in train_iterator:
    #     do training here!

    return train_data, valid_data, test_data, word2idx, idx2word