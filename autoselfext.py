#!/usr/bin/env python

import os
import sys
from subprocess import call

class secexcept(RuntimeError):
    def __init__(_self, msg):
        _self.message = msg

class selfextractorcreator:

    def __init__(_self, in_inst, in_pack, outfile):

        _self.input_inst = os.path.abspath(in_inst)
        _self.input_pack = os.path.abspath(in_pack)
        _self.outputfn = os.path.abspath(outfile)

        if not os.path.exists(_self.input_inst):
            raise secexcept("Input instructions file does not exist")

        if not os.path.exists(_self.input_pack):
            raise secexcept("Input package file does not exist")

        if os.path.exists(_self.outputfn):
            raise secexcept("%s already exists and I refuse to overwrite" % outfile)

    def _filecontents(_self, fname):
        ret = None
        with open(fname) as f:
            ret = f.read()
        return ret

    def inst_contents(_self):
        return _self._filecontents(_self.input_inst)

    def pack_contents(_self):
        return _self._filecontents(_self.input_pack)

    def template_contents(_self, inst, pack):

        template_edit = """#!/bin/bash

echo "Extracting..."

NAME_SELF=`basename $0`

OUT_INST=nop
OUT_PACK=nop

SIZE_INST=nop
SIZE_PACK=nop

# get byte offset of all magic string matches
FINDSENT=`grep -a "SENTINEL" --byte-offset --only-matching $NAME_SELF`
OFFSET_INST=""

# retrieves the last ocurrence of the magic string
for sents in $FINDSENT; do
    OFFSET_INST=${sents%%":SENTINEL"}
done

# check whether we did find the inst offset or not at all
if [ -z $OFFSET_INST ]; then
    echo "Unable to find instructions offset. Bailing out."
    exit 1
fi

# calc offsets
OFFSET_INST=$((OFFSET_INST + 9))
OFFSET_PACK=$((OFFSET_INST + SIZE_INST))

# extracts instruction script
dd skip=$OFFSET_INST count=$SIZE_INST if=$NAME_SELF of=$OUT_INST bs=1 &>/dev/null
chmod +x $OUT_INST

# extracts package file
dd skip=$OFFSET_PACK count=$SIZE_PACK if=$NAME_SELF of=$OUT_PACK bs=1 &>/dev/null

echo "Done. Will now run the embedded script."

# runs instruction script
source $OUT_INST

rm -rf ./$OUT_INST

exit 0 #SENTINEL\n"""

        # write names
        template_edit = template_edit.replace("OUT_INST=nop", "OUT_INST=%s" % os.path.basename(_self.input_inst))
        template_edit = template_edit.replace("OUT_PACK=nop", "OUT_PACK=%s" % os.path.basename(_self.input_pack))

        # write sizes
        template_edit = template_edit.replace("SIZE_INST=nop", "SIZE_INST=%s" % os.path.getsize(_self.input_inst))
        template_edit = template_edit.replace("SIZE_PACK=nop", "SIZE_PACK=%s" % os.path.getsize(_self.input_pack))

        return template_edit

    def produce(_self):
        inst_ct = _self.inst_contents()
        pack_ct = _self.pack_contents()
        templ_ct = _self.template_contents(inst_ct, pack_ct)

        with open(_self.outputfn, 'w') as f:
            f.write(templ_ct)
            f.write(inst_ct)
            f.write(pack_ct)

        call(["chmod", "+x", _self.outputfn])

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("Usage: %s input_instructionsfile.sh input_packagefile.tar.gz output_filename.sh" % os.path.basename(__file__))
        sys.exit(1)

    infile_inst = sys.argv[1]
    infile_pack = sys.argv[2]
    outfile = sys.argv[3]

    try:
        sec = selfextractorcreator(infile_inst, infile_pack, outfile)
        sec.produce()
    except secexcept as sx:
        print("Failed: %s" % sx.message)

