import sys
import io
import argparse

# import parsing.ParseTrees as pt

def sr_hybrid_tokenizer(line):
    return sr_tokenizer(line, lambda x:x.lower(), tokenize_reduce_hybrid)

def sr_tokenizer(line, s_tokenizer, r_tokenizer):
    commands = line.split(' ')
    result = []
    for command in commands:
        if command[0]=='S':
            assert len(command[0])==1
            result.append(s_tokenizer(command))
        elif command[0]=='R':
            result += r_tokenizer(command)
    return result 

def tokenize_reduce_hybrid(reduce_command):
    assert reduce_command[0]=='R'
    tokens = reduce_command.split('-')
    #tokens = [tokens[0][0]] + [tokens[0][1:]] + tokens[1:]
    return tokens

def hybrid_tokens_to_sr_commands(tokens):
    ''' tokens: string array.
    '''
    commands = []
    current_command=[]
    seen_reduce=False
    for token in tokens:
        if token[0]=='s': 
            #if we've finished the previous reduce command, then add it before shifting
            if len(current_command)>0:
                commands.append('-'.join(current_command))
                current_command=[]
            #add shift command
            commands.append(token.upper())
        elif token[0]=='R':
            #if we've finished previous reduce command, then add it before starting next one
            if len(current_command)>0:
                commands.append('-'.join(current_command))
            #add next reduce command
            current_command = [token]
        else:
            #build up the reduce command token by token
            current_command.append(token)
    if len(current_command)>0:
        commands.append('-'.join(current_command))
    return commands

def normalize_sr_commands(sr_commands, reduce_normalizer=lambda x:x):
    result = []
    num_shifts = 0
    for command in sr_commands:
        if command[0]=='S':
            num_shifts += 1
        elif command[0]=='R':
            if num_shifts>0:
                result.append('S' + str(num_shifts))
            result.append(reduce_normalizer(command))
            num_shifts = 0
        else:
            #result.append('X')
            result.append(command)
            #raise ValueError('Error, invalid SR command:'+command)
    if num_shifts>0:
        result.append('S' + str(num_shifts))
    return result

def main(f_input, f_output):
    # '''
    input_sentence = 'S S S R3-NP R2-PP-TMP S S S R5-S'
    tokens = sr_hybrid_tokenizer(input_sentence)

    print 'original',input_sentence
    print 'tokens',tokens
   
    with io.open(args.input_filename) as input_file:
      with io.open(args.output_filename, mode='w') as output_file: 
        for line in input_file:
            tokens = sr_hybrid_tokenizer(line)
            output_file.write(' '.join(tokens))
    ## outputs from running "python convert-SR2sR.py"
    # original S S S R3-NP R2-PP-TMP S S S R5-S
    # tokens ['s', 's', 's', 'R3', 'NP', 'R2', 'PP', 'TMP', 's', 's', 's', 'R5', 'S']

    
  
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--input_filename", required=True)
    argparser.add_argument("-o", "--output_filename", required=True)
    args = argparser.parse_args()

    main(args.input_filename, args.output_filename)
