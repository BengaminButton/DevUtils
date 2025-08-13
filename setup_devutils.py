#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parent

files = {
    # Project metadata
    'pyproject.toml': '''
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "devutils"
version = "0.1.0"
description = "DevUtils: QR generator, website check, Base64 tools, duplicate finder — CLI and GUI"
authors = [{ name = "DevUtils", email = "devutils@example.com" }]
license = { text = "MIT" }
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "rich>=13",
    "typer[all]>=0.9",
    "qrcode[pil]>=7.4",
    "requests>=2.31",
    "Pillow>=10",
    "PySide6>=6.6",
]

[project.urls]
Homepage = "https://github.com/BengaminButton"

[project.scripts]
devutils = "devutils.cli:app"
devutils-gui = "devutils.gui.main:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools]
package-dir = {"" = "src"}
''',

    # README
    'README.md': '''
# DevUtils

Набор утилит: 
- Генерация QR-кодов
- Проверка доступности сайта (HTTP ping)
- Конвертер Base64/Text
- Поиск дубликатов файлов

Есть CLI и GUI (PySide6). Цветной вывод, модульная архитектура.

Запуск без установки:

```
python -m venv .venv
source .venv/bin/activate
pip install -e .
devutils --help
devutils-gui
```
''',

    # License
    'LICENSE': '''
MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''',

    # Gitignore
    '.gitignore': '''
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.build/
*.egg-info/
dist/
build/
.idea/
.vscode/
.DS_Store
''',

    # Package init
    'src/devutils/__init__.py': '''
__all__ = [
    "cli",
    "modules",
    "gui",
]
''',

    # CLI entrypoint
    'src/devutils/cli.py': '''
from pathlib import Path
import sys
import json
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from devutils.modules.qr import generate_qr, ascii_qr
from devutils.modules.ping import http_ping
from devutils.modules.base64util import b64_encode, b64_decode
from devutils.modules.duplicates import find_duplicates

app = typer.Typer(add_completion=False, no_args_is_help=True, help="DevUtils CLI")
console = Console()


@app.command()
def qr(
    text: str = typer.Option(None, "--text", "-t", help="Текст для QR"),
    input_file: Path = typer.Option(None, "--in", help="Файл с текстом"),
    output: Path = typer.Option(Path("qr.png"), "--out", "-o", help="PNG файл"),
    size: int = typer.Option(6, help="Размер модуля"),
    border: int = typer.Option(4, help="Рамка"),
    preview: bool = typer.Option(False, "--preview", help="Показать ASCII превью"),
):
    if not text and not input_file:
        raise typer.BadParameter("Укажите --text или --in")
    if input_file:
        text = input_file.read_text(encoding="utf-8")
    path = generate_qr(text, output, box_size=size, border=border)
    if preview:
        console.print(Panel.fit(ascii_qr(text), title="Preview"))
    console.print(f"[bold green]Saved:[/bold green] {path}")


@app.command()
def ping(
    url: str = typer.Argument(..., help="URL"),
    count: int = typer.Option(4, "-c", help="Количество запросов"),
    timeout: float = typer.Option(3.0, "-w", help="Таймаут, сек"),
    json_output: bool = typer.Option(False, "--json", help="Вывод JSON"),
):
    results = http_ping(url, count=count, timeout=timeout)
    if json_output:
        console.print_json(data=results)
        raise typer.Exit()

    table = Table(title="HTTP ping", box=box.SIMPLE)
    table.add_column("#")
    table.add_column("Status")
    table.add_column("Time, ms")
    for i, r in enumerate(results["samples"], 1):
        st = str(r.get("status", "-"))
        ms = f"{r.get('ms', 0):.1f}"
        color = "green" if r.get("ok") else "red"
        table.add_row(str(i), f"[{color}]{st}[/{color}]", ms)
    console.print(table)

    stats = results["stats"]
    panel = Panel.fit(
        f"sent={stats['sent']} received={stats['received']} loss={stats['loss']:.0%}\n"
        f"min={stats['min_ms']:.1f} avg={stats['avg_ms']:.1f} max={stats['max_ms']:.1f}",
        title="Summary",
    )
    console.print(panel)


@app.command("b64")
def b64(
    mode: str = typer.Argument(..., help="encode|decode"),
    input_path: Path = typer.Option(None, "--in", help="Входной файл"),
    output_path: Path = typer.Option(None, "--out", help="Выходной файл"),
    text: str = typer.Option(None, "--text", help="Текстовый ввод"),
):
    mode = mode.lower()
    if mode not in {"encode", "decode"}:
        raise typer.BadParameter("mode: encode|decode")

    data: bytes
    if input_path:
        data = input_path.read_bytes()
    elif text is not None:
        data = text.encode()
    else:
        data = sys.stdin.buffer.read()

    if mode == "encode":
        out = b64_encode(data)
    else:
        out = b64_decode(data)

    if output_path:
        output_path.write_bytes(out)
        console.print(f"[green]Saved:[/green] {output_path}")
    else:
        sys.stdout.buffer.write(out)


@app.command()
def dupes(
    path: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True),
    min_size: int = typer.Option(1, help="Мин. размер файла, байт"),
    algo: str = typer.Option("md5", help="Хеш: md5|sha1|sha256"),
    delete: bool = typer.Option(False, help="Удалить дубли кроме первого"),
):
    groups = find_duplicates(path, min_size=min_size, algo=algo)
    if not groups:
        console.print("[green]Дубликаты не найдены[/green]")
        raise typer.Exit()

    table = Table(title="Дубликаты", box=box.SIMPLE_HEAVY)
    table.add_column("Группа")
    table.add_column("Размер")
    table.add_column("Файлы")

    for i, g in enumerate(groups, 1):
        size = g[0][1]
        files = "\n".join(str(p) for p, _ in g)
        table.add_row(str(i), str(size), files)
    console.print(table)

    if delete:
        for g in groups:
            for p, _ in g[1:]:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass
        console.print("[yellow]Дубли удалены[/yellow]")


if __name__ == "__main__":
    app()
''',

    # Modules: QR
    'src/devutils/modules/qr.py': '''
from pathlib import Path
import qrcode


def generate_qr(text: str, output: Path, box_size: int = 6, border: int = 4) -> Path:
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=box_size, border=border)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    return output


def ascii_qr(text: str) -> str:
    qr = qrcode.QRCode(border=1)
    qr.add_data(text)
    qr.make(fit=True)
    m = qr.get_matrix()
    lines = []
    for row in m:
        line = ''.join('  ' if not cell else '██' for cell in row)
        lines.append(line)
    return "\n".join(lines)
''',

    # Modules: HTTP ping
    'src/devutils/modules/ping.py': '''
from __future__ import annotations
import time
import requests
from statistics import mean


def http_ping(url: str, count: int = 4, timeout: float = 3.0) -> dict:
    samples = []
    for _ in range(count):
        t0 = time.perf_counter()
        ok = False
        status = None
        try:
            r = requests.get(url, timeout=timeout)
            status = r.status_code
            ok = r.ok
        except requests.RequestException:
            ok = False
        dt = (time.perf_counter() - t0) * 1000.0
        samples.append({"ok": ok, "status": status, "ms": dt})
    received = sum(1 for s in samples if s["ok"])
    ms_values = [s["ms"] for s in samples]
    stats = {
        "sent": count,
        "received": received,
        "loss": (count - received) / count if count else 0.0,
        "min_ms": min(ms_values) if ms_values else 0.0,
        "avg_ms": mean(ms_values) if ms_values else 0.0,
        "max_ms": max(ms_values) if ms_values else 0.0,
    }
    return {"samples": samples, "stats": stats}
''',

    # Modules: Base64
    'src/devutils/modules/base64util.py': '''
import base64


def b64_encode(data: bytes) -> bytes:
    return base64.b64encode(data)


def b64_decode(data: bytes) -> bytes:
    return base64.b64decode(data)
''',

    # Modules: duplicates
    'src/devutils/modules/duplicates.py': '''
from __future__ import annotations
from pathlib import Path
from hashlib import md5, sha1, sha256
from typing import List, Tuple


CHUNK = 1024 * 1024


def _hasher(name: str):
    name = name.lower()
    if name == 'md5':
        return md5
    if name == 'sha1':
        return sha1
    if name == 'sha256':
        return sha256
    return md5


def _hash_file(p: Path, algo: str) -> str:
    h = _hasher(algo)()
    with p.open('rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def find_duplicates(root: Path, min_size: int = 1, algo: str = 'md5') -> List[List[Tuple[Path, int]]]:
    files = []
    for p in root.rglob('*'):
        if p.is_file():
            try:
                size = p.stat().st_size
            except OSError:
                continue
            if size >= min_size:
                files.append((p, size))

    by_size = {}
    for p, size in files:
        by_size.setdefault(size, []).append(p)

    groups = []
    for size, same_size in by_size.items():
        if len(same_size) < 2:
            continue
        by_hash = {}
        for p in same_size:
            try:
                h = _hash_file(p, algo)
            except OSError:
                continue
            by_hash.setdefault(h, []).append(p)
        for h, dupes in by_hash.items():
            if len(dupes) > 1:
                groups.append([(p, size) for p in dupes])
    groups.sort(key=lambda g: g[0][1], reverse=True)
    return groups
''',

    # GUI main
    'src/devutils/gui/__init__.py': '''
''',

    'src/devutils/gui/main.py': '''
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from devutils.modules.qr import generate_qr
from devutils.modules.ping import http_ping
from devutils.modules.base64util import b64_encode, b64_decode
from devutils.modules.duplicates import find_duplicates


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DevUtils')
        self.resize(900, 600)
        self._apply_dark_theme()
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(QRWidget(), 'QR')
        tabs.addTab(PingWidget(), 'Ping')
        tabs.addTab(Base64Widget(), 'Base64')
        tabs.addTab(DuplicatesWidget(), 'Duplicates')
        self.setCentralWidget(tabs)

    def _apply_dark_theme(self):
        app = QtWidgets.QApplication.instance()
        app.setStyle('Fusion')
        palette = QtGui.QPalette()
        c_bg = QtGui.QColor(30, 30, 30)
        c_panel = QtGui.QColor(45, 45, 45)
        c_text = QtGui.QColor(220, 220, 220)
        c_high = QtGui.QColor(53, 132, 228)
        palette.setColor(QtGui.QPalette.Window, c_bg)
        palette.setColor(QtGui.QPalette.WindowText, c_text)
        palette.setColor(QtGui.QPalette.Base, c_panel)
        palette.setColor(QtGui.QPalette.AlternateBase, c_bg)
        palette.setColor(QtGui.QPalette.ToolTipBase, c_text)
        palette.setColor(QtGui.QPalette.ToolTipText, c_text)
        palette.setColor(QtGui.QPalette.Text, c_text)
        palette.setColor(QtGui.QPalette.Button, c_panel)
        palette.setColor(QtGui.QPalette.ButtonText, c_text)
        palette.setColor(QtGui.QPalette.Highlight, c_high)
        palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(palette)


class QRWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.input = QtWidgets.QPlainTextEdit()
        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(1, 20)
        self.size_spin.setValue(6)
        self.border_spin = QtWidgets.QSpinBox()
        self.border_spin.setRange(1, 10)
        self.border_spin.setValue(4)
        self.preview = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.preview.setMinimumHeight(300)
        self.preview.setFrameShape(QtWidgets.QFrame.StyledPanel)

        gen_btn = QtWidgets.QPushButton('Generate')
        save_btn = QtWidgets.QPushButton('Save...')
        gen_btn.clicked.connect(self._generate)
        save_btn.clicked.connect(self._save)

        form = QtWidgets.QFormLayout()
        form.addRow('Text', self.input)
        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(QtWidgets.QLabel('Box size'))
        hb.addWidget(self.size_spin)
        hb.addSpacing(12)
        hb.addWidget(QtWidgets.QLabel('Border'))
        hb.addWidget(self.border_spin)
        hb.addStretch()
        form.addRow(hb)
        form.addRow(self.preview)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(gen_btn)
        buttons.addWidget(save_btn)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

        self._img_path = None

    def _generate(self):
        text = self.input.toPlainText()
        if not text.strip():
            QtWidgets.QMessageBox.warning(self, 'QR', 'Введите текст')
            return
        tmp = Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.TempLocation)) / 'devutils_qr.png'
        generate_qr(text, tmp, box_size=self.size_spin.value(), border=self.border_spin.value())
        self._img_path = tmp
        pix = QtGui.QPixmap(str(tmp))
        self.preview.setPixmap(pix.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._img_path and Path(self._img_path).exists():
            pix = QtGui.QPixmap(str(self._img_path))
            self.preview.setPixmap(pix.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def _save(self):
        if not self._img_path:
            self._generate()
        if not self._img_path:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save QR', 'qr.png', 'PNG (*.png)')
        if path:
            Path(path).write_bytes(Path(self._img_path).read_bytes())


class PingWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.url = QtWidgets.QLineEdit('https://example.com')
        self.count = QtWidgets.QSpinBox()
        self.count.setRange(1, 50)
        self.count.setValue(4)
        self.timeout = QtWidgets.QDoubleSpinBox()
        self.timeout.setRange(0.1, 60.0)
        self.timeout.setValue(3.0)
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['#', 'Status', 'ms'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        run_btn = QtWidgets.QPushButton('Run')
        run_btn.clicked.connect(self._run)

        form = QtWidgets.QFormLayout()
        form.addRow('URL', self.url)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel('Count'))
        row.addWidget(self.count)
        row.addSpacing(12)
        row.addWidget(QtWidgets.QLabel('Timeout'))
        row.addWidget(self.timeout)
        row.addStretch()
        form.addRow(row)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.table)
        layout.addWidget(run_btn)

    def _run(self):
        self.table.setRowCount(0)
        res = http_ping(self.url.text(), self.count.value(), self.timeout.value())
        for i, s in enumerate(res['samples'], 1):
            self.table.insertRow(self.table.rowCount())
            self.table.setItem(i-1, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.table.setItem(i-1, 1, QtWidgets.QTableWidgetItem(str(s.get('status'))))
            self.table.setItem(i-1, 2, QtWidgets.QTableWidgetItem(f"{s.get('ms',0):.1f}"))
        stats = res['stats']
        QtWidgets.QMessageBox.information(self, 'Summary', f"sent={stats['sent']} received={stats['received']} loss={stats['loss']*100:.0f}%\nmin={stats['min_ms']:.1f} avg={stats['avg_ms']:.1f} max={stats['max_ms']:.1f}")


class Base64Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.in_edit = QtWidgets.QPlainTextEdit()
        self.out_edit = QtWidgets.QPlainTextEdit()
        self.out_edit.setReadOnly(True)
        encode_btn = QtWidgets.QPushButton('Encode')
        decode_btn = QtWidgets.QPushButton('Decode')
        load_btn = QtWidgets.QPushButton('Load...')
        save_btn = QtWidgets.QPushButton('Save...')

        encode_btn.clicked.connect(self._encode)
        decode_btn.clicked.connect(self._decode)
        load_btn.clicked.connect(self._load)
        save_btn.clicked.connect(self._save)

        grid = QtWidgets.QGridLayout(self)
        grid.addWidget(QtWidgets.QLabel('Input'), 0, 0)
        grid.addWidget(QtWidgets.QLabel('Output'), 0, 1)
        grid.addWidget(self.in_edit, 1, 0)
        grid.addWidget(self.out_edit, 1, 1)
        hb = QtWidgets.QHBoxLayout()
        hb.addWidget(encode_btn)
        hb.addWidget(decode_btn)
        hb.addStretch()
        hb.addWidget(load_btn)
        hb.addWidget(save_btn)
        grid.addLayout(hb, 2, 0, 1, 2)

    def _encode(self):
        data = self.in_edit.toPlainText().encode()
        self.out_edit.setPlainText(b64_encode(data).decode())

    def _decode(self):
        try:
            data = b64_decode(self.in_edit.toPlainText().encode())
            try:
                self.out_edit.setPlainText(data.decode())
            except UnicodeDecodeError:
                self.out_edit.setPlainText(str(data))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Base64', str(e))

    def _load(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open', '', 'All (*)')
        if path:
            self.in_edit.setPlainText(Path(path).read_text(errors='ignore'))

    def _save(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save', '', 'All (*)')
        if path:
            Path(path).write_text(self.out_edit.toPlainText())


class DuplicatesWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dir_edit = QtWidgets.QLineEdit(str(Path.home()))
        browse = QtWidgets.QPushButton('Browse')
        browse.clicked.connect(self._browse)
        self.min_size = QtWidgets.QSpinBox()
        self.min_size.setRange(1, 1_000_000_000)
        self.min_size.setValue(1)
        self.algo = QtWidgets.QComboBox()
        self.algo.addItems(['md5', 'sha1', 'sha256'])
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Group', 'Size', 'File'])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        run = QtWidgets.QPushButton('Scan')
        run.clicked.connect(self._scan)

        top = QtWidgets.QHBoxLayout()
        top.addWidget(self.dir_edit)
        top.addWidget(browse)

        opts = QtWidgets.QHBoxLayout()
        opts.addWidget(QtWidgets.QLabel('Min size'))
        opts.addWidget(self.min_size)
        opts.addSpacing(12)
        opts.addWidget(QtWidgets.QLabel('Algo'))
        opts.addWidget(self.algo)
        opts.addStretch()
        opts.addWidget(run)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addLayout(opts)
        layout.addWidget(self.table)

    def _browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Directory', self.dir_edit.text())
        if path:
            self.dir_edit.setText(path)

    def _scan(self):
        self.table.setRowCount(0)
        root = Path(self.dir_edit.text())
        if not root.exists():
            QtWidgets.QMessageBox.warning(self, 'Duplicates', 'Путь не найден')
            return
        groups = find_duplicates(root, min_size=self.min_size.value(), algo=self.algo.currentText())
        row = 0
        for gi, g in enumerate(groups, 1):
            for p, size in g:
                self.table.insertRow(row)
                self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(gi)))
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(size)))
                self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(p)))
                row += 1


def main():
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
''',
}


def write_all():
    for rel, content in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    print('Scaffold complete')


if __name__ == '__main__':
    write_all()
