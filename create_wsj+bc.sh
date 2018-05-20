# copy wsj + bc (cctv, cnn, msnbc) train files to subdir/wsj+bc

data_dir="${HOME}/repository/data/OntoNoteParse"
cd $data_dir


##training edataset
#wsj
cp nw/wsj/split-train.* subdir/wsj+bc/
# cctv
cat bc/cctv/split-train.encode >> subdir/wsj+bc/split-train.encode
cat bc/cctv/split-train.decode >> subdir/wsj+bc/split-train.decode
# cnn
cat bc/cnn/split-train.encode >> subdir/wsj+bc/split-train.encode
cat bc/cnn/split-train.decode >> subdir/wsj+bc/split-train.decode
# msnbc
cat bc/msnbc/split-train.encode >> subdir/wsj+bc/split-train.encode
cat bc/msnbc/split-train.decode >> subdir/wsj+bc/split-train.decode

## test & dev
# cctv dataset
cp bc/cctv/split-test.* subdir/wsj+bc/
cp bc/cctv/split-development.decode subdir/wsj+bc/split-dev.decode
cp bc/cctv/split-development.encode subdir/wsj+bc/split-dev.encode

# cnn dataset 
cat bc/cnn/split-development.decode >> subdir/wsj+bc/split-dev.decode
cat bc/cnn/split-development.encode >> subdir/wsj+bc/split-dev.encode
cat bc/cnn/split-test.encode >> subdir/wsj+bc/split-test.encode
cat bc/cnn/split-test.decode >> subdir/wsj+bc/split-test.decode
# msnbc dataset
cat bc/msnbc/split-development.decode >> subdir/wsj+bc/split-dev.decode
cat bc/msnbc/split-development.encode >> subdir/wsj+bc/split-dev.encode
cat bc/msnbc/split-test.decode >> subdir/wsj+bc/split-test.decode
cat bc/msnbc/split-test.encode >> subdir/wsj+bc/split-test.encode


wc -l subdir/wsj+bc/split-*

cd -