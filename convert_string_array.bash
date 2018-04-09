IN="/zfsauton/home/jaylee/repository/data/OntoNoteParse/wb/"
IFS='/' read -r -a array <<< "$IN"
echo ${array[*]}
let id=${#array[*]}-1
echo $id
echo ${array[id]}