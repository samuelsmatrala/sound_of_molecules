// Ak sa váš Python súbor volá napr. main.py v koreňovom priečinku:
import * as pyModule from 'pythonscripts.main';

try {
    console.log("1. Skript začíname...");
    
    if (typeof backend === 'undefined') {
        console.error("2. CHYBA: Backend nie je dostupný! Spustite projekt cez tlačidlo Run.");
    } else {
        console.log("3. Backend je OK, spúšťam main...");
        
        // Voláme funkciu cez naimportovaný modul
        const result = await pyModule.main.callPromising(backend);
        
        // Prevod výsledku z Pyodide na čistý JS objekt
        const data = result.toJs ? result.toJs() : result;
        
        console.log("4. Úspech! Výsledok:", data);

        // Ak dáta obsahujú audio signál a sampleRate, prehrejeme ich
        if (data && data.audio && data.sampleRate) {
            console.log("5. Pripravujem prehrávanie zvuku...");
            
            const audioData = data.audio;
            const sampleRate = data.sampleRate;

            // Vytvorenie Audio Contextu pre prehliadač
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            const audioCtx = new AudioContext();

            // Odomknutie kontextu pre prípad reštrikcií prehliadača
            if (audioCtx.state === 'suspended') {
                await audioCtx.resume();
            }

            // Vytvorenie bufferu a naplnenie vzorkami z Pythonu
            const buffer = audioCtx.createBuffer(1, audioData.length, sampleRate);
            const channelData = buffer.getChannelData(0);
            
            for (let i = 0; i < audioData.length; i++) {
                channelData[i] = audioData[i];
            }

            // Spustenie audio bufferu
            const source = audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(audioCtx.destination);
            source.start(0);
            
            console.log("🎵 Zvuk úspešne spustený v prehliadači!");
            console.log("QPE:<\n", data.qpe);
            console.log("Mol Fre:\n", data.moleculeFrequency);
        } else {
            console.warn("Výsledok neobsahuje audio dáta alebo sampleRate.");
        }
    }
} catch (err) {
    console.error("CHYBA V RUNTIME:", err);
}