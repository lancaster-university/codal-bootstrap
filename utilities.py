def library_version( name ):
  try:
    return subprocess.check_output( "git rev-parse --short HEAD", cwd=os.path.join( BASE_ROOT, "libraries", name ), shell=True ).decode( 'utf-8' )
  except subprocess.CalledProcessError as err:
    Log.error( "library_version error:", err )
    return ""
  except FileNotFoundError as err:
    return ""