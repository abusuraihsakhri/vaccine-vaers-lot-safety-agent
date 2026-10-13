/* Descriptive VAERSVAX CSV lot counting; no causal or incidence inference. */
(function (root) {
    "use strict";
    const MISSING = new Set(["", "UNKNOWN", "UNK", "NA", "N/A", "NONE", "NOT REPORTED"]);

    function parseCsv(input) {
        if (typeof input !== "string") throw new TypeError("CSV text is required");
        const text = input.replace(/^\uFEFF/, "");
        const rows = [];
        let row = [], value = "", quoted = false, endedQuote = false;
        function appendRow() {
            row.push(value);
            if (row.some(cell => cell.trim() !== "")) rows.push(row);
            row = []; value = ""; endedQuote = false;
        }
        for (let i = 0; i < text.length; i++) {
            const char = text[i];
            if (quoted) {
                if (char === '"') {
                    if (text[i + 1] === '"') { value += '"'; i++; }
                    else { quoted = false; endedQuote = true; }
                } else { value += char; }
                continue;
            }
            if (char === '"') {
                if (value !== "" || endedQuote) throw new Error("Unexpected quote in CSV");
                quoted = true;
            } else if (char === ",") {
                row.push(value); value = ""; endedQuote = false;
            } else if (char === "\n" || char === "\r") {
                appendRow();
                if (char === "\r" && text[i + 1] === "\n") i++;
            } else if (endedQuote && char !== " " && char !== "\t") {
                throw new Error("Unexpected character after a quoted CSV field");
            } else if (!endedQuote) { value += char; }
        }
        if (quoted) throw new Error("Unclosed quoted CSV field");
        if (row.length || value !== "") appendRow();
        return rows;
    }

    function analyzeCsv(input) {
        const rows = parseCsv(input);
        if (!rows.length) throw new Error("CSV is empty");
        const columns = rows.shift().map(name => name.trim().toUpperCase());
        if (new Set(columns).size !== columns.length) throw new Error("Duplicate CSV headers");
        const idIndex = columns.indexOf("VAERS_ID");
        const lotIndex = columns.indexOf("VAX_LOT");
        if (idIndex === -1 || lotIndex === -1) {
            throw new Error("Upload a VAERSVAX CSV containing VAERS_ID and VAX_LOT");
        }
        const typeIndex = columns.indexOf("VAX_TYPE");
        const manuIndex = columns.indexOf("VAX_MANU");
        const groups = new Map();
        let excluded = 0;
        for (const [index, row] of rows.entries()) {
            if (row.length !== columns.length) throw new Error("Row " + (index + 2) + " has a different number of columns");
            const reportId = row[idIndex].trim();
            const lot = row[lotIndex].trim().toUpperCase();
            if (!reportId || MISSING.has(lot)) { excluded++; continue; }
            const vaccineType = (typeIndex === -1 ? "" : row[typeIndex].trim().toUpperCase()) || "UNKNOWN";
            const manufacturer = (manuIndex === -1 ? "" : row[manuIndex].trim().toUpperCase()) || "UNKNOWN";
            const key = JSON.stringify([vaccineType, manufacturer, lot]);
            if (!groups.has(key)) groups.set(key, {vaccine_type: vaccineType, manufacturer, lot, ids: new Set()});
            groups.get(key).ids.add(reportId);
        }
        const data = Array.from(groups.values(), item => ({
            vaccine_type: item.vaccine_type,
            manufacturer: item.manufacturer,
            lot: item.lot,
            report_count: item.ids.size
        })).sort((a, b) => b.report_count - a.report_count ||
            a.vaccine_type.localeCompare(b.vaccine_type) ||
            a.manufacturer.localeCompare(b.manufacturer) || a.lot.localeCompare(b.lot));
        return {rows: data, stats: {
            input_rows: rows.length,
            excluded_rows: excluded,
            lot_groups: data.length,
            distinct_lot_report_associations: data.reduce((sum, entry) => sum + entry.report_count, 0)
        }};
    }

    function exportCsv(rows) {
        const fields = ["vaccine_type", "manufacturer", "lot", "report_count"];
        function protect(value) {
            let result = String(value);
            if (/^[\s]*[=+\-@]/.test(result) || /^[\t\r\n]/.test(result)) result = "'" + result;
            return '"' + result.replace(/"/g, '""') + '"';
        }
        return [fields.join(","), ...rows.map(row => fields.map(field => protect(row[field])).join(","))].join("\r\n") + "\r\n";
    }

    const api = Object.freeze({parseCsv, analyzeCsv, exportCsv});
    if (typeof module !== "undefined" && module.exports) module.exports = api;
    root.VAERSLot = api;
})(typeof window !== "undefined" ? window : globalThis);
