#!/usr/bin/env python3

# The MIT License (MIT)

# Copyright (c) 2022 Lancaster University.

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import subprocess

WORK_DIR = os.getcwd()

def runAndGetReturn( cmd ):
    result = subprocess.run( cmd, stdout=subprocess.PIPE )
    return result.stdout.decode( 'utf8' )

finalReport = []
for file in os.listdir( os.path.join( WORK_DIR, 'build' ) ):
    if( str(file).endswith( '.a' ) ):
        report = runAndGetReturn( [
            'arm-none-eabi-size',
            os.path.join( WORK_DIR, 'build', file )
        ] )

        reportData = report.split('\n')
        for line in reportData:
            if( len(line) > 0 and not line.strip().startswith('text	   data	    bss	    dec	    hex	filename')):
                info = line.split("(")[0].split('\t')
                info = [s.strip() for s in info]

                finalReport.insert( 0, info )

def sortFunc( x ):
    return x[5]

print( '\t'.join( ['text', 'data', 'bss', 'dec', 'hex', 'filename'] ) )
output = sorted( finalReport, key=sortFunc )
for entry in output:
    print( '\t'.join(entry) )