from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from devutils.modules.qr import generate_qr
from devutils.modules.ping import http_ping
from devutils.modules.base64util import b64_encode, b64_decode
from devutils.modules.duplicates import find_duplicates


class Header(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        title = QtWidgets.QLabel("DevUtils")
        subtitle = QtWidgets.QLabel("Набор утилит: QR-коды • Пинг • Base64 • Дубликаты")
        author = QtWidgets.QLabel('<a style="color:#ffffff; text-decoration:none; font-weight:600;" href="https://github.com/BengaminButton">⭐ Автор: BengaminButton</a>')
        author.setObjectName("authorLink")
        author.setOpenExternalLinks(True)
        author.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        title_font = QtGui.QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 160))
        title.setGraphicsEffect(shadow)

        subtitle_font = QtGui.QFont()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)

        author_font = QtGui.QFont()
        author_font.setPointSize(13)
        author_font.setBold(True)
        author.setFont(author_font)

        title.setStyleSheet("color: #E8EAED;")
        subtitle.setStyleSheet("color: #B0B3B8;")
        author.setStyleSheet("")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(4)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(author)

        self.setAutoFillBackground(True)
        p = self.palette()
        grad = QtGui.QLinearGradient(0, 0, 0, 1)
        grad.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
        grad.setColorAt(0.0, QtGui.QColor(32, 33, 36))
        grad.setColorAt(1.0, QtGui.QColor(24, 25, 28))
        brush = QtGui.QBrush(grad)
        p.setBrush(QtGui.QPalette.Window, brush)
        self.setPalette(p)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DevUtils — Набор утилит')
        self.resize(1100, 720)
        self.setMinimumSize(980, 640)
        self._apply_theme()

        central = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(central)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        header = Header()
        v.addWidget(header)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(QRWidget(), 'QR‑код')
        tabs.addTab(PingWidget(), 'Пинг')
        tabs.addTab(Base64Widget(), 'Base64')
        tabs.addTab(DuplicatesWidget(), 'Дубликаты')
        v.addWidget(tabs)

        self.setCentralWidget(central)
        self.statusBar().showMessage('Готово')

    def _apply_theme(self):
        app = QtWidgets.QApplication.instance()
        app.setStyle('Fusion')

        base_font = QtGui.QFont()
        base_font.setPointSize(12)
        app.setFont(base_font)

        palette = QtGui.QPalette()
        c_bg = QtGui.QColor(32, 33, 36)
        c_panel = QtGui.QColor(40, 42, 46)
        c_text = QtGui.QColor(232, 234, 237)
        c_hint = QtGui.QColor(176, 179, 184)
        c_high = QtGui.QColor(53, 132, 228)
        palette.setColor(QtGui.QPalette.Window, c_bg)
        palette.setColor(QtGui.QPalette.WindowText, c_text)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(28, 29, 31))
        palette.setColor(QtGui.QPalette.AlternateBase, c_panel)
        palette.setColor(QtGui.QPalette.ToolTipBase, c_text)
        palette.setColor(QtGui.QPalette.ToolTipText, c_text)
        palette.setColor(QtGui.QPalette.Text, c_text)
        palette.setColor(QtGui.QPalette.Button, c_panel)
        palette.setColor(QtGui.QPalette.ButtonText, c_text)
        palette.setColor(QtGui.QPalette.BrightText, QtGui.QColor(255, 255, 255))
        palette.setColor(QtGui.QPalette.Highlight, c_high)
        palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(255, 255, 255))
        app.setPalette(palette)

        style = """
        QWidget { color: #E8EAED; }
        QTabWidget::pane { border: 0; }
        QTabBar::tab {
            background: #2b2d31;
            color: #E8EAED;
            padding: 10px 18px;
            margin-right: 6px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }
        QTabBar::tab:selected { background: #39424e; }
        QTabBar::tab:hover { background: #33373d; }

        #authorLink { background: #0B57D0; border-radius: 14px; padding: 6px 12px; }
        #authorLink:hover { background: #0F66FF; }

        QGroupBox {
            border: 1px solid #3a3d41; border-radius: 10px; margin-top: 16px; padding: 12px; font-weight: 500;
        }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #B0B3B8; }

        QLabel[hint="true"] { color: #B0B3B8; }

        QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: #202226;
            border: 1px solid #3a3d41;
            border-radius: 8px;
            padding: 8px 10px;
            selection-background-color: #3566e4;
            selection-color: white;
        }
        QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #4c89ff;
        }

        QPushButton { background: #2f3136; border: 1px solid #3a3d41; border-radius: 10px; padding: 10px 16px; }
        QPushButton:hover { background: #36393f; }
        QPushButton:pressed { background: #2a2d31; }
        QPushButton[primary="true"] { background: #3566e4; border: 1px solid #3566e4; color: white; }
        QPushButton[primary="true"]:hover { background: #3e74ff; }

        QTableWidget {
            background: #202226; gridline-color: #3a3d41; border: 1px solid #3a3d41; border-radius: 8px;
        }
        QHeaderView::section { background: #2b2d31; color: #E8EAED; padding: 10px; border: 0; }
        QTableWidget::item { padding: 8px; }
        """
        app.setStyleSheet(style)


class QRWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.input = QtWidgets.QPlainTextEdit()
        self.input.setPlaceholderText('Введите текст для QR‑кода')
        self.input.setMinimumHeight(140)

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(1, 20)
        self.size_spin.setValue(8)
        self.size_spin.setMinimumHeight(36)

        self.border_spin = QtWidgets.QSpinBox()
        self.border_spin.setRange(1, 10)
        self.border_spin.setValue(4)
        self.border_spin.setMinimumHeight(36)

        self.preview = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.preview.setMinimumHeight(360)
        self.preview.setFrameShape(QtWidgets.QFrame.StyledPanel)

        gen_btn = QtWidgets.QPushButton('Сгенерировать')
        gen_btn.setProperty('primary', True)
        save_btn = QtWidgets.QPushButton('Сохранить…')
        gen_btn.setMinimumHeight(40)
        save_btn.setMinimumHeight(40)
        gen_btn.clicked.connect(self._generate)
        save_btn.clicked.connect(self._save)

        form = QtWidgets.QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        form.addWidget(QtWidgets.QLabel('Текст'), 0, 0)
        form.addWidget(self.input, 1, 0, 1, 4)

        form.addWidget(QtWidgets.QLabel('Размер модуля'), 2, 0)
        form.addWidget(self.size_spin, 2, 1)
        form.addWidget(QtWidgets.QLabel('Рамка'), 2, 2)
        form.addWidget(self.border_spin, 2, 3)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.preview)
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(gen_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        self._img_path = None

    def _generate(self):
        text = self.input.toPlainText()
        if not text.strip():
            QtWidgets.QMessageBox.warning(self, 'QR‑код', 'Введите текст')
            return
        tmp = Path(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.TempLocation)) / 'devutils_qr.png'
        generate_qr(text, tmp, box_size=self.size_spin.value(), border=self.border_spin.value())
        self._img_path = tmp
        pix = QtGui.QPixmap(str(tmp))
        self._update_preview(pix)

    def _update_preview(self, pix: QtGui.QPixmap):
        self.preview.setPixmap(pix.scaled(self.preview.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._img_path and Path(self._img_path).exists():
            pix = QtGui.QPixmap(str(self._img_path))
            self._update_preview(pix)

    def _save(self):
        if not self._img_path:
            self._generate()
        if not self._img_path:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить QR‑код', 'qr.png', 'PNG (*.png)')
        if path:
            Path(path).write_bytes(Path(self._img_path).read_bytes())
            QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('QR‑код сохранён', 3000)


class PingWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.url = QtWidgets.QLineEdit('https://example.com')
        self.url.setMinimumHeight(36)
        self.count = QtWidgets.QSpinBox()
        self.count.setRange(1, 100)
        self.count.setValue(4)
        self.count.setMinimumHeight(36)
        self.timeout = QtWidgets.QDoubleSpinBox()
        self.timeout.setRange(0.1, 60.0)
        self.timeout.setValue(3.0)
        self.timeout.setSingleStep(0.1)
        self.timeout.setMinimumHeight(36)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['#', 'Статус', 'мс'])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setMinimumHeight(280)

        self.summary = QtWidgets.QLabel()
        self.summary.setProperty('hint', True)

        run_btn = QtWidgets.QPushButton('Запустить')
        run_btn.setProperty('primary', True)
        run_btn.setMinimumHeight(40)
        run_btn.clicked.connect(self._run)

        form = QtWidgets.QGridLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)
        form.addWidget(QtWidgets.QLabel('URL'), 0, 0)
        form.addWidget(self.url, 0, 1, 1, 3)
        form.addWidget(QtWidgets.QLabel('Запросов'), 1, 0)
        form.addWidget(self.count, 1, 1)
        form.addWidget(QtWidgets.QLabel('Таймаут, сек'), 1, 2)
        form.addWidget(self.timeout, 1, 3)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.table)

        bottom = QtWidgets.QHBoxLayout()
        bottom.addWidget(self.summary)
        bottom.addStretch()
        bottom.addWidget(run_btn)
        layout.addLayout(bottom)

    def _run(self):
        self.table.setRowCount(0)
        self.summary.setText('')
        res = http_ping(self.url.text(), self.count.value(), self.timeout.value())
        for i, s in enumerate(res['samples'], 1):
            self.table.insertRow(self.table.rowCount())
            self.table.setItem(i-1, 0, QtWidgets.QTableWidgetItem(str(i)))
            self.table.setItem(i-1, 1, QtWidgets.QTableWidgetItem(str(s.get('status'))))
            self.table.setItem(i-1, 2, QtWidgets.QTableWidgetItem(f"{s.get('ms',0):.1f}"))
        stats = res['stats']
        self.summary.setText(f"Отправлено: {stats['sent']} • Получено: {stats['received']} • Потери: {stats['loss']*100:.0f}% | "
                             f"min: {stats['min_ms']:.1f} ms • avg: {stats['avg_ms']:.1f} ms • max: {stats['max_ms']:.1f} ms")
        QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Пинг выполнен', 3000)


class Base64Widget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.in_edit = QtWidgets.QPlainTextEdit()
        self.in_edit.setPlaceholderText('Ввод')
        self.in_edit.setMinimumHeight(260)
        self.out_edit = QtWidgets.QPlainTextEdit()
        self.out_edit.setPlaceholderText('Вывод')
        self.out_edit.setReadOnly(True)
        self.out_edit.setMinimumHeight(260)

        encode_btn = QtWidgets.QPushButton('Кодировать')
        decode_btn = QtWidgets.QPushButton('Декодировать')
        load_btn = QtWidgets.QPushButton('Открыть…')
        save_btn = QtWidgets.QPushButton('Сохранить…')
        encode_btn.setProperty('primary', True)
        for b in (encode_btn, decode_btn, load_btn, save_btn):
            b.setMinimumHeight(40)

        encode_btn.clicked.connect(self._encode)
        decode_btn.clicked.connect(self._decode)
        load_btn.clicked.connect(self._load)
        save_btn.clicked.connect(self._save)

        grid = QtWidgets.QGridLayout(self)
        grid.setContentsMargins(18, 18, 18, 18)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)
        grid.addWidget(QtWidgets.QLabel('Ввод'), 0, 0)
        grid.addWidget(QtWidgets.QLabel('Вывод'), 0, 1)
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
        QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Текст закодирован', 3000)

    def _decode(self):
        try:
            data = b64_decode(self.in_edit.toPlainText().encode())
            try:
                self.out_edit.setPlainText(data.decode())
            except UnicodeDecodeError:
                self.out_edit.setPlainText(str(data))
            QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Текст декодирован', 3000)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Base64', f'Ошибка: {e}')

    def _load(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Открыть', '', 'Все файлы (*)')
        if path:
            self.in_edit.setPlainText(Path(path).read_text(errors='ignore'))
            QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Файл загружен', 3000)

    def _save(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить', '', 'Все файлы (*)')
        if path:
            Path(path).write_text(self.out_edit.toPlainText())
            QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Файл сохранён', 3000)


class DuplicatesWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.dir_edit = QtWidgets.QLineEdit(str(Path.home()))
        self.dir_edit.setMinimumHeight(36)
        browse = QtWidgets.QPushButton('Обзор')
        browse.setMinimumHeight(40)
        browse.clicked.connect(self._browse)
        self.min_size = QtWidgets.QSpinBox()
        self.min_size.setRange(1, 1_000_000_000)
        self.min_size.setValue(1)
        self.min_size.setMinimumHeight(36)
        self.algo = QtWidgets.QComboBox()
        self.algo.addItems(['md5', 'sha1', 'sha256'])
        self.algo.setMinimumHeight(36)

        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(['Группа', 'Размер', 'Файл'])
        self.table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table.setMinimumHeight(320)

        run = QtWidgets.QPushButton('Сканировать')
        run.setProperty('primary', True)
        run.setMinimumHeight(40)
        run.clicked.connect(self._scan)

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(12)
        top.addWidget(self.dir_edit)
        top.addWidget(browse)

        opts = QtWidgets.QHBoxLayout()
        opts.setSpacing(12)
        opts.addWidget(QtWidgets.QLabel('Мин. размер'))
        opts.addWidget(self.min_size)
        opts.addWidget(QtWidgets.QLabel('Алгоритм'))
        opts.addWidget(self.algo)
        opts.addStretch()
        opts.addWidget(run)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        layout.addLayout(top)
        layout.addLayout(opts)
        layout.addWidget(self.table)

    def _browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Выбрать папку', self.dir_edit.text())
        if path:
            self.dir_edit.setText(path)

    def _scan(self):
        self.table.setRowCount(0)
        root = Path(self.dir_edit.text())
        if not root.exists():
            QtWidgets.QMessageBox.warning(self, 'Дубликаты', 'Путь не найден')
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
        QtWidgets.QApplication.instance().activeWindow().statusBar().showMessage('Поиск завершён', 3000)


def main():
    app = QtWidgets.QApplication([])
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == '__main__':
    main()
