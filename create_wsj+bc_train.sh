# copy wsj + bc (cctv, cnn, msnbc) train files to subdir/wsj+bc

data_dir="${HOME}/repository/data/OntoNoteParse"
cd $data_dir
##training edataset
# cctv
cat bc/cctv/split-train.encode >> subdir/bc/split-train.encode
cat bc/cctv/split-train.decode >> subdir/bc/split-train.decode
# cnn
cat bc/cnn/split-train.encode >> subdir/bc/split-train.encode
cat bc/cnn/split-train.decode >> subdir/bc/split-train.decode
# msnbc
cat bc/msnbc/split-train.encode >> subdir/bc/split-train.encode
cat bc/msnbc/split-train.decode >> subdir/bc/split-train.decode

wc -l subdir/bc/split-*

cd -