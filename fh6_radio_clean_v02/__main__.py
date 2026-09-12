"""Desktop entry point for the independent rewrite shell."""

from __future__ import annotations

import sys

from .material_ui import MaterialWindow, QApplication


def main() -> int:
    app = QApplication.instance() or QApplication(sys.argv)
    window = MaterialWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
