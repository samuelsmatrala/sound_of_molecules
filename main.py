# NOTE: 'backend' is pre-created as a global variable
if 'backend' in globals():
    backend = globals()['backend']
    print("Backend successfully loaded:", backend)
else:
    print("The backend has not yet been initialized in the global scope.")

#IMPORTS
from QPE import QPE

#PROGRAM
QPE(backend = backend)