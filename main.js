import * as pyModule from 'pythonscripts.main';

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
        throw new Error("Backend nie je dostupný! Spustite projekt cez tlačidlo Run.");
    }

    console.log(`Spúšťam main pre molekulu: ${molecule}`);
    const result = await pyModule.main.callPromising(backend, molecule);
    const data = result.toJs ? result.toJs() : result;
    console.log("Výsledok:", data);

    if (data && data.audio && data.sampleRate) {
        playAudio(data.audio, data.sampleRate);
    } else {
        console.warn("Výsledok neobsahuje audio dáta alebo sampleRate.");
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
    statusDiv.textContent = `Počítam obvod pre ${molecule}... (môže chvíľu trvať)`;

    try {
        const data = await quantumRun(molecule);
        statusDiv.textContent = `Hotovo! Prehráva sa melódia pre ${molecule}.`;
        if (data && data.qpe) {
            out.textContent = data.qpe;
            out.style.display = "block";
        }
    } catch (err) {
        console.error(err);
        statusDiv.textContent = "Chyba pri výpočte: " + err;
    } finally {
        btn.disabled = false;
    }
}

function init() {
    const btn = document.getElementById('runBtn');
    if (btn) btn.addEventListener('click', onRunClick);
}

window.quantumRun = quantumRun;

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
