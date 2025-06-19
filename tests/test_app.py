import os, sys, types, csv
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Stub unavailable modules
sys.modules["PIL"] = types.ModuleType("PIL")
sys.modules["pandas"] = types.ModuleType("pandas")
sys.modules["pandas"].read_csv = lambda *a, **k: None

sys.modules["PIL.Image"] = types.ModuleType("PIL.Image")
sys.modules["PIL.ImageTk"] = types.ModuleType("PIL.ImageTk")

import importlib.util
spec = importlib.util.spec_from_file_location("app", os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py"))
app = importlib.util.module_from_spec(spec)
with open(spec.origin) as f:
    code = f.read().replace("obj = NewsApp()", "")
exec(code, app.__dict__)
sys.modules["app"] = app


def dummy_read_csv(path, index_col=0):
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames
    if index_col == 0 and columns and columns[0] == "":
        columns = columns[1:]
        for row in rows:
            row.pop("", None)
    class DummyDF:
        def __init__(self, data, cols):
            self._data = data
            self._cols = cols
        @property
        def columns(self):
            return self._cols
        def __getitem__(self, key):
            return [r[key] for r in self._data]
    return DummyDF(rows, columns)
sys.modules["pandas"].read_csv = dummy_read_csv

def patched_show_categories(self):
    categories = []
    for cat in self.df['category']:
        c = eval(cat)[0]
        if c not in categories:
            categories.append(c)
    return categories

def setup_app(monkeypatch):
    monkeypatch.setattr(app.pd, 'read_csv', dummy_read_csv)
    monkeypatch.setattr(app.NewsApp, 'show_categories', patched_show_categories)
    obj = app.NewsApp.__new__(app.NewsApp)
    obj.load_news_items()
    return obj

def test_load_news_items_columns(monkeypatch):
    obj = setup_app(monkeypatch)
    assert {'category', 'title_en'} <= set(obj.df.columns)

def test_show_categories(monkeypatch):
    obj = setup_app(monkeypatch)
    expected = sorted({eval(row)[0] for row in obj.df['category']})
    result = obj.show_categories()
    assert sorted(result) == expected
