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
  from pythonscripts.sound import sound
  
  #PROGRAM
  MOLECULES = ["H3+", "H2", "H2+", "HeH+", "Li+", "H4"]
  qpe_result = QPE(backend = backend, SELECTED_MOLECULE = MOLECULES[0])
  mol_frequency = molecule_frequency(backend = backend)
  audio_data = sound() # Predpokladáme, že sound() vracia slovník {"audio": [...], "sampleRate": 44100}
  
  # Vráťme všetko pekne do JS ako slovník
  return {
      "qpe": qpe_result,
      "moleculeFrequency": mol_frequency,
      "audio": audio_data["audio"],
      "sampleRate": audio_data["sampleRate"]
  }
