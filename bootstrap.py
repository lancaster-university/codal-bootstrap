import json
from ntpath import join
import os
import sys
import shutil
import pathlib
import subprocess
import urllib.request
import optparse
from importlib import import_module
from genericpath import exists
from passthroughoptparser import PassThroughOptionParser
from log import Log
from colorama import Style

CODAL_URL = "https://github.com/lancaster-university/codal.git"
BASE_ROOT = os.getcwd()
BOOTSTRAP_ROOT = pathlib.Path(__file__).parent.absolute()

def library_version( name ):
  try:
    return subprocess.check_output( "git rev-parse --short HEAD", cwd=os.path.join( BASE_ROOT, "libraries", name ), shell=True ).decode( 'utf-8' )
  except subprocess.CalledProcessError as err:
    Log.error( F"library_version error: {err}" )
    return "BAD-VERSION"
  except FileNotFoundError as err:
    Log.error( F"library_version file not found: {err}" )
    return "BAD-REPO"

def create_tree():
  path_list = [
    "libraries",
    "docs",
    "build",
    "source"
  ]
  for p in path_list:
    if not exists( os.path.join( BASE_ROOT, p ) ):
      os.mkdir( os.path.join( BASE_ROOT, p ) )
  
  shutil.copy2(
    os.path.join( BOOTSTRAP_ROOT, "templates", "gitignore.template" ),
    os.path.join( BASE_ROOT, ".gitignore" )
  )


def download_targets( target_list ):
  Log.info( "Downloading valid targets..." )
  cache = {}
  for url in target_list:
    r = urllib.request.urlopen( url )
    for t in json.load( r ):
      cache[ t["name"] ] = t
  return cache

def library_clone( url, name, branch = "master", specfile = "module.json" ):
  Log.info( f'Downloading library {name}...' )
  git_root = os.path.join( BASE_ROOT, 'libraries', name )
  if not exists( os.path.join( git_root, '.git' ) ):
    os.system( f'git clone --recurse-submodules --branch "{branch}" "{url}" "{git_root}"' )

  if exists( os.path.join( git_root, specfile ) ):
    return load_json( os.path.join( git_root, specfile ) )

  Log.info( f'WARN: Missing specification file for {name}: {specfile}' )
  return {}

def load_json( path ):
  with open(path, 'r') as src:
    return json.load( src )

def library_update( name, branch="", specfile = "module.json"):
  Log.info( f'Updating library {name}...' )
  git_root = os.path.join( BASE_ROOT, 'libraries', name )
  if not exists( git_root ):
    raise Exception( f'No such library {name}' )
  
  if branch != "":
    try:
      subprocess.run( f'git checkout {branch}', cwd=git_root, shell=True )
    except subprocess.CalledProcessError as err:
      raise Exception( f'No such branch {branch} for library {name}' )

  try:
    subprocess.run( "git pull", cwd=git_root, shell=True )
  except subprocess.CalledProcessError as err:
    raise Exception( 'Unable to pull changes for ${name}' )

  if exists( os.path.join( git_root, specfile ) ):
    return load_json( os.path.join( git_root, specfile ) )

  Log.warn( f'WARN: Missing specification file for {name}: {specfile}' )
  return {}

def go_configure( info, config={} ):
  create_tree()
  library_clone( CODAL_URL, "codal", branch="feature/bootstrap" )

  # Copy out the base CMakeLists.txt, can't run from the library, and this is a CMake limitation
  # Note; use copy2 here to preserve metadata
  shutil.copy2(
    os.path.join( BASE_ROOT, "libraries", "codal", "CMakeLists.txt" ),
    os.path.join( BASE_ROOT, "CMakeLists.txt" )
  )

  Log.info( "Downloading target support files..." )
  details = library_clone( info["url"], info["name"], branch = info["branch"], specfile = "target.json" )

  # This is _somewhat_ redundant as cmake does this as well, but it might be worth doing anyway as there might be
  # additional library files needed for other, as-yet unidentified features. Plus, it makes the build faster afterwards -JV
  Log.info( "Downloading libraries..." )
  for lib in details["libraries"]:
    library_clone( lib["url"], lib["name"], branch = lib["branch"] )

  with open( os.path.join( BASE_ROOT, "codal.json" ), "w" ) as codal_json:
    config["target"] = info
    config["target"]["test_ignore"] = True
    config["target"]["dev"] = True

    json.dump( config, codal_json, indent=4 )
  
  print( "\n" )
  print( Style.BRIGHT + "All done! You can now start developing your code in the source/ folder. Running ./build.py will now defer to the actual build tools" )
  print( "Happy coding!" + Style.RESET_ALL )
  print( "" )

def list_valid_targets( target_list ):
  targets = download_targets( target_list )
  for t in targets:
    print( f'{t:<30}: {targets[t]["info"]}' )

def merge_json(base_obj, delta_obj):
  if not isinstance(base_obj, dict):
    return delta_obj
  common_keys = set(base_obj).intersection(delta_obj)
  new_keys = set(delta_obj).difference(common_keys)
  for k in common_keys:
    base_obj[k] = merge_json(base_obj[k], delta_obj[k])
  for k in new_keys:
    base_obj[k] = delta_obj[k]
  return base_obj

def go_build_docs():
  config = {
    "PROJECT_NAME": "default name",
    "PROJECT_NUMBER": "",
    "PROJECT_BRIEF": "",
    "PROJECT_LOGO": "",
    "INPUT": []
  }
  if( exists( os.path.join( BASE_ROOT, "docs.json" ) ) ):
    Log.info( "Merging user config from docs.json" )
    userConfig = load_json( os.path.join(BASE_ROOT, "docs.json") )
    config = merge_json( config, userConfig )
  
  def quoteString( _in ):
    return '"' + str(_in) + '"'

  for key in set(config):
    if type(config[key]) == list:
      config[key] = map( quoteString, config[key] )
      config[key] = " \\\n                         ".join( config[key] )
    else:
      config[key] = '"' +config[key]+ '"'
  
  for lib in os.listdir( os.path.join(BASE_ROOT, "libraries") ):
    libdef = os.path.join(BASE_ROOT, "libraries", lib, "library.json")
    if exists( libdef ):
      Log.info( F"Including {lib} documentation..." )
      libspec = load_json( libdef )
      if "docs" in libspec and "INPUT" in libspec["docs"]:
        print( config["INPUT"] )
        config["INPUT"].extend( os.path.join(BASE_ROOT, "libraries", lib, libspec["docs"]["INPUT"] ) )

  with open( os.path.join( BOOTSTRAP_ROOT, "templates", "Doxyfile.template" ), 'r' ) as template:
    with open( os.path.join( BASE_ROOT, "Doxyfile" ), 'w' ) as output:
      for line in template.readlines():
        for key in set(config):
          line = line.replace( "{{" +key+ "}}", config[key] )
        output.write( line );
  
  Log.info( "Building with doxygen..." )
  os.system( F'doxygen "{os.path.join( BASE_ROOT, "Doxyfile" )}"' )

def go_bootstrap( target_list ):
  if exists( os.path.join(BASE_ROOT, "codal.json") ) and exists( os.path.join(BASE_ROOT, "libraries", "codal", "build.py") ):
    parser = PassThroughOptionParser(add_help_option=False)
    parser.add_option('--bootstrap', dest='force_bootstrap', action="store_true", default=False)
    (options, args) = parser.parse_args()

    if options.force_bootstrap:
      Log.warn( "WARNING: '--bootstrap' forces bootstrap to take over, downloaded build tools will not be run!" )

    if not options.force_bootstrap:
      sys.path.append( os.path.join(BASE_ROOT, "libraries", "codal") )
      import_module( f'libraries.codal.build' )
      exit(0)

  parser = optparse.OptionParser(usage="usage: %prog target-name [options]", description="BOOTSTRAP MODE - Configures the current project directory for a specified target. Will defer to the latest build tools once configured.")
  parser.add_option('--bootstrap', dest='force_bootstrap', action='store_true', help="Skips any already downloaded build toolchain, and runs in bootstrap mode directly.", default=False)
  parser.add_option('--ignore-codal', dest='ignore_codal', action='store_true', help="Skips any pre-existing codal.json in the project folder, and runs as if none exists.", default=False)
  parser.add_option('--merge-upstream-target', dest='merge_upstream_target', action='store_true', help="Keeps the existing codal.json, but only for non-target parameters, merging the new target definition in with the old arguments.", default=False)
  parser.add_option('--makedocs', dest='makedocs', action='store_true', help='Builds documentation (including supported libraries) with doxygen')
  parser.add_option('-u', dest='update', action='store_true', help="Update this file and the build tools library", default=False)
  (options, args) = parser.parse_args()

  if options.makedocs:
    go_build_docs()
    exit(0)

  if options.update:
    Log.info( "Attempting to automatically update bootstrap..." )
    old_vers = library_version( 'codal-bootstrap' )
    if exists(os.path.join( BASE_ROOT, "libraries", "codal-bootstrap" )):
      library_update( "codal-bootstrap" )
    else:
      library_clone( "https://github.com/lancaster-university/codal-bootstrap.git", "codal-bootstrap", branch="main" )
    vers = library_version( 'codal-bootstrap' )
    
    if vers == old_vers:
      Log.info( "Nothing to update, codal-bootstrap is already the latest version" )
      exit( 0 )

    Log.info( "Downloaded a new version of bootstrap, updating the project files..." )
    shutil.copy2(
      os.path.join( BASE_ROOT, "libraries", "codal-bootstrap", "build.py" ),
      os.path.join( BASE_ROOT, "build.py" )
    )

    Log.info( "Done! Happy coding :)\n" )

    exit(0)

  if len(args) == 0:
    # We might have an existing device config already, so grab that and try and pull that...
    if exists( os.path.join( BASE_ROOT, "codal.json" ) ) and not options.ignore_codal:
      Log.info( "Project already has a codal.json, trying to use that to determine the build system and any missing dependencies..." )
      local_config = load_json( os.path.join( BASE_ROOT, "codal.json" ) )
      local_target = local_config["target"]

      print( "Configuring from codal.json!" )
      go_configure( local_target )
      exit(0)

    Log.warn( "Please supply an initial target to build against:" )
    list_valid_targets( target_list )
    exit( 0 )

  if len(args) == 1:

    # 'Magic' target to list all targets
    if args[0] == "ls":
      Log.info( "Available target platforms:" )
      list_valid_targets( target_list )
      exit( 0 )
    
    targets = download_targets( target_list )
    query = args[0]

    if query not in targets:
      Log.error( "Invalid or unknown target, try './build.py ls' to see available targets" )
      exit( 1 )

    local_config = {}
    if options.merge_upstream_target:
      Log.info( "Preserving local configuration, but ignoring the target and using supplied user target..." )
      local_config = load_json( os.path.join( BASE_ROOT, "codal.json" ) )

    go_configure( targets[query], config=local_config )