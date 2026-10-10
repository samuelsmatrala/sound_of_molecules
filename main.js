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
        
        console.log("4. Úspech! Výsledok:", result.toJs ? result.toJs() : result);
    }
} catch (err) {
    console.error("CHYBA V RUNTIME:", err);
}