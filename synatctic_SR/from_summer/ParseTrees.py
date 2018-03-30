import sys
import re
from os import listdir
from os.path import isfile, join
import getopt
from collections import deque
from DataUtils import *

class ParseTree(object):
    def __init__(self,data_type,data):
        self.data_type=data_type
        self.data=data
        self.parent=None
        self.children=[]

    def is_leaf(self):
        return len(self.children)==0

    def is_root(self):
        return self.parent==None

    def is_sentence_root(self):
        return len(self.data_type)>=1 and self.data_type[0]=='S' #is_root isn't sufficient because we might root tree at doc-level

    def is_redundant_root(self):
        return self.is_root() and (self.data_type == None or len(self.data_type) == 0)

    #def is_sentence_fragment_root(self):
    #    return self.is_root() and not self.data_type == None && not self.is_sentence_root()

    def is_binary(self):
        is_binary=True
        for node in self.traverse_preorder():
            is_binary = is_binary and (len(node.children)<=2)
        return is_binary

    def is_node_PTB_null(node):
        is_null = node.data_type == '-NONE-'
        if is_null:
            assert node.is_leaf()
        return is_null

    def num_children(self):
        return len(self.children)

    def root(self):
        if self.is_root():
            return self
        else:
            return parent.root()

    def set_parent(self, node):
        if not self.parent==None:
            self.parent.children.remove(self)
            #raise NotYetSupportedException("Error: not yet implemented.")
        self.parent=node
        if node != None:
            node.children.append(self)

    def remove_subtree(self, remove_linear_chains=False):
        '''Removes the entire subtree starting with this node. Compare with remove_node.
        '''
        if remove_linear_chains:
            old_parent = self.parent
            self.set_parent(None)
            if not old_parent.is_root() and len(old_parent.children)<=1:
                old_parent.remove_node(remove_linear_chains)
        else:
            self.set_parent(None)

    def remove_node(self, remove_linear_chains=False):
        '''Removes the node, but preserves subtree by making children elements of parent. Preserves order of children.
        '''
        assert(self.parent != None)
        siblings = self.parent.children
        my_order = siblings.index(self)
        correct_order_children = []
        child_order = 0
        for i in range(len(siblings)):
            if i==my_order:
                for child in self.children:
                    child.parent = self.parent
                    correct_order_children.append(child)
            else:
                correct_order_children.append(siblings[i])
        self.parent.children = correct_order_children
        old_parent=self.parent
        self.parent=None
        if remove_linear_chains and not old_parent.is_root() and len(old_parent.children)<=1:
            old_parent.remove_node(remove_linear_chains)

    def print_tree(self, depth=0):
        pad = '  ' * depth
        out = pad
        if not self.data_type == None:
            out = out + self.data_type
            if not self.data == None:
                out = out + ':'
        if not self.data == None:
            out = out + self.data
        print out
        for child in self.children:
            child.print_tree(depth+1)

    def print_node(self):
        print self.node_as_string()

    def node_as_string(self):
        data = self.data
        data_type = self.data_type
        if data == None or len(data)==0:
            data = '<None>'
        if data_type == None or data_type.isspace() or len(data_type)==0:
            data_type = '<None>'
        if data.isspace():
            data = '<WS>'

        return data_type+':'+data

    def traverse_leaves_preorder(self):
        all_nodes = self.traverse_preorder()
        return [node for node in all_nodes if node.is_leaf()]

    def traverse_preorder(self):
        return self.traverse_preorder_accum([])

    def traverse_preorder_accum(self, result):
        result.append(self)
        for child in self.children:
            child.traverse_preorder_accum(result)
        return result

    def traverse_bfs(self):
        result = []
        q = deque([self])
        while(len(q)>0):
            n = q.popleft()
            result.append(n)
            for child in n.children:
                q.append(child)
        return result

    def to_sentence(self):
        assert(self.is_root() or self.is_sentence_root())
        return self.to_tokens()

    def to_tokens(self):
        leaves = self.traverse_leaves_preorder()
        return [leaf.data for leaf in leaves]

    def to_SR(self):
        #assert(self.is_sentence_root())
        return self.to_SR_helper([])
            
    def to_SR_helper(self, result):
        if self.is_leaf():
            result.append('S')
        for child in self.children:
            child.to_SR_helper(result)
        if not self.is_leaf():
            result.append('R'+str(len(self.children)))
        return result

    def to_SR_rich(self):
        #assert(self.is_sentence_root())
        return self.to_SR_rich_helper([])
            
    def to_SR_rich_helper(self, result):
        if self.is_leaf():
            result.append('S')
        for child in self.children:
            child.to_SR_rich_helper(result)
        if not self.is_leaf():
            result.append('R'+str(len(self.children)) + '-' + self.data_type)
        return result

    def to_SEXP(self):
        result = []
        self.to_SEXP_helper(result)
        return ''.join(result)

    def to_SEXP_helper(self,result):
        if self.is_leaf():
            if self.data==None:
                print 'ERROR: data is none'
                print 'Tree'
                self.root().print_tree()
                print 'Node',self.node_as_string()
            result.append('(NA ' + self.data+')')
        else:
            if self.data_type==None:
                print 'ERROR: data_type is none'
                print 'Tree'
                self.root().print_tree()
                print 'Node',self.node_as_string()
            result.append('('+self.data_type+' ')
        for child in self.children:
            child.to_SEXP_helper(result)
        if not self.is_leaf():
            result.append(')')


def parse_reduce_command_robust(r_command):
    if not '-' in r_command:
        return ['R',1,'-NP']
        #return [r_command,'-NP']
    (prefix,reduce_type) = r_command.split('-',1)
    command_type = prefix[0]
    times = int(prefix[1:])
    return (command_type, times, reduce_type)

def perform_shift_reduce(tokens, sr_commands):
    token_index=0
    stack = []
    for sr_command in sr_commands:
        if sr_command=='S': #shift
            leaf = ParseTree(None,tokens[token_index])
            stack.append(leaf)
            token_index += 1
        elif sr_command[0]=='R': #reduce
            (c_type, times, r_type) = parse_reduce_command(sr_command)
            assert(times<=len(stack))
            parent = ParseTree(r_type, None)
            for i in range(times):
                node = stack.pop()
                assert(node.is_root())
                node.set_parent(parent)
            parent.children.reverse() #compensate for popping off stack
            stack.append(parent)
        else:
            raise Exception('Illegal shift-reduce command: ' + sr_command)
    assert(len(stack)==1) #a valid sequence of SR commands should result in a tree
    sentence_root = stack.pop()
    return sentence_root


def is_consistent_parse(tokens, sr_commands):
    [sentence_root,overshifted,undershifted,overpopped,underpopped]=perform_shift_reduce_robust(tokens,sr_commands)
    return overshifted==0 and undershifted==0 and overpopped==0 and underpopped==0

def perform_shift_reduce_robust(tokens, sr_commands):
    '''This function treats illegal commands as shifts.
    '''
    overshifted = 0
    overpopped = 0
    stack = []
    last_push = None
    sentence_root = None
    num_shifts = 0
    for sr_command in sr_commands:
        if sr_command[0]=='R': #reduce
            (c_type, times, r_type) = parse_reduce_command_robust(sr_command)
            parent = ParseTree(r_type, None)
            for i in range(times):
                if len(stack)>0:
                    node = stack.pop()
                    assert(node.is_root())
                    node.set_parent(parent)
                else:
                    overpopped += 1

            if len(parent.children) > 0:
                parent.children.reverse() #compensate for popping off stack
                stack.append(parent)
                last_push=parent
        else: # if sr_command=='S': #shift 
            if num_shifts < len(tokens):
                leaf = ParseTree(None,tokens[num_shifts])
                stack.append(leaf)
                num_shifts += 1
            else:
                overshifted += 1
    #assert(len(stack)==1) #a valid sequence of SR commands should result in a tree

    if len(stack)==0: #whoops, we overpopped 
        sentence_root = last_push
    elif len(stack)==1: #almost perfect, we likely created a valid tree, nothing left to do!
        node = stack.pop()
        if node.data_type==None:#except in this case, we shifted one item and never reduced
            sentence_root = ParseTree('S', None)
            node.set_parent(sentence_root)
        else:
            sentence_root=node
    else: #whoops, we underpopped and have to create a new root node for the remaining items
        sentence_root = ParseTree('S', None)
        for i in range(len(stack)):
            node = stack.pop()
            assert(node.is_root())
            node.set_parent(sentence_root)
        sentence_root.children.reverse()

    undershifted = len(tokens) - num_shifts
    underpopped = len(stack) #must be defined here, after we popped the root

    #if we undershifted, just stuff 'em under the root node
    for i in range(undershifted):
        leaf = ParseTree(None,tokens[num_shifts])
        leaf.set_parent(sentence_root)
        num_shifts += 1
    if sentence_root is not None:
        assert(sentence_root.is_root())

    return [sentence_root,overshifted,undershifted,overpopped,underpopped]
         

def make_node_binary(node):
    #print 'Making node binary'
    #node.print_tree()
    #print '------------------'
    new_parent=None
    #pair-up children under a common sub-parent
    children = [child for child in node.children] #because set_parent will remove from old parent
    for i in range(len(children)):
        child = children[i]
        if i % 2 == 0:
            new_parent = ParseTree('bin_'+child.parent.data_type,None)
            new_parent.set_parent(node)
        child.set_parent(new_parent)
    #prune tree by removing linear chains
    children = [child for child in node.children] #because above operations changed children
    for child in children:
        if len(child.children) == 1:
            child.children[0].set_parent(node)
            child.set_parent(None)
    if len(children)==1:
        children[0].set_parent(None)
        grandchildren = [child for child in children[0].children]
        for grandchild in grandchildren:
            grandchild.set_parent(node)

def make_tree_binary(tree):
    for node in tree.traverse_preorder():
        make_node_binary(node)

def get_parents(nodes):
    parent_set = {node.parent for node in nodes if not node.parent==None}
    return parent_set

def nodes_to_examples(nodes):
    pass

def node_to_example(node, vector):
    pass

def remove_null_elements(tree):
    '''
    Removes null elements and index nodes e.g., (NP (-NONE- *)) and (S-TPC-1 ( ...)) from PTB style co-indexed annotation. Works on the .mrg version of the files.
    '''
    index_suffix = re.compile('.*\-[0-9]+$')
    def is_null_element(node):
        return node.data_type and node.data_type=='-NONE-'
    def is_target(node):
        return node.data_type and index_suffix.match(node.data_type)

    #remove null elements first or the assumption about a null element's parent might be wrong
    nodes = tree.traverse_preorder()
    for node in nodes:
        if is_null_element(node):
            '''
            then we have a null element structure to remove:
               VP (VBN used)
                  (NP (-NONE- *) )  <------remove me

            '''
            assert(node.is_leaf())
            assert(node.parent != None)
            #node.parent.set_parent(None)
            node.remove_subtree(True)
    #remove indexes
    nodes = tree.traverse_preorder()
    for node in nodes:
        if is_target(node): #remove this node, add its children to their grand parent
            '''
            then we have an index node to remove:
               ( (S
                    (S-TPC-1     <------remove index suffix
                       (NP-SBJ
            '''
            split = node.data_type.split('-')
            node.data_type = '-'.join(split[0:-1])     
            #if node.is_root():
            #    split = node.data_type.split('-')
            #    node.data_type = '-'.join(split[0:-1])
            #else:
            #    node.remove_node(True) #n.b. also adds children to their grandparent
        
    nodes = tree.traverse_preorder()
    for node in nodes:
        if node.is_leaf() and not node.data:
            node.set_parent(None)

def main(argv):
    print '-------------------'
    print 'testing parse trees'
    parse_string='''( (S 
    (NP-SBJ (NNP Mr.) (NNP Vinken) )
    (VP (VBZ is) 
      (NP-PRD 
        (NP (NN chairman) )
        (PP (IN of) 
          (NP 
            (NP (NNP Elsevier) (NNP N.V.) )
            (, ,) 
            (NP (DT the) (NNP Dutch) (VBG publishing) (NN group) )))))
   (. .) ))'''


    parse_string2 = '''( (S
    (S-TPC-1
      (NP-SBJ
        (NP
          (NP (DT A) (NN form) )
          (PP (IN of)
            (NP (NN asbestos) )))
        (RRC
          (ADVP-TMP (RB once) )
          (VP (VBN used)
            (NP (-NONE- *) )
            (S-CLR
              (NP-SBJ (-NONE- *) )
              (VP (TO to)
                (VP (VB make)
                  (NP (NNP Kent) (NN cigarette) (NNS filters) )))))))
      (VP (VBZ has)
        (VP (VBN caused)
          (NP
            (NP (DT a) (JJ high) (NN percentage) )
            (PP (IN of)
              (NP (NN cancer) (NNS deaths) ))
            (PP-LOC (IN among)
              (NP
                (NP (DT a) (NN group) )
                (PP (IN of)
                  (NP
                    (NP (NNS workers) )
                    (RRC
                      (VP (VBN exposed)
                        (NP (-NONE- *) )
                        (PP-CLR (TO to)
                          (NP (PRP it) ))
                        (ADVP-TMP
                          (NP
                            (QP (RBR more) (IN than) (CD 30) )
                            (NNS years) )
                          (IN ago) )))))))))))
    (, ,)
    (NP-SBJ (NNS researchers) )
    (VP (VBD reported)
      (SBAR (-NONE- 0)
        (S (-NONE- *T*-1) )))
    (. .) ))'''

    parse_tree = create_tree(parse_string)
    print '--------------------'
    print 'Original tree'
    print '  is binary?', parse_tree.is_binary()
    parse_tree.print_tree()

    remove_null_elements(parse_tree)
    print 'After removing null elements:'
    parse_tree.print_tree()
    #print 'FLATTENED:'
    #node_strs = [node.node_as_string() for node in parse_tree.children[0].traverse_preorder()]
    #print ' '.join(node_strs)
    print 'SENTENCE:'
    tokens = parse_tree.children[0].to_sentence()
    print tokens
    print ' '.join(tokens)
    print 'PARSE-COMMANDS:'
    parse_commands = parse_tree.children[0].to_SR_rich()
    print ' '.join(parse_commands)
    print 'TEST'
    [inp,out] = parse_to_encoder_decoder_line(parse_tree.children[0])
    print inp
    print out
    
    print 'RECONSTRUCTING TREE'
    omit = 4
    #parse_commands = parse_commands[0:omit] + parse_commands[omit+1:]
    [reconstructed,oshifted,ushifted,opopped,upopped] = perform_shift_reduce_robust(tokens, parse_commands)
    reconstructed.print_tree()
    print 'over shifted:',oshifted
    print 'under shiftd:',ushifted
    print 'over popped: ',opopped
    print 'under popped:',upopped
    
    print 'SEXP'
    print parse_tree.to_SEXP()
    

    #make_tree_binary(parse_tree)
    #print '--------------------'
    #print 'Binary tree'
    #print '  is binary?', parse_tree.is_binary()
    #parse_tree.print_tree()
    
    #create_encoder_decoder_file('/home/mwick/data/parsing/parsed/mrg/wsj/','test.sr')

if __name__ == "__main__":
    main(sys.argv[1:])
