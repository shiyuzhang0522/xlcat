"""End-to-end CLI tests; fixtures are temporary OOXML archives."""
import csv
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

CLI = Path(__file__).with_name("xlcat")
NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def fixture(path):
    sheet = '''<worksheet xmlns="%s"><dimension ref="A1:C4"/><sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>SNP</t></is></c><c r="B1" t="inlineStr"><is><t>P</t></is></c><c r="C1" t="inlineStr"><is><t>Note</t></is></c></row>
    <row r="2"><c r="A2" t="inlineStr"><is><t>rs123</t></is></c><c r="B2"><v>1e-12</v></c><c r="C2" t="inlineStr"><is><t>α&#10;line&#9;tab\\path</t></is></c></row>
    <row r="3"><c r="A3" t="inlineStr"><is><t>00123</t></is></c><c r="B3"><f>1+1</f><v>2</v></c><c r="C3" t="b"><v>0</v></c></row>
    <row r="4"><c r="A4" t="inlineStr"><is><t>end</t></is></c><c r="B4"><f>2+2</f><v></v></c></row>
    </sheetData></worksheet>''' % NS
    with ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''')
        z.writestr("_rels/.rels", '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''')
        z.writestr("xl/workbook.xml", '''<workbook xmlns="%s" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Per locus" sheetId="1" r:id="rId1"/><sheet name="2" sheetId="2" r:id="rId2"/></sheets></workbook>''' % NS)
        z.writestr("xl/_rels/workbook.xml.rels", '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/></Relationships>''')
        z.writestr("xl/worksheets/sheet1.xml", sheet)
        z.writestr("xl/worksheets/sheet2.xml", sheet.replace("rs123", "rs456"))


class CLITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.temp.name) / "test.xlsx"
        fixture(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def cli(self, *args, path=None):
        return subprocess.run([sys.executable, str(CLI), str(path or self.path), *args], capture_output=True, text=True, encoding="utf-8")

    def test_head_and_headers(self):
        r = self.cli("-n", "2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(r.stdout.splitlines()), 2)
        self.assertIn("α\\nline\\ttab\\\\path", r.stdout)
        self.assertEqual(self.cli("--header").stdout, "SNP\tP\tNote\n")
        self.assertEqual(self.cli("--columns").stdout, "1\tA\tSNP\n2\tB\tP\n3\tC\tNote\n")
        self.assertEqual(self.cli("-n", "0").stdout, "")
        self.assertTrue(self.cli("--header-row", "3", "-n", "1").stdout.startswith("00123\t2\tFALSE"))

    def test_sheet_selection(self):
        self.assertEqual(self.cli("--sheets").stdout, "1\tPer locus\n2\t2\n")
        self.assertIn("rs456", self.cli("-s", "2").stdout)
        self.assertEqual(self.cli("-s", "2").stdout, self.cli("--sheet-index", "2").stdout)

    def test_export_and_formulas(self):
        for option, delim in [("--tsv", "\t"), ("--csv", ",")]:
            r = self.cli(option)
            rows = list(csv.reader(io.StringIO(r.stdout), delimiter=delim))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[1][2], "α\nline\ttab\\path")
            self.assertEqual(rows[3], ["end", "", ""])
        self.assertIn("=1+1", self.cli("--formulas").stdout)
        self.assertIn("=2+2", self.cli("--formulas").stdout)
        self.assertNotIn("=", self.cli().stdout)
        self.assertEqual(self.cli("--reset-dimensions", "-n", "2").stdout, self.cli("-n", "2").stdout)

    def test_errors(self):
        for args in [("--sheet", "missing"), ("--sheet-index", "99"), ("-n", "-1"), ("--header-row", "0")]:
            r = self.cli(*args)
            self.assertNotEqual(r.returncode, 0)
            self.assertEqual(r.stdout, "")
            self.assertNotIn("Traceback", r.stderr)
        for name in ["missing.xlsx", "legacy.xls", "corrupt.xlsx"]:
            path = self.path.with_name(name)
            if name == "corrupt.xlsx":
                path.write_text("invalid")
            self.assertNotEqual(self.cli(path=path).returncode, 0)

    def test_pipe_closure(self):
        proc = subprocess.Popen([sys.executable, str(CLI), str(self.path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.stdout.close()
        stderr = proc.stderr.read()
        self.assertEqual(proc.wait(timeout=20), 0, stderr)
        self.assertEqual(stderr, b"")
        proc.stderr.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
