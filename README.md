# Sound of Molecules

![Sound of Molecules browser interface](images/sound_of_molecules.png "Sound of Molecules")

## Summary

Sound of Molecules is an interactive web experience that lets you select a molecular system, run quantum calculations, view estimated energies, and hear a generated melody. The interface offers H3+, H2, H2+, HeH+, Li+, and H4; Li+ is a single atomic ion rather than a molecule.

The frontend uses plain HTML and JavaScript. Python performs the calculations through a host-provided bridge, and the browser plays the returned audio using the Web Audio API.

The melody combines energy-dependent pitches with a random note sequence. It is a **sonification of calculated energies**, not a recording of molecular vibrations or a prediction of a molecule's natural sound.

## Quick Start

The project is designed to run inside Qollab using **Run with Qollab**.

1. Open the project in Qollab and use **Run with Qollab**.
2. Ensure the host has initialized a compatible quantum backend and made it available to the application as `backend`.
3. Select a molecular system in the browser interface. H3+ is selected by default.
4. Click **Run Quantum Calculation**.
5. Wait for the three QPE calculations and music sampling to finish. The page then displays an energy report and starts a nine-second melody.

### Runtime Requirements

- A Qollab host that loads `main.js`, exposes the Python module `pythonscripts.main` to JavaScript, and supports `main.callPromising(backend, molecule)`.
- A Python environment with the packages in [requirements.txt](requirements.txt). These include `qiskit>=2.5.2,<3.0.0`, Qiskit Nature, and PySCF. The source also imports NumPy directly.
- A backend supporting Qiskit transpilation, `run`, job status, and measurement counts. Music sampling additionally requires `run(..., memory=True)` and `get_memory()`.
- A browser with Web Audio support and permission to play audio.

Opening `index.html` directly or serving it with an ordinary static server is **not sufficient**: the Python bridge and backend are host-provided, and the HTML does not load `main.js` itself. There is no bundled standalone server or command-line launcher.

Exact host setup steps, tested Python versions, and a verified list of simulator or hardware backends are not yet documented. Backend compatibility should not be assumed solely because a provider supports Qiskit.

## How It Works

The selected system is sent to Python, where molecular energy estimation runs first, followed by random sequence generation and audio synthesis.

### Molecular Calculations

The calculation estimates total energies for a fixed arrangement of atoms using quantum phase estimation (QPE). It does not simulate atoms moving, optimize geometry, or calculate vibrational frequencies.

Each system has a configuration containing atomic positions, electrical charge, spin, and basis set. For example, H2 uses:

```python
{
    "atom": "H 0.0 0.0 0.0; H 0.0 0.0 0.735",
    "charge": 0,
    "spin": 0,
    "basis": "sto-3g"
}
```

PySCF performs classical electronic-structure calculations to construct an electronic Hamiltonian: the mathematical operator describing electron kinetic energy, attraction between electrons and nuclei, and repulsion between electrons.

The Hamiltonian initially uses fermionic operators. Qiskit Nature converts it into qubit operations using parity mapping:

```python
mapper = ParityMapper(num_particles=problem.num_particles)
qubit_op = mapper.map(problem.hamiltonian.second_q_op())
```

The resulting Hamiltonian is a weighted sum of Pauli operators `I`, `X`, `Y`, and `Z`. Known particle-number parities allow the mapper to remove two qubits.

QPE is run for three initial-state preparations:

| Preparation | Implementation |
| --- | --- |
| First | Hartree-Fock state, a simple approximation to the electronic ground state |
| Second | Hartree-Fock state with an `X` gate on system qubit 0 |
| Third | Hartree-Fock state with an `X` gate on system qubit 1, if that qubit exists; otherwise unchanged |

The current report labels these results as ground, first excited, and second excited states. **Those labels are not verified physical state assignments.** Flipping mapped qubits does not guarantee preparation of particular eigenstates or preservation of the intended electron number. A starting state can overlap multiple eigenstates, and the most frequent measured outcome is not necessarily the ground-state energy.

For each preparation, the code chooses the most frequent six-bit QPE outcome, decodes its phase into an electronic energy estimate, and adds nuclear repulsion to obtain a total energy in Hartree.

### Quantum Circuits

The QPE circuit in [QPE.py](pythonscripts/QPE.py) uses six evaluation qubits in addition to the mapped system qubits:

1. Prepare the selected starting state on the system qubits.
2. Apply Hadamard gates to the evaluation qubits.
3. Apply controlled Hamiltonian evolution for times `t`, `2t`, `4t`, `8t`, `16t`, and `32t`, with `t = 0.3` in atomic units.
4. Apply the inverse quantum Fourier transform.
5. Measure the evaluation qubits over 1,000 shots.

Time evolution uses a first-order, single-step product-formula approximation. The measured phase is wrapped into `[-0.5, 0.5)` and decoded with:

```text
electronic_energy = -(2 * pi * phase) / 0.3
total_energy = electronic_energy + nuclear_repulsion
```

The separate sampling circuit in [molecule_frequency.py](pythonscripts/molecule_frequency.py) prepares one qubit with `Ry(pi / 2)` and measures it. It runs three batches of 30 shots and sums their outcomes position by position, producing 30 indices from 0 to 3.

### Energy-to-Sound Mapping

[sound.py](pythonscripts/sound.py) maps each of the three total energy estimates to a frequency using a linear scale:

```text
frequency_hz = (energy_hartree + 8) / 7.995 * (329.63 - 82.41) + 82.41
```

The assumed input interval is `-8` to `-0.005` Hartree, and the target interval is `82.41` to `329.63` Hz. This is an artistic mapping into an audible range, not a physical energy-to-frequency conversion. The code does not explain the choice of these bounds or clamp values outside them.

Each random index selects a rest or one of the mapped frequencies:

| Index | Sound |
| --- | --- |
| 0 | Silence |
| 1 | Frequency mapped from the first energy estimate |
| 2 | Frequency mapped from the second energy estimate |
| 3 | Frequency mapped from the third energy estimate |

The pitches are not restricted to A, C-sharp, and E, and they are not guaranteed to be ordered from low to high or form a chord. The sequence is independently random, while the pitches depend on the energy calculations.

Each tone is synthesized as a sine wave with short fade-in and fade-out envelopes. Thirty tones or rests, each lasting 0.3 seconds, produce nine seconds of mono audio at a sample rate of 44,100 Hz. No instrument recordings are used.

## Architecture

```text
Selected system
      |
      v
PySCF -> Qiskit Nature -> QPE (three preparations)
                              |              |
                              v              v
                       Energy report    Three energies
                              |              |
                              v              v
                           Browser     Frequency mapping
                                             |
Quantum sampling -> 30 indices ------------> sound.py
                                             |
                                             v
                                      Web Audio playback
```

Quantum sampling happens after QPE completes. Both the random indices and the calculated energies are inputs to audio synthesis.

## Expected Output

A successful run displays the mapped system-qubit count, evaluation-qubit count, total qubit count, nuclear repulsion energy, and a table of three measured bitstrings and total energy estimates. The browser automatically plays the generated melody.

For a first check, select H2 using the configuration shown above. Exact energy values and note sequences are not provided as reference results here: they depend on sampling and the backend, and have not been validated against a classical reference in this repository.

## Limitations

- All systems use fixed geometries and the small `sto-3g` basis set. Results are estimates within that model, not high-accuracy molecular predictions.
- Six evaluation qubits provide finite phase resolution, while approximate time evolution and finite shots introduce additional error. Hardware noise can add further error.
- Phase wrapping can alias energies outside the decoding interval. The fixed evolution time is not an automatic guarantee against aliasing for every system.
- The three initial-state preparations are not verified ground/excited eigenstates. Some preparations may produce the same dominant result.
- No classical reference comparison or uncertainty estimate is currently reported.
- The frequency mapping extrapolates outside its assumed energy interval and can produce frequencies outside the intended range.
- QPE backend polling has no timeout. The sampling circuit is submitted without explicit transpilation, which may limit backend compatibility.
- The repository currently has no automated test suite or documented end-to-end backend validation.

## Project Structure

| Path | Role |
| --- | --- |
| `index.html` | Molecule selection, inline styling, status area, and energy-report display |
| `main.js` | Host Python bridge calls, interface updates, and Web Audio playback |
| `pythonscripts/main.py` | Coordinates energy estimation, sampling, and synthesis |
| `pythonscripts/QPE.py` | System configurations, Hamiltonian mapping, state preparation, and QPE |
| `pythonscripts/molecule_frequency.py` | Generates random indices through quantum measurements |
| `pythonscripts/sound.py` | Maps energies to frequencies and generates audio samples |
| `requirements.txt` | Declared Python dependencies |

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Python module import fails or clicking Run does nothing | Launch through Qollab, not a standalone static page. Confirm the host loads `main.js` and provides the Python bridge. |
| Backend is unavailable | Confirm the host initializes and exposes `backend` before running the calculation. |
| Calculation fails | Check the browser console and host logs for missing Python dependencies, backend capacity, or unsupported operations. Music sampling requires measurement-memory support. |
| Calculation takes a long time | Check the backend job status and queue. Three QPE jobs run sequentially; the application has no polling timeout. |
| Report appears but no sound is heard | Check device volume, site audio permissions, and the browser console for Web Audio errors. |

