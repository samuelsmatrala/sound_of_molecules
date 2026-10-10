import numpy as np
from qiskit import QuantumCircuit

def molecule_frequency(backend):
  qc = QuantumCircuit(1, 1)
  qc.h(0)
  qc.measure(0, 0)
  print(qc)
  
  suma = np.zeros(10, dtype=int)
  
  for i in range(3):
      job = backend.run(qc, shots=10, memory=True)
      vysledky = np.array(job.result().get_memory(), dtype=int)
      suma += vysledky
  
  return suma
