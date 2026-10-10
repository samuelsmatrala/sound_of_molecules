#IMPORTS
import numpy as np
import time
from qiskit import QuantumCircuit, transpile
from qiskit.providers.jobstatus import JobStatus
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import ParityMapper
from qiskit_nature.second_q.circuit.library import HartreeFock
from qiskit.circuit.library import PauliEvolutionGate, QFT
from qiskit.synthesis import SuzukiTrotter

#FUNCTIONS
def QPE(backend, SELECTED_MOLECULE):
  result = ""
  energies = []
  # 1. MOLECULE SELECTION
  
  MOLECULE_CONFIGS = {
    "H3+":  {"atom": "H 0.0 0.0 0.0; H 0.0 0.0 0.9; H 0.0 0.0 1.7", "charge": 1, "spin": 0, "basis": "sto-3g"},
    "H2":   {"atom": "H 0.0 0.0 0.0; H 0.0 0.0 0.735", "charge": 0, "spin": 0, "basis": "sto-3g"},
    "H2+":  {"atom": "H 0.0 0.0 0.0; H 0.0 0.0 1.06",  "charge": 1, "spin": 1, "basis": "sto-3g"},
    "HeH+": {"atom": "He 0.0 0.0 0.0; H 0.0 0.0 0.772", "charge": 1, "spin": 0, "basis": "sto-3g"},
    "Li+":  {"atom": "Li 0.0 0.0 0.0",                 "charge": 1, "spin": 0, "basis": "sto-3g"},
    "H4":   {"atom": "H 0.0 0.0 0.0; H 0.0 0.0 1.0; H 0.0 0.0 2.0; H 0.0 0.0 3.0", "charge": 0, "spin": 0,"basis": "sto-3g"},}
  
  cfg = MOLECULE_CONFIGS[SELECTED_MOLECULE]
  
  #   PARAMETERS FOR EFFICIENCY AND PRECISION
  NUM_EVAL_QUBITS = 6     # 6 EVALUATION QUBITS
  TIME_STEP = 0.3         # EVOLUTION STEP PREVENTING 2PI-ALIASING
  SHOTS = 1000            # # OF SAMPLES PER SIMULATION
  
  # 2. MODEL AND MOLECULAR HAMILTONIAN PREPARATION
  
  print(f"=== STARTING QPE FOR: {SELECTED_MOLECULE} ===")
  driver = PySCFDriver(
      atom=cfg["atom"],
      basis=cfg["basis"],
      charge=cfg["charge"],
      spin=cfg["spin"]
  )
  problem = driver.run()
  
  # PARITY MAPPER WITH 2-QUBIT REDUCTION
  mapper = ParityMapper(num_particles=problem.num_particles)
  qubit_op = mapper.map(problem.hamiltonian.second_q_op())
  
  num_system_qubits = qubit_op.num_qubits
  total_qubits = num_system_qubits + NUM_EVAL_QUBITS
  nuclear_rep = problem.nuclear_repulsion_energy
  
  result+=("\n   MOLECULAR QUBITS (AFTER 2-QUBIT REDUCTION): "+str(num_system_qubits))
  result+=("\n   EVALUATION QUBITS: "+str(NUM_EVAL_QUBITS))
  result+=("\n   TOTAL # OF QUBITS: "+str(total_qubits))
  result+=("\n   REPULSION: "+str(nuclear_rep)+" HARTREE")
  
  # 3. HELPER FUNCTION FOR RUNNING QPE IN QOLLAB
  
  trotter_prep = SuzukiTrotter(order=1, reps=1)
  
  def run_qpe_for_state(state_prep_circuit, state_name):
      qc = QuantumCircuit(total_qubits, NUM_EVAL_QUBITS)
  
      # A) INITIAL STATE PREPARATION
      qc.compose(state_prep_circuit, qubits=range(num_system_qubits), inplace=True)
  
      # B) HADAMARD ON EVALUATION QUBITS
      eval_qubits = list(range(num_system_qubits, total_qubits))
      qc.h(eval_qubits)
  
      # C) CONTROLLED TIME EVOLUTIONS U^(2^k)
      for k, eval_qubit in enumerate(eval_qubits):
          power = 2**k
          evo_gate = PauliEvolutionGate(qubit_op, time=TIME_STEP * power, synthesis=trotter_prep)
          ctrl_evo = evo_gate.control(1)
          qc.append(ctrl_evo, [eval_qubit] + list(range(num_system_qubits)))
  
      # D) INVERSE QFT AND MEASUREMENT
      qft_inv = QFT(NUM_EVAL_QUBITS, inverse=True).to_gate()
      qc.append(qft_inv, eval_qubits)
      qc.measure(eval_qubits, range(NUM_EVAL_QUBITS))
  
      # E) RUNNING ON QOLLAB BACKEND
      qc_transpiled = transpile(qc, backend)
      job = backend.run(qc_transpiled, shots=SHOTS)
  
      while job.status() not in (JobStatus.DONE, JobStatus.ERROR, JobStatus.CANCELLED):
          time.sleep(1)
  
      counts = job.result().get_counts()
      most_frequent_bitstring = max(counts, key=counts.get)
  
      # CALCULATING ENERGY FROM PHASE
      decimal_phase = int(most_frequent_bitstring, 2) / (2**NUM_EVAL_QUBITS)
      if decimal_phase >= 0.5:
          decimal_phase -= 1.0
  
      energy_estimate = - (2 * np.pi * decimal_phase) / TIME_STEP
      total_energy = energy_estimate + nuclear_rep
  
      return state_name, most_frequent_bitstring, total_energy
  
  # 4. PREPARATION OF INITIAL STATES (E0, E1, E2)
  
  hf_base = HartreeFock(
      num_spatial_orbitals=problem.num_spatial_orbitals,
      num_particles=problem.num_particles,
      qubit_mapper=mapper
  )
  
  # E0: HARTREE-FOCK INITIAL STATE
  state_e0 = hf_base.copy()
  
  # E1: 1ST EXCITED STATE
  state_e1 = hf_base.copy()
  state_e1.x(0)
  
  # E2: 2ND EXCITED STATE
  state_e2 = hf_base.copy()
  if num_system_qubits > 1:
      state_e2.x(1)
  
  states_to_test = [
      (state_e0, "E_0 (Ground state)"),
      (state_e1, "E_1 (1st excited state)"),
      (state_e2, "E_2 (2nd excited state)")
  ]
  
  # 5. EXECUTION AND SUMMARY OF RESULTS
  
  result+=("\n\nStarting the QPE calculation for E0, E1, E2 on Qollab...\n")
  
  qpe_results = []
  for circuit, name in states_to_test:
      t0 = time.time()
      res = run_qpe_for_state(circuit, name)
      dt = time.time() - t0
      qpe_results.append(res)
      result+=("\n   [COMPLETED in "+str(dt)+"s] {name} -> Bitstring: "+str(res[1])+", QPE Energy: "+str(res[2])+" Hartree")
      energies.append(res[2])
  
  result+=("\n" + "="*55)
  result+=("\n"+str('Energy level')+" | "+str('Bitstring') +"| "+str('Measured E (QPE)'))
  result+=("\n"+"="*55)
  for name, bitstr, qpe_e in qpe_results:
      result+=("\n"+str(name)+" | "+str(bitstr)+" | "+str(qpe_e)+" Hartree")
  result+=("\n"+"="*55)
  return {
    "result" : result,
    "energies" : energies,
  }