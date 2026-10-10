# NOTE: 'backend' is pre-created as a global variable

from qiskit import QuantumCircuit

# Create a basic Bell State
circuit = QuantumCircuit(2, 2) # 2 qubits, 2 bits
circuit.h(0)
circuit.cx(0, 1)

# Measure qubits 0 and 1 into bits 0 and 1 respectively
circuit.measure([0, 1], [0, 1])
# NOTE: circuit.measure_all() or circuit.measure_active() would do the same here

# Display circuit, same as print(circuit.draw(output="text"))
print(circuit)
# NOTE: you can use circuit.draw(output="mpl", filename="circuit.png") to get the Qiskit circuit
#       rendering in the console + download it as PNG file (SVG would be the default) - make sure
#       to select "Visualization" checkbox above

from qiskit.providers.jobstatus import JobStatus
import time

def main(shots: int = 100, excludeLowProbabilityValues: bool = True, lowProbabilityThreshold: float = 0.05):
  # Submit the job for execution
  job = backend.run(circuit, shots=shots)

  # Poll for status till the job is done
  while True:
    status = job.status()
    print(f"Job status is {status}")
    match status:
      case JobStatus.DONE:
        break
      case JobStatus.ERROR:
        raise Exception(job.result())
    time.sleep(10)

  # Get values to probabilities map
  counts = job.result().get_counts()
  if excludeLowProbabilityValues:
    shotsThreshold = shots * lowProbabilityThreshold
    # Filter noise
    counts = {bits: cnt for bits, cnt in counts.items() if cnt > shotsThreshold}

  print(f"Counts for {shots} shots: {counts}")
