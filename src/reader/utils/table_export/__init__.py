import io
import csv
import xlsxwriter

# Per RFC 7111: https://www.rfc-editor.org/rfc/rfc7111
CSV_CONTENT_TYPE = "text/csv"
CSV_EXTENSION = ".csv"

XLS_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
XLS_EXTENSION = ".xlsx"

def get_exporter(table_type, fieldnames, **kwargs):
    if table_type == 'csv':
        return CSVTableExport(fieldnames, **kwargs)
    elif table_type == 'xlsx' or table_type == 'xls':
        return XLSTableExport(fieldnames, **kwargs)

class TableExport:
    def __init__(self, fieldnames, **kwargs):
        self.output = io.StringIO()
        self.set_fieldnames(fieldnames)

    def set_fieldnames(self, fieldnames):
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
    def __init__(self, fieldnames, **kwargs):
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
    def __init__(self, fieldnames, title = None, **kwargs):
        super().__init__(fieldnames)
        self.output = io.BytesIO()
        self.workbook = xlsxwriter.workbook.Workbook(self.output, {'in_memory': True})
        self.worksheet = self.workbook.add_worksheet(title)
        self.row = 1

        self.writeheader()

    def writeheader(self):
        header_format = self.workbook.add_format({'bold': True})

        # Write out the header
        for idx, field in enumerate(self.fieldnames):
            self.worksheet.write(0, idx, field, header_format)

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

    def set_column_width(self, column_index, width):
        self.worksheet.set_column(column_index, column_index, width)

    def set_column_widths(self, widths):
        for idx, width in enumerate(widths):
            self.set_column_width(idx, width)

    def add_worksheet(self, title):
        self.worksheet = self.workbook.add_worksheet(title)

    def set_cell(self, row, column, value):
        self.worksheet.write(row, column, value)
