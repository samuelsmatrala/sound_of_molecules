import * as pyModule from 'pythonscripts.main';
import { MOLECULE_INFO } from './molecule_info.js';

let audioCtx = null;

function playAudio(audioData, sampleRate) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!audioCtx) audioCtx = new AudioContext();
    if (audioCtx.state === 'suspended') audioCtx.resume();

    const buffer = audioCtx.createBuffer(1, audioData.length, sampleRate);
    const channelData = buffer.getChannelData(0);
    for (let i = 0; i < audioData.length; i++) {
        channelData[i] = audioData[i];
    }

    const source = audioCtx.createBufferSource();
    source.buffer = buffer;
    source.connect(audioCtx.destination);
    source.start(0);
}

async function quantumRun(molecule) {
    if (typeof backend === 'undefined') {
        throw new Error("Backend is not available! Please run the project using the Run button.");
    }

    console.log(`Running main for molecule: ${molecule}`);
    const result = await pyModule.main.callPromising(backend, molecule);
    const data = result.toJs ? result.toJs() : result;
    console.log("Result:", data);

    if (data && data.audio && data.sampleRate) {
        playAudio(data.audio, data.sampleRate);
    } else {
        console.warn("Result does not contain audio data or sampleRate.");
    }
    return data;
}

async function onRunClick() {
    const statusDiv = document.getElementById('status');
    const btn = document.getElementById('runBtn');
    const out = document.getElementById('qpeOutput');
    const checked = document.querySelector('input[name="molecule"]:checked');
    const molecule = checked ? checked.value : "H3+";

    btn.disabled = true;
    out.style.display = "none";
    statusDiv.textContent = `Computing circuit for ${molecule}... (this may take a moment)`;

    try {
        const data = await quantumRun(molecule);
        statusDiv.textContent = `Done! Playing melody for ${molecule}.`;
        if (data && data.qpe) {
            out.textContent = data.qpe;
            out.style.display = "block";
        }
    } catch (err) {
        console.error(err);
        statusDiv.textContent = "Error during calculation: " + err;
    } finally {
        btn.disabled = false;
    }
}

function onMoleculeChange(input) {
    const molecule = input.value;
    const moleculeInfo = MOLECULE_INFO[molecule];
    dispalyMoleculeInfo(moleculeInfo);
}

function dispalyMoleculeInfo(molecule) {
    const infoDiv = document.querySelector('.molecule-info');
    infoDiv.innerHTML = `
    <h3>${molecule.name}</h3>
    <p><b>Description:</b> ${molecule.description}</p>
    <p><b>Occurrence:</b> ${molecule.occurrence}</p>
    <p><b>Uses:</b> ${molecule.uses}</p>
    `;
}

function init() {
    const btn = document.getElementById('runBtn');
    if (btn) btn.addEventListener('click', onRunClick);
    const moleculeDiv = document.querySelectorAll('input[name="molecule"]');
    if (moleculeDiv) moleculeDiv.forEach(input => input.addEventListener('input', () => {
        onMoleculeChange(input);
    }));
}

window.quantumRun = quantumRun;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
