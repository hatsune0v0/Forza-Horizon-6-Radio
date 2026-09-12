"""Small PySide6 Material-like shell for the independent rewrite."""

from __future__ import annotations

from typing import Callable

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - exercised on machines without Qt
    QApplication = None
    QMainWindow = object
    QWidget = object
    QHBoxLayout = QLabel = QListWidget = QListWidgetItem = QPushButton = QStackedWidget = None


class MaterialWindow(QMainWindow):
    def __init__(self, *, on_toggle: Callable[[], None] | None = None, on_sync: Callable[[], None] | None = None):
        if QApplication is None:
            raise RuntimeError("PySide6 is unavailable")
        super().__init__()
        self.setWindowTitle("FH6 Radio")
        self.resize(900, 620)
        self._on_toggle = on_toggle or (lambda: None)
        self._on_sync = on_sync or (lambda: None)
        root = QWidget(self)
        layout = QHBoxLayout(root)
        self.navigation = QListWidget()
        self.navigation.setFixedWidth(150)
        self.navigation.setAccessibleName("Main navigation")
        self.pages = QStackedWidget()
        for name in ("首页", "音量", "输入", "提示", "主题", "日志"):
            self.navigation.addItem(QListWidgetItem(name))
            page = QWidget()
            page_layout = QVBoxLayout(page)
            title = QLabel(name)
            title.setObjectName("PageTitle")
            page_layout.addWidget(title)
            if name == "首页":
                self.status = QLabel("等待遥测")
                self.status.setObjectName("Status")
                page_layout.addWidget(self.status)
                controls = QHBoxLayout()
                start = QPushButton("启动")
                start.clicked.connect(self._on_toggle)
                sync = QPushButton("强制同步")
                sync.clicked.connect(self._on_sync)
                controls.addWidget(start)
                controls.addWidget(sync)
                page_layout.addLayout(controls)
            else:
                page_layout.addWidget(QLabel("此页面由独立运行时提供数据"))
            page_layout.addStretch(1)
            self.pages.addWidget(page)
        layout.addWidget(self.navigation)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.navigation.setCurrentRow(0)
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #202124; color: #f4f4f4; }
            QListWidget { background: #292a2d; border: 0; border-radius: 22px; padding: 8px; }
            QListWidget::item { padding: 12px; border-radius: 16px; }
            QListWidget::item:selected { background: #4d4f55; }
            QLabel#PageTitle { font: 700 24px 'Segoe UI'; }
            QLabel#Status { background: #303136; border-radius: 22px; padding: 24px; font-size: 18px; }
            QPushButton { background: #3a3b40; border: 1px solid #777980; border-radius: 18px; padding: 10px 18px; }
            QPushButton:hover { background: #4d4f55; }
            QPushButton:pressed { background: #5e6068; }
        """)

    def set_status(self, text: str) -> None:
        self.status.setText(text)
