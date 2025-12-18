"""主程式模組 - CMD GUI 工具的主要界面"""

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTabWidget, QTextEdit, QLabel
from .tabs.cmd_tab import CmdTab
from .tabs.sftp_tab import SftpTab
from .tabs.settings_tab import SettingsTab


class CMDTool(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CMD 控制工具 - 模組化版")
        self.resize(800, 700)

        layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        tabs = QTabWidget()

        # 初始化各個分頁
        self.sftp_tab = SftpTab(self.output)
        self.cmd_tab = CmdTab(self.output, self.sftp_tab)
        self.settings_tab = SettingsTab(self.output)

        # 加入分頁
        tabs.addTab(self.cmd_tab, "CMD 控制")
        tabs.addTab(self.sftp_tab, "SFTP 設定")
        tabs.addTab(self.settings_tab, "json自動化 設定")

        layout.addWidget(tabs)
        layout.addWidget(QLabel("輸出結果："))
        layout.addWidget(self.output)

        self.setLayout(layout)


def main():
    """主程式進入點，用於 setuptools console_scripts"""
    import sys
    app = QApplication(sys.argv)
    window = CMDTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()