
if [[ $1 == "" ]] ; then
  echo "Missing input file"
  exit 0
fi

if [[ $2 == "" ]] ; then
  echo "Missing output file"
  exit 0
fi

openssl des3 -d -salt -in $1 -out $2

