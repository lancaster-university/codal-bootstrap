#!/usr/bin/env python3

# The MIT License (MIT)

# Copyright (c) 2017 Lancaster University.

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

import json
import os
import sys
import urllib.request
import optparse

from importlib import import_module
from genericpath import exists

TARGET_LIST = [
    "https://raw.githubusercontent.com/lancaster-university/codal/master/utils/targets.json"
]
BASE_ROOT = os.getcwd()

if exists( os.path.join(BASE_ROOT, "codal.json") ) and exists( os.path.join(BASE_ROOT, "libraries", "codal", "build.py") ):
  sys.path.append( os.path.join(BASE_ROOT, "libraries", "codal") )
  import_module( f'libraries.codal.build' )
  exit( 0 )

parser = optparse.OptionParser(usage="usage: %prog target-name [options]", description="BOOTSTRAP MODE - Configures the current project directory for a specified target. Will defer to the latest build tools once configured.")
(options, args) = parser.parse_args()

def create_tree():
  path_list = [
    "libraries",
    "build",
    "source"
  ]
  for p in path_list:
    if not exists( os.path.join( BASE_ROOT, p ) ):
      os.mkdir( os.path.join( BASE_ROOT, p ) )
  
  with open(".gitignore", 'w') as git_ignore:
    git_ignore.writelines( [
      ".vscode"
      ".yotta.json"
      "*.bin"
      "*.DS_Store"
      "*.hex"
      "*.pyc"
      "*.swp"
      "*.uf2"
      "*~"
      "build"
      "buildcache.json"
      "codal.json"
      "libraries"
      "Makefile"
      "pxtapp"
      "yotta_modules"
      "yotta_targets"
    ] )

def download_targets():
  print( "Downloading valid targets..." )
  cache = {}
  for url in TARGET_LIST:
    r = urllib.request.urlopen( url )
    for t in json.load( r ):
      cache[ t["name"] ] = t
  return cache

def library_clone( url, name, branch = "master", specfile = "module.json" ):
  print( f'Downloading library {name}...' )
  git_root = os.path.join( BASE_ROOT, 'libraries', name )
  if not exists( os.path.join( git_root, '.git' ) ):
    os.system( f'git clone --branch "{branch}" "{url}" "{git_root}"' )

  if exists( os.path.join( git_root, specfile ) ):
    return load_json( os.path.join( git_root, specfile ) )

  print( f'WARN: Missing specification file for {name}: {specfile}' )
  return {}

def load_json( path ):
  with open(path, 'r') as src:
    return json.load( src )

if exists( os.path.join( BASE_ROOT, "codal.json" ) ):
  exit( "It looks like this project has already been configured, if this is not the case, delete codal.json and re-run this script." )

if len(args) == 0 or (len(args) == 1 and args[0] == "ls"):
  targets = download_targets()

  print( "Please supply an initial target to build against" )

  for t in targets:
    print( f'{t:<30}: {targets[t]["info"]}' )

if len(args) == 1:
  targets = download_targets()
  query = args[0]

  if query not in targets:
    exit( "Invalid or unknown target" )

  info = targets[query]

  create_tree()
  library_clone( "https://github.com/lancaster-university/codal.git", "codal" )

  print( "Downloading target support files..." )
  details = library_clone( info["url"], info["name"], branch = info["branch"], specfile = "target.json" )

  print( "Downloading libraries..." )
  for lib in details["libraries"]:
    library_clone( lib["url"], lib["name"], branch = lib["branch"] )

  with open( os.path.join( BASE_ROOT, "codal.json" ), "w" ) as codal_json:
    config = {
      "target": info
    }
    config["target"]["test_ignore"] = True
    config["target"]["dev"] = True

    json.dump( config, codal_json, indent=4 )