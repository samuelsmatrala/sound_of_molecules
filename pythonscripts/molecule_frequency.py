import numpy as np
from qiskit import QuantumCircuit

def molecule_frequency(backend):
  num = 30
  qc = QuantumCircuit(1, 1)
  qc.ry(np.pi/3,0)
  qc.measure(0, 0)
  print(qc)
  
  suma = np.zeros(num, dtype=int)
  
  for i in range(3):
      job = backend.run(qc, shots=num, memory=True)
      vysledky = np.array(job.result().get_memory(), dtype=int)
      suma += vysledky
  
  return suma
