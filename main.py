import urllib.request
from html.parser import HTMLParser
import re
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class VGMTableParser(HTMLParser):
    """Parse HTML tables and extract rows containing VGM scores."""
    def __init__(self):
        super().__init__()
        self.tables = []
        self._in_table = False
        self._current_table = []
        self._in_row = False
        self._current_row = []
        self._in_cell = False
        self._current_cell = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self._in_table = True
            self._current_table = []
        elif self._in_table and tag == 'tr':
            self._in_row = True
            self._current_row = []
        elif self._in_row and tag in {'td', 'th'}:
            self._in_cell = True
            self._current_cell = []

    def handle_endtag(self, tag):
        if tag in {'td', 'th'} and self._in_cell:
            cell_data = ''.join(self._current_cell).strip()
            self._current_row.append(cell_data)
            self._in_cell = False
        elif tag == 'tr' and self._in_row:
            self._current_table.append(self._current_row)
            self._current_row = []
            self._in_row = False
        elif tag == 'table' and self._in_table:
            self.tables.append(self._current_table)
            self._current_table = []
            self._in_table = False

    def handle_data(self, data):
        if self._in_cell:
            self._current_cell.append(data)


def strip_tags(text: str) -> str:
    return re.sub(r'<[^>]+>', '', text)


def find_vgm_table(html: str):
    parser = VGMTableParser()
    parser.feed(html)
    for table in parser.tables:
        if not table:
            continue
        header = [h.lower() for h in table[0]]
        if {'value', 'growth', 'momentum', 'vgm'} <= set(header):
            return table
    return None


def parse_vgm_rows(table):
    rows = []
    header = [h.lower() for h in table[0]]
    for row in table[1:]:
        if len(row) < len(header):
            continue
        data = dict(zip(header, row))
        item = {
            'company': data.get('name') or data.get('company') or row[0],
            'ticker': data.get('ticker') or row[1],
            'value': data.get('value'),
            'growth': data.get('growth'),
            'momentum': data.get('momentum'),
            'vgm': data.get('vgm'),
        }
        rows.append(item)
        if len(rows) >= 5:
            break
    return rows


def fetch_top_vgm_stocks():
    url = 'https://www.zacks.com'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        messagebox.showerror('Network Error', f'Unable to fetch data: {e}')
        return []
    table = find_vgm_table(html)
    if not table:
        messagebox.showerror('Parse Error', 'Could not locate VGM table on the page.')
        return []
    return parse_vgm_rows(table)


def populate_table(tree):
    tree.delete(*tree.get_children())
    stocks = fetch_top_vgm_stocks()
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for stock in stocks:
        tree.insert('', 'end', values=(ts, stock['company'], stock['ticker'],
                                       stock['value'], stock['growth'],
                                       stock['momentum'], stock['vgm']))


def main():
    root = tk.Tk()
    root.title('Zacks VGM Stock Fetcher')

    columns = ('timestamp', 'company', 'ticker', 'value', 'growth', 'momentum', 'vgm')
    tree = ttk.Treeview(root, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=100)
    tree.pack(fill='both', expand=True)

    btn = ttk.Button(root, text='Fetch Top VGM Stocks', command=lambda: populate_table(tree))
    btn.pack(pady=5)

    root.mainloop()

if __name__ == '__main__':
    main()
