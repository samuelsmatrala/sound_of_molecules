import numpy as np
from qiskit import QuantumCircuit

def molecule_frequency(backend):
  num = 36
  qc = QuantumCircuit(1, 1)
  qc.ry(4*np.pi/7,0)
  qc.measure(0, 0)
  print(qc)
  
  sequence_rythm = np.zeros(num, dtype=int)
  
  for i in range(3):
      job = backend.run(qc, shots=num, memory=True)
      vysledky = np.array(job.result().get_memory(), dtype=int)
      sequence_rythm += vysledky
  
  return sequence_rythm
