#!/usr/bin/env python
# -.- coding: utf-8 -.-

import os, sys, time, re
from optparse import OptionParser


def main(pattern, opts):

    source_dir = opts.src
    lists = os.listdir(source_dir)

    old_map = []
    new_map = []
    tmp_map = []

    # ------------
    # find old_map
    # ------------
    for i in lists:
        path = os.path.join(source_dir, i)
        if opts.type == 'f' and os.path.isfile(path):
            old_map.append(i)
        elif opts.type == 'd' and os.path.isdir(path):
            #old_map.append(i)
            
            ## auto sort by file created time
            t_latest = 0            
            # scan files            
            for j in os.listdir(path):
                fpath = os.path.join(path, j)
                if os.path.isfile(fpath):
                    t = os.path.getmtime(fpath)
                    if t > t_latest:
                        t_latest = t
            tmp_map.append([i, t_latest])
            
    if tmp_map:
        tmp_map = sorted(tmp_map, key=lambda x: x[1])
        for j in tmp_map:
            old_map.append(j[0])

    # ------------            
    # make new_map
    # ------------
    sort = 1

    # check is_seq
    seq = ''
    m = re.search('%0?[0-9]?d', pattern)
    if m:
        seq = m.group(0)
        
    else:
        if opts.add_seq:
            # add auto prefix, if needed                
            seq = '%02d'
            pattern = seq + pattern
            
    print 'seq:', seq

    def apply_pattern(fname, sort):

        # add seq and name
        pat = pattern.replace('%s', '{0}')
        if seq:
            pat = pat.replace(seq, '{1:%s}'%seq[1:])
            pat = pat.format(fname, sort)
        else:
            pat = pat.format(fname)

        # slice
        m = re.search('(.+)\[([0-9]*):([0-9]*)\]', pat)
        if m:
            start = int(m.group(2)) if m.group(2) else None
            end = int(m.group(3)) if m.group(3) else None
            pat = m.group(1)[start:end]
        return pat

    for i in old_map:
        
        name = ''
        path = os.path.join(source_dir, i)        
        if opts.type == 'f':
            (fname, fext) = os.path.splitext(i)
            
            name = apply_pattern(fname, sort) + fext
        elif opts.type == 'd':
            name = apply_pattern(i, sort)
            

        new_map.append(name)
        sort += 1

    
    print old_map
    print '--------'
    print new_map

    # ------------
    # apply rename
    # ------------
    idx = 0
    for i in old_map:

        if not opts.dry_run:
            src = os.path.join(source_dir, i)
            dst = os.path.join(source_dir, new_map[idx])
            os.rename(src, dst)           
        idx += 1

    
if __name__ == '__main__':

    parser = OptionParser(usage='light-my-file [options] PATTERN (ex: %02d_%s[m:n])')
    parser.add_option('-s', '--source_dir', dest='src', default='.',
                      help='source diretory to rename', metavar='SRC_DIR')
    parser.add_option('-t', '--type', dest='type', default='f',
                      help='file or dir')    
    parser.add_option('-y', '--prompt',
                      action='store_false', dest='prompt', default=True,
                      help='prompt')
    parser.add_option('-d', '--dry-run',
                      action='store_true', dest='dry_run', default=False,
                      help='dry run for test')
    parser.add_option('-a', '--add_seq', dest='add_seq', default=False,
                      action='store_true',
                      help='auto add_seq')
    (options, args) = parser.parse_args()

    #m = None
    #if args:
    #    m = re.search('%0?[0-9]?d', args[0])
        
    print 'opts:', options, 'args', args
    
    if not args:
        parser.print_help()
    elif '%s' not in args[0]:
        parser.print_help()
    #elif not m or not m.group(0):
    #    parser.print_help()        
    else:
        main(args[0], options)
