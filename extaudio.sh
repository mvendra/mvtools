
if [ -z $1 ]; then
  echo "Missing input file"
  exit 1
fi

if [ -z $2 ]; then
  echo "Missing output file"
  exit 2
fi

avconv -i $1 $2

