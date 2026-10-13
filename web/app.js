/* Browser-only interface: uploaded CSV data never leaves this page. */
"use strict";
(function () {
    const input = document.getElementById("file");
    const demo = document.getElementById("demo");
    const download = document.getElementById("download");
    const filter = document.getElementById("filter");
    const tbody = document.getElementById("rows");
    const info = document.getElementById("info");
    const error = document.getElementById("error");
    const table = document.getElementById("report-table");
    const formatter = new Intl.NumberFormat("en-US");
    let report = null;

    function setError(message) {
        error.textContent = message;
        error.hidden = !message;
    }

    function draw() {
        tbody.replaceChildren();
        if (!report) return;
        const needle = filter.value.trim().toUpperCase();
        const items = report.rows.filter(item =>
            [item.vaccine_type, item.manufacturer, item.lot].some(field => field.includes(needle)));
        for (const item of items.slice(0, 1000)) {
            const tr = document.createElement("tr");
            for (const field of ["vaccine_type", "manufacturer", "lot", "report_count"]) {
                const td = document.createElement("td");
                td.textContent = field === "report_count" ? formatter.format(item[field]) : item[field];
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        table.hidden = !items.length;
        document.getElementById("empty").hidden = Boolean(items.length);
        info.textContent = formatter.format(report.stats.input_rows) + " rows read · " +
            formatter.format(report.stats.excluded_rows) + " missing ID/lot rows excluded · " +
            formatter.format(report.stats.lot_groups) + " lot groups · " +
            formatter.format(report.stats.distinct_lot_report_associations) + " distinct lot-report associations" +
            (items.length > 1000 ? " · Table shows first 1,000 matches; CSV export includes all." : "");
        download.disabled = !report.rows.length;
    }

    function display(text) {
        try {
            report = window.VAERSLot.analyzeCsv(text);
            setError("");
            filter.value = "";
            draw();
        } catch (ex) {
            report = null;
            tbody.replaceChildren();
            table.hidden = true;
            download.disabled = true;
            document.getElementById("empty").hidden = false;
            info.textContent = "No dataset loaded.";
            setError(ex instanceof Error ? ex.message : "Could not parse CSV");
        }
    }

    input.addEventListener("change", async () => {
        if (!input.files.length) return;
        const file = input.files[0];
        if (file.size > 20 * 1024 * 1024) {
            display("");
            setError("CSV exceeds 20 MB browser limit. Use the Python CLI for larger files.");
            return;
        }
        try { display(await file.text()); }
        catch (_err) { display(""); setError("Unable to read the selected file."); }
    });
    demo.addEventListener("click", () => {
        display("VAERS_ID,VAX_TYPE,VAX_MANU,VAX_LOT\nS01,COVID19,Example Manufacturer,DEMO-A1\nS01,COVID19,Example Manufacturer,DEMO-A1\nS02,COVID19,Example Manufacturer,DEMO-A1\nS03,FLU,Example Manufacturer,DEMO-B2\nS04,FLU,Example Manufacturer,UNKNOWN\n");
    });
    filter.addEventListener("input", draw);
    download.addEventListener("click", () => {
        if (!report || !report.rows.length) return;
        const blob = new Blob([window.VAERSLot.exportCsv(report.rows)], {type: "text/csv;charset=utf-8"});
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url; link.download = "vaers_lot_report_counts.csv";
        document.body.appendChild(link);
        link.click(); link.remove();
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    });
})();
