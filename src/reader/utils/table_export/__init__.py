import io
import csv
import xlsxwriter

# Per RFC 7111: https://www.rfc-editor.org/rfc/rfc7111
CSV_CONTENT_TYPE = "text/csv"
CSV_EXTENSION = ".csv"

XLS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
XLS_EXTENSION = ".xlsx"

def get_exporter(table_type, fieldnames):
    if table_type == 'csv':
        return CSVTableExport(fieldnames)
    elif table_type == 'xlsx' or table_type == 'xls':
        return XLSTableExport(fieldnames)

class TableExport:
    def __init__(self, fieldnames):
        self.output = io.StringIO()
        self.fieldnames = fieldnames

    def add_row(self, row_dict):
        pass

    def getvalue(self):
        return self.output.getvalue()

    def close(self):
        pass

    def content_type(self):
        pass

    def file_extension(self):
        pass

class CSVTableExport(TableExport):
    def __init__(self, fieldnames):
        super().__init__(fieldnames)
        self.resultswriter = csv.DictWriter(self.output, fieldnames=self.fieldnames)
        
        self.resultswriter.writeheader()

    def add_row(self, row_dict):
        self.resultswriter.writerow(row_dict)

    def content_type(self):
        return CSV_CONTENT_TYPE + "; charset=utf-8-sig"

    def file_extension(self):
        return CSV_EXTENSION

class XLSTableExport(TableExport):
    def __init__(self, fieldnames):
        super().__init__(fieldnames)
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.workbook.Workbook(self.output, {'in_memory': True})
        self.worksheet = self.workbook.add_worksheet()
        self.row = 0

    def add_row(self, row_dict):

        # Write out the row
        for idx, field in enumerate(self.fieldnames):
            self.worksheet.write(self.row, idx, row_dict[field])
        
        self.row += 1

    def content_type(self):
        return XLS_CONTENT_TYPE

    def file_extension(self):
        return XLS_EXTENSION

    def close(self):
        self.workbook.close()

    def getvalue(self):
        self.output.seek(0)
        return self.output.read()
