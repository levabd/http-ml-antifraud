#!/usr/bin/env python
import os


def split_file(infile, prefix, max_size=50*1024*1024, file_buffer=1024):
    """
    file: the input file
    prefix: prefix of the output files that will be created
    max_size: maximum size of each created file in bytes
    buffer: buffer size in bytes

    Returns the number of parts created.
    """
    with open(infile, 'r+b') as src:
        suffix = 0
        while True:
            with open(prefix + '.%s' % suffix, 'w+b') as tgt:
                written = 0
                while written < max_size:
                    data = src.read(file_buffer)
                    if data:
                        tgt.write(data)
                        written += file_buffer
                    else:
                        return suffix
                suffix += 1


def cat_files(infiles, outfile, file_buffer=1024):
    """
    infiles: a list of files
    outfile: the file that will be created
    buffer: buffer size in bytes
    """
    if os.path.isfile(outfile):
        os.remove(outfile)
    with open(outfile, 'w+b') as tgt:
        for infile in sorted(infiles):
            with open(infile, 'r+b') as src:
                while True:
                    data = src.read(file_buffer)
                    if data:
                        tgt.write(data)
                    else:
                        break
