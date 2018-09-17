import os

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

    data.append((temp_s, temp_q, temp_a))

    return data

def get_max_lengths(all_data):
    """
    Given a list of list of (story, query, answer) tuples, get the maximum story, sentence and query lengths
    """
    max_story_len = 0
    max_sent_len = 0
    max_queries = 0
    max_query_len = 0
    using_supporting_answers = False
    
    for data in all_data:
        for story, query, answer in data:
            if len(story) > max_story_len:
                max_story_len = len(story)
            for sentence in story:
                if len(sentence) > max_sent_len:
                    max_sent_len = len(sentence)
            if len(query) > max_queries:
                max_queries = len(query)
            for q in query:
                if len(q) > max_query_len:
                    max_query_len = len(q)
            for a in answer:
                if len(a) > 1:
                    using_supporting_answers = True
                
    return max_story_len, max_sent_len, max_queries, max_query_len, using_supporting_answers
            
def pad_data(data, max_story_len, max_sent_len, max_queries, max_query_len, using_supporting_answers):
    """
    Given a list of (story, query, answer) tuples, pad them all to the maximum lenghts provided
    """
    for i, (story, query, answer) in enumerate(data):
        for j, sentence in enumerate(story):
            if len(sentence) < max_sent_len:
                data[i][0][j].extend(['<pad>'] * (max_sent_len - len(sentence)))
        while len(story) < max_story_len:
            data[i][0].append(['<pad>'] * max_sent_len)
        for j, q in enumerate(query):
            if len(q) < max_query_len:
                data[i][1][j].extend(['<pad>'] * (max_query_len - len(q)))
        while len(query) < max_queries:
            data[i][1].append(['<pad>'] * max_query_len)
        if using_supporting_answers:
            for j, a in enumerate(answer):
                if len(a) < max_story_len:                  
                    data[i][2][j].extend([-1] * (max_story_len - len(a)))
        while len(answer) < max_queries:
            data[i][2].append([-1] * max_story_len if using_supporting_answers else [-1])
            
    return data
    
def create_vocab(all_data):
    """
    Given a list of list of (story, query, answer) tuples, create the vocabulary word-to-index and index-to-word mappings
    Makes sure the padding token is index 0
    """
    word2idx = {'<pad>': 0}
    idx2word = {0: '<pad>'}
    
    for data in all_data:
        for s, q, _ in data:
            for sent in s:
                for word in sent:
                    if word not in word2idx:
                        word2idx[word] = len(word2idx)
                        idx2word[len(idx2word)] = word
            for query in q:
                for word in query:
                    if word not in word2idx:
                        word2idx[word] = len(word2idx)
                        idx2word[len(idx2word)] = word

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
        temp.append((temp_story, temp_query, temp_answer))
        
    return temp
    
def load_data(data_dir):
     
    #get (s,q,a) for each file
    train_data = data_from_files(os.path.join(data_dir, 'train.txt'))
    valid_data = data_from_files(os.path.join(data_dir, 'valid.txt'))
    test_data = data_from_files(os.path.join(data_dir, 'test.txt'))

    #get sizes for padding
    max_story_len, max_sent_len, max_queries, max_query_len, using_supporting_answers = get_max_lengths([train_data, valid_data, test_data])

    #now do padding
    train_data = pad_data(train_data, max_story_len, max_sent_len, max_queries, max_query_len, using_supporting_answers)
    valid_data = pad_data(valid_data, max_story_len, max_sent_len, max_queries,max_query_len, using_supporting_answers)
    test_data = pad_data(test_data, max_story_len, max_sent_len, max_queries,max_query_len, using_supporting_answers)

    #create vocab
    word2idx, idx2word = create_vocab([train_data, valid_data, test_data])
    
    #vectorize, i.e. go from words to indexes
    train_data = vectorize(train_data, word2idx)
    valid_data = vectorize(valid_data, word2idx)
    test_data = vectorize(test_data, word2idx)

    return train_data, valid_data, test_data, word2idx, idx2word