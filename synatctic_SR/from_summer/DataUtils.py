import getopt
import subprocess
import time
from os import listdir
from os.path import isfile, join
from ParseTrees import *
from Alphabet import *

help = 'DataUtils.py -i <in path to PTB data> -o <out path to generated encoder decoder file>'


class JaggedBatches(object):
    def __init__(self,batches,offsets,lengths):
        assert(len(offsets) == len(lengths))
        self.batches=batches
        self.offsets=offsets
        self.lengths=lengths
        self.batch_size = self.batches.shape[1]
        self.num_batches = len(offsets)
        self.max_value = int(batches.max())
        self.make_shared()

    def make_shared(self):
        '''
        shuttles the batches onto the GPU
        '''
        self.batches = TT.cast(T.shared(self.batches, borrow=True),'int32')

def load_trees_from_ptb_dir(input_dir):
    result = []
    print 'Loading parse trees from top-level dir:', input_dir 
    for sub_dir in listdir(input_dir):
        if not isfile(join(input_dir,sub_dir)):
            print '  ',sub_dir
            for parse_file in listdir(join(input_dir,sub_dir)):
                parses = load_trees(join(input_dir,sub_dir,parse_file))
                result = result + parses
                print '      loaded ', len(parses), 'parses. Total:',len(result)
    print 'Done loading ', len(result),'parses from', input_dir
    return result

def create_encoder_decoder_file(input_dir, output_file, include_null):
    result = load_trees_from_ptb_dir(input_dir)
    if not include_null:
        for tree in result:
            remove_null_elements(tree)
    print 'Creating encoder-decoder file:',output_file
    outf = open(output_file,'w')
    num_invalid=0
    num_mismatches=0
    for tree in result:
        #print '\nTREE'
        #tree.print_tree()
        [sentence,sr_commands] = parse_to_encoder_decoder_line(tree)
        tokens = sentence.split(' ')
        cmd_list = sr_commands.split(' ')
        tree_sentence = ' '.join(tree.to_tokens()).strip()
        if is_consistent_parse(tokens,cmd_list):
            outf.write(sentence+'\n')
            outf.write(sr_commands+'\n')
        else:
            print 'Parse is not consistent'
            print 'tokens:',sentence
            print 'cmds:  ',sr_commands
            num_invalid += 1

        if sentence.strip() != tree_sentence:
            print 'WARNING: mismatch between encoder input and sentence implied by tree'
            print 'encode:',sentence.strip()
            print 'tree:  ',tree_sentence
            num_mismatches += 1

    print 'number of inconsistent sr commands:', num_invalid 
    print 'number of altered sentences:', num_mismatches
    outf.close()
    
def parse_to_encoder_decoder_line(tree):
    #assert(tree.is_sentence_root())
    encoder_input=''
    decoder_output = ''
    try:
        encoder_input = ' '.join(tree.to_sentence())
        decoder_output= ' '.join(tree.to_SR_rich())
    except:
        e = sys.exc_info()[0]
        print '\n========ERROR========='
        print e
        print 'Printing tree to debug'
        tree.print_tree()
        print 'Tokens'
        print tree.to_tokens()

    return [encoder_input,decoder_output]


def load_trees(file_name):
    file = open(file_name, 'r')
    content = file.read()
    file.close()
    content = '(DOC ' + content + ')'
    file_tree = create_tree(content)
    #make file tree into file forest: one tree per sentence
    #sentence_trees = [tree for tree in file_tree.children]
    #for sentence_tree in sentence_trees:
    #    sentence_tree.set_parent(None)
    #remove redundant node at top (results from extra outer parens in sexp's)
    #sentence_trees = [tree.children[0] for tree in sentence_trees]
    #for sentence_tree in sentence_trees:
    #    sentence_tree.set_parent(None)
    sentence_trees = doc_tree_to_sentence_forest(file_tree)
    return sentence_trees


def doc_tree_to_sentence_forest(doc_tree):
    assert(doc_tree.is_root())
    assert(not doc_tree.is_sentence_root())

    sentence_trees = [tree for tree in doc_tree.children]
    for sentence_tree in sentence_trees:
        sentence_tree.set_parent(None)
    sentence_trees = [get_sentence_root(tree) for tree in sentence_trees]
    return sentence_trees

def get_sentence_root(tree):
    assert(tree.is_root())
    sentence_root=tree
    if not tree.is_sentence_root():
        assert(tree.num_children() == 1)
        #print '\nPARENT--------'
        #sentence_root.print_tree()
        sentence_root = sentence_root.children[0]
        #print '\nCHILD--------'
        #sentence_root.print_tree()
        sentence_root.set_parent(None)
        assert(not sentence_root.is_redundant_root())
    return sentence_root

def create_tree(string):
    assert string[0]=='(', 'Must begin with paren, not: '+string[0]
    assert string[-1]==')', 'Must end with paren, not: '+string[-1]
    trav_string = string[1:-1].strip()
    if(trav_string.find(')') == -1): #leaf node, e.g., trag_string = "NN chairman"
        (pos, text) = trav_string.split(' ') #e.g., NN chairman
        node = ParseTree(pos,text)
        return node
    else: #recurse e.g.,  trav_string = "S (NP-SBJ (NNP Mr.) (NNP Vinken) ) ..."
        index = trav_string.index('(')
        pos = trav_string[0:index].strip() #pos = "S"
        children_string = trav_string[index:] #children_string = "(NP-SBJ (NNP Mr.) (NNP Vinken) )"
        parent = ParseTree(pos,None)
        #get substring expressions corresponding to the child of this node
        child_strings = []
        open_parens = 0
        start = 0
        for i in xrange(len(children_string)):
            if children_string[i] == '(':
                open_parens += 1
            elif children_string[i] == ')': #reached end of some node
                open_parens -= 1
                if open_parens == 0: #reached end of a node one level down from parent
                    child_string = children_string[start:i+1].strip()
                    open_parens=0
                    start=i+1
                    child_strings.append(child_string)
        #recurse on each child
        for child_string in child_strings:
            node = create_tree(child_string)
            node.set_parent(parent)
        return parent

def shuffle_train_valid(train, valid_portion=0.05, prev_steps=10):
    
    # split training set into validation set
    train_x = train
    n_samples = len(train_x)
    sidx = np.random.permutation(n_samples)
    n_train = int(np.round(n_samples * (1. - valid_portion)))
    valid_x = [train_x[s] for s in sidx[n_train:]]
    train_x = [train_x[s] for s in sidx[:n_train]]

    train = train_x
    valid = valid_x

    return train, valid



def index_tokens(alphabet, list_of_token_lists):
    for tlist in list_of_token_lists:
        for token in tlist:
            alphabet.index(token)

def load_raw_SR_data(sr_file, num_examples=None, char_level=True):
    encoder_data = []
    decoder_data = []
    inf = open(sr_file,'r')
    is_encode_line=True
    lines = inf.readlines()
    if not num_examples==None:
        lines = lines[0:num_examples*2]
    for line in lines:
        if is_encode_line:
            tokens = line #if character level
            if not char_level:
                tokens = line.split(' ')
            encoder_data.append(tokens)
        else:
            sr_commands = line.split(' ')
            if not char_level:
                decoder_data.append(sr_commands)
            else:
                decoder_data.append(''.join(sr_commands))
        is_encode_line = not is_encode_line
    inf.close()
    return (encoder_data, decoder_data)

def rich_SR_to_basic_SR(sr_commands):
    basic_SR = ''
    for sr_command in sr_commands:
        if sr_command=='S':
            basic_SR = basic_SR + sr_command
        elif sr_command[0]=='R':
            (c_type, times, r_type) = parse_reduce_command(sr_command)
            simple_r = c_type * times
            basic_SR = basic_SR + simple_r
        else:
            raise Exception('Illegal shift-reduce command: ' + sr_command)
    return basic_SR


def parse_reduce_command(r_command):
    assert(len(r_command)>=3)
    assert(r_command[0]=='R')
    (prefix,reduce_type) = r_command.split('-',1)
    command_type = prefix[0]
    times = int(prefix[1:])
    return (command_type, times, reduce_type)


#load_raw_SR_data(sr_file, num_examples=None, char_level=True)

def load_data_for_lm(sr_file):
    (edata,ddata) = load_raw_SR_data(sr_file, num_examples=None, char_level=False)
    assert(len(edata) == len(ddata))
    print 'Testing SR'
    result = []
    for i in range(len(edata)):
        sr_sentence = make_combined_sr_sentence(edata[i], ddata[i])
        result.append(sr_sentence)
    return result

def create_file_for_lm(sr_file, out_file):
    sr_sentences = load_data_for_lm(sr_file)
    outf = open(out_file,'w')
    for sr_sentence in sr_sentences:
        outf.write(sr_sentence)
    outf.close()

def make_combined_sr_sentence(tokens, sr_commands):
    '''
    Input:
      tokens = [he, saw, the, cat,]
      sr_commands = [S, R1-NP, S, S, S, R2-NP, R3-VP, R1-S]

    Output:
      he R1-NP saw the cat R2-NP R3-VP R1-S
    '''
    token_index=0
    all_tokens = []
    for sr_command in sr_commands:
        if sr_command=='S': #shift
            all_tokens.append(tokens[token_index])
            token_index += 1
        elif sr_command[0]=='R': #reduce
            all_tokens.append(sr_command)
        else:
            raise Exception('Illegal shift-reduce command: ' + sr_command)
    return ' '.join(all_tokens)

def main(argv):
    in_path ='/home/mwick/data/parsing/parsed/mrg/wsj/'
    out_path = 'sr_encode_decode.txt'
    conversion = 'ptb2ed'
    include_null_elements=False

    sys.setrecursionlimit(1024)
    try:
        opts, args = getopt.getopt(argv,"hp:o:c:n:",["help","in_path=","out_path=","conversion=","include_null"])
    except getopt.GetoptError:
        print help
        sys.exit(2)   

    revision = subprocess.check_output('git rev-list --count HEAD', shell=True)
    date = time.strftime("%x")
    who = subprocess.check_output('whoami', shell=True)
    where = subprocess.check_output('uname -n', shell=True)
    args = date + ' ' + revision + ' ' + who + ' ' + where + ' '
    args = args.replace('\n',' ')
    print 'The following args were provided'
    for opt, arg in opts:
        args = args + ' ' + opt + ' ' + arg
        print '  ',opt, arg
        if opt in ("-h","--help"):
            print help
            sys.exit()
        elif opt in ("-i","--in_path"):
            in_path = arg
        elif opt in ("-o","--out_path"):
            out_path = arg
        elif opt in ("-c","--conversion"):
            conversion = arg
        elif opt in ("-n","include_null"):
            include_null_elements=True

    #load_data_for_lm('sr_encode_decode.txt')
    assert(conversion) in ("ptb2ed", "ed2lm")

    if(conversion=='ptb2ed'):
        create_encoder_decoder_file(in_path,out_path, include_null_elements)
    else:
        create_file_for_lm(in_path, out_path)

if __name__ == "__main__":
    main(sys.argv[1:])
