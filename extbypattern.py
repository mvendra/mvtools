#!/usr/bin/env python

import sys
import os

import path_utils

class extractpattern:

    def __init__(_self, infile, beginpattern, endpattern, baseoutputfilename = None):
        _self.infile = infile
        _self.beginpattern = beginpattern
        _self.endpattern = endpattern
        _self.baseoutputfilename = baseoutputfilename

        if _self.baseoutputfilename == None:
            _self.baseoutputfilename = infile # no base output filename was provided. we'll just reuse the input filename

        auxstr = _self.baseoutputfilename.split(".")
        if len(auxstr) == 2: # the provided output filename came with extension
            _self.baseoutputfilename = auxstr[0]
            _self.outext = auxstr[1]
        elif len(auxstr) == 1: # the provided output filename came WITHOUT extension. lets add some default
            _self.outext = ".txt"
        elif len(auxstr) > 2: # great... a filename with dots midway
            _self.baseoutputfilename = _self.baseoutputfilename[:_self.baseoutputfilename.rfind(".")]
            _self.outext = auxstr[len(auxstr)-1]

    def doesmatch(_self, content, offset, pattern):
        i=0
        while i < len(pattern):
            try:
                if content[offset+i] != pattern[i]:
                    return False
            except IndexError:
                return False
            i+=1
        return True

    def findpattern(_self, content, offset, pattern):
        i = offset
        while i < len(content):
            if _self.doesmatch(content, i, pattern):
                return i
            i+=1
        return -1
        
    def process(_self):
        outnum=0;
        with open(_self.infile, "rb") as f:
            content = f.read()
            i=0
            while (True):

                # find new happenstance of pattern pair
                b_off = _self.findpattern(content, i, _self.beginpattern)
                if b_off == -1:
                    break
                e_off = _self.findpattern(content, b_off, _self.endpattern)
                if e_off == -1:
                    break

                e_off+=len(_self.endpattern)
                i = e_off

                # write it out
                newcontent = content[b_off:e_off]
                outnum+=1
                newfile = _self.baseoutputfilename + str(outnum) + "." + _self.outext
                newfile = path_utils.concat_path(".", newfile)
                with open(newfile, "wb+") as nf:
                    nf.write(newcontent)

def extbypattern(file_in, file_out):

    beginpattern = [0x89, 0x50, 0x4E, 0x47] # header of a png image
    endpattern = [0x49, 0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82] # trailing of a png image

    epinst = extractpattern(file_in, beginpattern, endpattern, file_out)
    epinst.process()

def puaq(selfhelp):
    print("Usage: %s inputfilename [baseoutputfilename]" % path_utils.basename_filtered(__file__))
    if selfhelp:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":

    fileout = None

    if len(sys.argv) < 2:
        puaq(False)
    elif len(sys.argv) > 2:
        fileout = sys.argv[2]

    filein = sys.argv[1]
    extbypattern(filein , fileout)
