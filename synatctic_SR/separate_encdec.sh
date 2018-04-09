#!/bin/bash
DATA_DIR=$1
OUT_DIR=$2
fname=$3

ENCODE_FILE="${OUT_DIR}/${fname}.encode"
DECODE_FILE="${OUT_DIR}/${fname}.decode"
# python parsing/DataUtils.py

echo "encode: ${ENCODE_FILE}"
echo "decode: ${DECODE_FILE}"
awk 'NR%2==1' ${DATA_DIR}/${fname} > "${ENCODE_FILE}"
awk 'NR%2==0' ${DATA_DIR}/${fname} > "${DECODE_FILE}"
