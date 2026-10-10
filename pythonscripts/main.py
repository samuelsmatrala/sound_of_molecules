def main(backend):
  # NOTE: 'backend' is pre-created as a global variable
  if 'backend' in globals():
      backend = globals()['backend']
      print("Backend successfully loaded:", backend)
  else:
      print("The backend has not yet been initialized in the global scope.")
  
  #IMPORTS
  from pythonscripts.QPE import QPE 
  from pythonscripts.molecule_frequency import molecule_frequency
  
  #PROGRAM
  MOLECULES = ["H3+", "H2", "H2+", "HeH+", "Li+", "H4"]
  return QPE(backend = backend, SELECTED_MOLECULE = MOLECULES[0]), molecule_frequency(backend = backend)
