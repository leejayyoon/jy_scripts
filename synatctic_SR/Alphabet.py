class Alphabet(object):
    def __init__(self):
        self.size=0
        self.index2token={}
        self.token2index={}
        self.frozen=False
    
    def index(self,token):
        if not token in self.token2index:
            assert(not self.frozen)
            self.token2index[token] = self.size
            self.index2token[self.size] = token
            self.size += 1
        return self.token2index[token]

    def token(self,index):
        assert(index in self.index2token)
        return self.index2token[index]
    
    def freeze(self):
        self.frozen=True

    def unfreeze(self):
        self.frozen=False
