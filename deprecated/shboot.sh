#!/bin/sh

SHBOOTFILE=testforecho.sh
if [ ! -z $1 ]; then
    SHBOOTFILE=$1
fi

if [ -e ./$SHBOOTFILE ]; then
    echo "There's already a ./$SHBOOTFILE in the CWD (`pwd -P`), so this script is aborted."
    exit 1
fi

touch ./$SHBOOTFILE
echo "#!/bin/bash\n\nfunction puaq(){ # puaq stands for Print Usage And Quit\n  echo \"Usage: \`basename \$0\` param\"\n  exit 1\n}\n\nif [ -z \$1 ]; then\n  puaq\nfi\n\n#code goes here\n" > ./$SHBOOTFILE
chmod +x ./$SHBOOTFILE
