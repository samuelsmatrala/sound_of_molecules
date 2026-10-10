/**
 * Vykreslí namerané výsledky (counts) z kvantového obvodu do určeného HTML elementu.
 * @param {HTMLElement} container - HTML element, kam sa má graf/výpis umiestniť
 * @param {Object} counts - Objekt s výsledkami z Qiskitu (napr. {"00": 512, "11": 512})
 */
export function renderCounts(container, counts) {
    // Vyčistíme predchádzajúci obsah
    container.innerHTML = "";

    // Nadpis
    const title = document.createElement("h4");
    title.textContent = "Výsledky kvantového merania:";
    container.appendChild(title);

    // Vytvoríme jednoduchý zoznam alebo vizualizáciu
    const list = document.createElement("ul");
    list.style.listStyleType = "none";
    list.style.padding = "0";

    // Prejdeme jednotlivé namerané stavy (napr. "0", "1" alebo "00")
    for (const [state, count] of Object.entries(counts)) {
        const item = document.createElement("li");
        item.style.margin = "5px 0";
        item.style.background = "#eef";
        item.style.padding = "5px 10px";
        item.style.borderRadius = "4px";

        // Vizuálny panel (jednoduchý stĺpec/pásik podľa počtu výskytov)
        item.textContent = `Stav |${state}⟩: ${count} krát`;
        
        list.appendChild(item);
    }

    container.appendChild(list);
}