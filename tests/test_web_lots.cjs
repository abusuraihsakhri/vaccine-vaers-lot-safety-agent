const test = require("node:test");
const assert = require("node:assert/strict");
const lot = require("../web/lot_analysis.js");

test("CSV parser handles BOM, quoted commas, newlines and escaped quotes", () => {
    const rows = lot.parseCsv('\uFEFFVAERS_ID,VAX_LOT\r\n1,"A,1"\r\n2,"B\n""2"""\r\n');
    assert.deepEqual(rows, [["VAERS_ID", "VAX_LOT"], ["1", "A,1"], ["2", 'B\n"2"']]);
});
test("deduplicates repeated report-lot rows, not different lots", () => {
    const csv = "VAERS_ID,VAX_LOT,VAX_TYPE,VAX_MANU\n1,X,FLU,A\n1,X,FLU,A\n2,X,FLU,A\n1,X,COVID19,A\n3,UNKNOWN,FLU,A\n";
    const result = lot.analyzeCsv(csv);
    assert.equal(result.stats.input_rows, 5);
    assert.equal(result.stats.excluded_rows, 1);
    assert.equal(result.stats.distinct_lot_report_associations, 3);
    assert.deepEqual(result.rows.map(x => x.report_count), [2,1]);
});
test("rejects malformed CSV and duplicates", () => {
    assert.throws(() => lot.analyzeCsv("VAERS_ID,OTHER\n1,x"), /VAERS_ID and VAX_LOT/);
    assert.throws(() => lot.analyzeCsv("VAERS_ID,VAX_LOT\n1,\"oops"), /Unclosed/);
    assert.throws(() => lot.analyzeCsv("VAERS_ID,VAX_LOT\n1,X,Y"), /different number/);
    assert.throws(() => lot.analyzeCsv("VAERS_ID,VAX_LOT,VAX_LOT\n1,X,X"), /Duplicate/);
});
test("formula-like spreadsheet data is neutralized on export", () => {
    const rows = [{vaccine_type: "FLU", manufacturer: "+attack", lot: "=1+1", report_count: 2}];
    const out = lot.exportCsv(rows);
    assert.match(out, /"'=1\+1"/);
    assert.match(out, /"'\+attack"/);
});
