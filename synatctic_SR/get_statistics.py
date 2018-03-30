# ==============================================================================
"""Utility to handle text file formatting before handing it to tensorflow.
The goal is to have unified mechanism in splitting 
"""
# ==============================================================================
import argparse
import codecs
import os
import nltk.tokenize
import re
# import tensorflow as tf
import numpy as np
from itertools import izip
# from ..utils import misc_utils as utils
import matplotlib.pyplot as plt

_WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")
_DIGIT_RE = re.compile(br"\d")


UNK = "<unk>"
SOS = "<s>"
EOS = "</s>"
UNK_ID = 0
_START_VOCAB = [UNK, SOS, EOS]


def basic_tokenizer(sentence):
  """Very basic tokenizer: split the sentence into a list of tokens."""
  words = []
  for space_separated_fragment in sentence.strip().split():
    words.extend(_WORD_SPLIT.split(space_separated_fragment))
  return [w for w in words if w]

def process_txt_files(data_path, tokenizer=nltk.tokenize.word_tokenize,
                                               normalize_digits=False, lowercase=False):
  """
  non-tensorflow version of process_txt_files_tf().
  processing txt file to be delimited by space ' ' to feed it to
  multiple training models. As they will all have different preprocessing steps.
  The goal is to unify the creating vocab & processing the txt file.

  Args:
    data_path: data file. (that will also be used to create vocabulary)
    tokenizer: a function to use to tokenize each data sentence;
      if None, nltk tokenizer will be used. (default: nltk.tokenize.work_toeknize)
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """
  new_file_path= data_path+"-tok" # add suffix to notify the change
  if normalize_digits:
    new_file_path += "-digitnorm"
  if lowercase:
    new_file_path += "-lowercase"

  if os.path.isfile(new_file_path):
    print("the new file attempted to create already exists %s" % (new_file_path))
    return


  if os.path.isfile(data_path):
    print("Creating modified %s from data %s" % (new_file_path, data_path))
    with open(data_path, mode="rb") as f:
      with open(new_file_path, mode="wb") as new_file:
        counter = 0
        for line in f:
          counter += 1
          # if counter >100:
          #   break
          if counter % 100000 == 0:
            print("  processing line %d" % counter)
          if lowercase:
            line = line.lower()
          tokens = tokenizer(line) if tokenizer else line.strip().split(' ')
          for i, w in enumerate(tokens):
            tokens[i] = _DIGIT_RE.sub(b"0", w) if normalize_digits else w
          new_file.write( " ".join(tokens) + b"\n")
  else:
    print("data file does not exist on data_path: %s, cannot process" %(data_path))


def process_txt_files_tf(data_path, tokenizer=None,
                                               normalize_digits=False, lowercase=False):
  """processing txt file to be delimited by space ' ' to feed it to
  multiple training models. As they will all have different preprocessing steps.
  The goal is to unify the creating vocab & processing the txt file.

  Args:
    data_path: data file. (that will also be used to create vocabulary)
    tokenizer: a function to use to tokenize each data sentence;
      if None, nltk tokenizer will be used. (default: nltk.tokenize.work_toeknize)
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """
  new_file_path= data_path+"-tok" # add suffix to notify the change
  if normalize_digits:
    new_file_path += "-digitnorm"
  if lowercase:
    new_file_path += "-lowercase"

  if os.path.isfile(new_file_path):
    print("the new file attempted to create already exists %s" % (new_file_path))
    return


  if os.path.isfile(data_path):
    print("Creating modified %s from data %s" % (new_file_path, data_path))
    with tf.gfile.GFile(data_path, mode="rb") as f:
      with tf.gfile.GFile(new_file_path, mode="wb") as new_file:
        counter = 0
        for line in f:
          counter += 1
          # if counter >100:
          #   break
          if counter % 100000 == 0:
            print("  processing line %d" % counter)
          line = tf.compat.as_bytes(line)
          if lowercase:
            line = line.lower()
          tokens = tokenizer(line) if tokenizer else line.strip().split(' ')
          for i, w in enumerate(tokens):
            tokens[i] = _DIGIT_RE.sub(b"0", w) if normalize_digits else w
          new_file.write( " ".join(tokens) + b"\n")
  else:
    print("data file does not exist on data_path: %s, cannot process" %(data_path))


def create_vocab_file(train_dir, vocabulary_path, data_path, max_vocabulary_size,
                      tokenizer=None, 
                      normalize_digits=False, lowercase=False):
  """Create vocabulary file (if it does not exist yet) from data file.
  
  --> Changed every parameter to become None & False 
      for tokenizer, norm_digits, lowercase, 
      as the text should be processed accordingly 
      and vocab should just read and memorize for the unity.

  -- Borrowed from the tensorflow seq2seq tutorial --
  Data file is assumed to contain one sentence per line. Each sentence is
  tokenized and digits are normalized (if normalize_digits is set).
  Vocabulary contains the most-frequent tokens up to max_vocabulary_size.
  We write it to vocabulary_path in a one-token-per-line format, so that later
  token in the first line gets id=0, second line gets id=1, and so on.

  Args:
    vocabulary_path: path where the vocabulary will be created. 
    --> in order to create lowwercase or normalized digit vocab, 
    then make sure you pass the vocab_path name accordingly for consistency.
    data_path: data file that will be used to create vocabulary.
    max_vocabulary_size: limit on the size of the created vocabulary.
    tokenizer: a function to use to tokenize each data sentence;
      if None, basic_tokenizer will be used.
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """

  if not tf.gfile.Exists(vocabulary_path):
    if not os.path.exists(train_dir):
      os.makedirs(train_dir)
    print("Creating vocabulary %s from data %s" % (vocabulary_path, data_path))
    vocab = {}
    with tf.gfile.GFile(data_path, mode="rb") as f:
      counter = 0
      for line in f:
        counter += 1
        if counter % 100000 == 0:
          print("  processing line %d" % counter)
        line = tf.compat.as_bytes(line)
        if lowercase:
          line = line.lower()
        tokens = tokenizer(line) if tokenizer else line.strip().split(' ')
        for w in tokens:
          word = _DIGIT_RE.sub(b"0", w) if normalize_digits else w
          if word in vocab:
            vocab[word] += 1
          else:
            vocab[word] = 1
      vocab_list = _START_VOCAB + sorted(vocab, key=vocab.get, reverse=True)
      if len(vocab_list) > max_vocabulary_size:
        vocab_list = vocab_list[:max_vocabulary_size]
      with tf.gfile.GFile(vocabulary_path, mode="wb") as vocab_file:
        for w in vocab_list:
          vocab_file.write(w + b"\n")
  else:
    print("Vocabulary file %s already exists, thus skipping the step." %(vocabulary_path))


def max_token_cnt(tgt_path, src_path=None, tokenizer=None,
                                               normalize_digits=False, lowercase=False):
  """processing txt file to be delimited by space ' ' to feed it to
  multiple training models. As they will all have different preprocessing steps.
  The goal is to unify the creating vocab & processing the txt file.

  Args:
    tgt_path: data file. (that will also be used to create vocabulary)
    tokenizer: a function to use to tokenize each data sentence;
      if None, nltk tokenizer will be used. (default: nltk.tokenize.work_toeknize)
    normalize_digits: Boolean; if true, all digits are replaced by 0s.
  """
  
  print('tgt: %s' %tgt_path)
  if src_path is None:
    max_length=0
    if os.path.isfile(tgt_path):
      with tf.gfile.GFile(tgt_path, mode="rb") as f:
        counter = 0
        for line in f:
          counter += 1
          if counter % 10000 == 0:
            print("  processing line %d" % counter)
          line = tf.compat.as_bytes(line)
          tokens = tokenizer(line) if tokenizer else line.strip().split(' ')
          if len(tokens)>max_length:
            max_length=len(tokens)
            print('line count: %d, and legnth: %d'%(counter, max_length))
    else:
      print("data file does not exist on data_path: %s, cannot process" %(tgt_path))
    print('===================================================')
    print('max_length %d' %max_length)
  else: 
    len_src, len_tgt=[],[]
    max_tgt_len, max_src_len, max_ratio= 0, 0, 0.0
    print('src: %s' %src_path)
    with open(src_path) as textfile1, open(tgt_path) as textfile2: 
      for x, y in izip(textfile1, textfile2):
          x_list = tokenizer(x) if tokenizer else x.strip().split(' ')
          y_list = tokenizer(y) if tokenizer else y.strip().split(' ')
          len_src.append(len(x_list))
          len_tgt.append(len(y_list))

    print('src: %d'%np.max(len_src))
    print(np.histogram(len_src))
    print('tgt: %d'%np.max(len_tgt))
    print(np.histogram(len_tgt))
    ratio_list = np.array(len_tgt)/np.array(len_src)+0.0
    print('ratio %f'%np.max(ratio_list))
    print(np.histogram(ratio_list))
    
    # print(np.histogram(len_tgt))
      #     enc_dec_ratio = len(y_list)/(len(x_list)+0.0)
      #     if len(x_list)>max_src_len:
      #       max_src_len=len(x_list)
      #     if len(y_list)>max_tgt_len:
      #       max_tgt_len=len(y_list)
      #     if enc_dec_ratio> max_ratio:
      #       max_ratio = enc_dec_ratio
      #       print('max_ratio %f, corresponding dec len: %d' %(max_ratio,len(y_list)))
      # print('===================================================')
      # print('src max len: %d, tgt max len: %d, max_ratio %f' %(max_src_len,max_tgt_len,max_ratio))


def add_arguments(parser):
  #register type bool
  argparser.register("type", "bool", lambda v: v.lower() == "true")
  
  # add arguments
  parser.add_argument("--tokenize_new_txt", type=bool, default=False,
                      help="command to tokenize new file")
  parser.add_argument("--create_vocab", type=bool, default=False,
                      help="command to tokenize new file")
  parser.add_argument("--WSJ_dataset", type=bool, default=False,
                      help="special treatment for WSJ --> do not normalize digits of decoding commands")
  parser.add_argument("--lowercase", type=bool, default=False,
                      help="flag to lowercase the tokens")
  parser.add_argument("--normalize_digits", type=bool, default=False,
                      help="flag to normalize the digits")
  parser.add_argument("--train_dir", type=str, default=None,
                      help="directory path to train_dir, typically I will put vocab file into train dir")
  parser.add_argument("--from_vocab_path", type=str, default=None,
                      help="directory path to vocabulary file")
  parser.add_argument("--to_vocab_path", type=str, default=None,
                      help="directory path to vocabulary file")
  parser.add_argument("--from_data", type=str, default=None, help="source data.")
  parser.add_argument("--from_dev", type=str, default=None, help="source data.")
  parser.add_argument("--from_test", type=str, default=None, help="source data.")
  parser.add_argument("--to_data", type=str, default=None, help="target data.")
  parser.add_argument("--to_dev", type=str, default=None, help="target data.")
  parser.add_argument("--to_test", type=str, default=None, help="target data.")
  parser.add_argument("--from_vocab_size", type=int, default=50000, help="src vocabulary size.")
  parser.add_argument("--to_vocab_size", type=int, default=50000, help="src vocabulary size.")

if __name__ == "__main__":
  # argparser = argparse.ArgumentParser()
  # add_arguments(argparser)
  # FLAGS, unparsed = argparser.parse_known_args()

  # if FLAGS.tokenize_new_txt:
  #   print("Preparing new tokezniation for given datatset")
  #   if FLAGS.WSJ_dataset:
  #     print("WSJ, only preparing digit normalization on encoder")
  #     process_txt_files_tf(FLAGS.from_data, tokenizer=None, 
  #                                           normalize_digits=True, #FLAGS.normalize_digits, 
  #                                         lowercase=FLAGS.lowercase)
  #     process_txt_files_tf(FLAGS.from_dev, tokenizer=None, 
  #                                     normalize_digits=True, #FLAGS.normalize_digits, 
  #                                   lowercase=FLAGS.lowercase)
  #     process_txt_files_tf(FLAGS.from_test, tokenizer=None, 
  #                                           normalize_digits=True, #FLAGS.normalize_digits, 
  #                                         lowercase=FLAGS.lowercase)

  #   else:
  #     process_txt_files_tf(FLAGS.from_data, tokenizer=nltk.tokenize.word_tokenize, # encoder
  #                                           normalize_digits=True, #FLAGS.normalize_digits, 
  #                                           lowercase=FLAGS.lowercase)
  #     process_txt_files_tf(FLAGS.to_data, tokenizer=nltk.tokenize.word_tokenize, # decoder
  #                                           normalize_digits=FLAGS.normalize_digits, lowercase=FLAGS.lowercase)
  # if FLAGS.create_vocab:
  #   # create vocabulary for encoder
  #   create_vocab_file(FLAGS.train_dir, FLAGS.from_vocab_path, FLAGS.from_data, FLAGS.from_vocab_size, 
  #                                         normalize_digits=FLAGS.normalize_digits, lowercase=FLAGS.lowercase)
  #   # create vocabulary for decoder
  #   if FLAGS.WSJ_dataset: # s R# should be preserved
  #     create_vocab_file(FLAGS.train_dir, FLAGS.to_vocab_path, FLAGS.to_data, FLAGS.to_vocab_size, 
  #                                         normalize_digits=False, lowercase=FLAGS.lowercase)
  #   else:  
  #     create_vocab_file(FLAGS.train_dir, FLAGS.to_vocab_path, FLAGS.to_data, FLAGS.to_vocab_size,
  #                                         normalize_digits=FLAGS.normalize_digits, lowercase=FLAGS.lowercase)

  # #getting data statistics
  datadir="/Users/jaylee/GoogleDrive_andrew/repository/data/WSJ_parse"
  max_token_cnt(datadir+'/split-train.decode',datadir+'/split-train.encode')
  max_token_cnt(datadir+'/split-dev.decode',datadir+'/split-dev.encode')
  max_token_cnt(datadir+'/split-test.decode',datadir+'/split-test.encode')
