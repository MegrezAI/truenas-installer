from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QStackedWidget, QApplication, QMessageBox, QProgressDialog)
from PyQt5.QtCore import Qt, QTimer
from concurrent.futures import ThreadPoolExecutor
import asyncio
import sys

from .pages import (
    LanguagePage, MainMenuPage, DiskSelectionPage,
    AuthPage, ProgressPage
)
from ..install import install
from ..serial import serial_sql
from ..disks import list_disks
from ..exception import InstallError
from ..i18n import I18n

class InstallerWindow(QMainWindow):
    def __init__(self, installer, loop):
        super().__init__()
        self.installer = installer
        self.i18n = I18n()
        self.loop = loop
        self.executor = ThreadPoolExecutor(max_workers=1)
        
        self.selected_disks = []
        self.wipe_disks = []
        self.set_pmbr = False
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('OceanNAS Installer')
        self.setFixedSize(800, 600)
        
        # Center window
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Create stacked widget and pages
        self.stacked_widget = QStackedWidget()
        self._create_pages()
        main_layout.addWidget(self.stacked_widget)

        # Create navigation
        nav_layout = self._create_navigation()
        main_layout.addLayout(nav_layout)

        # Setup async timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_async_tasks)
        self.timer.start(100)

        self.update_navigation_buttons()

    def _create_pages(self):
        # Initialize pages
        self.language_page = LanguagePage(self.i18n, self.installer.version)
        self.main_menu_page = MainMenuPage(self.installer, self.i18n)
        self.disk_selection_page = DiskSelectionPage(self.i18n)
        self.auth_page = AuthPage(self.i18n)
        self.progress_page = ProgressPage(self.i18n)

        # Connect signals
        self.language_page.languageChanged.connect(self.on_language_changed)
        self.main_menu_page.installationRequested.connect(self.start_installation)
        self.main_menu_page.shellRequested.connect(self.open_shell)
        self.main_menu_page.rebootRequested.connect(lambda: self.run_async(self._async_reboot()))
        self.main_menu_page.shutdownRequested.connect(lambda: self.run_async(self._async_shutdown()))
        
        self.disk_selection_page.disksSelected.connect(self.on_disks_selected)
        self.auth_page.installationRequested.connect(self.start_install)
        self.progress_page.rebootRequested.connect(lambda: self.run_async(self._async_reboot()))

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.language_page)
        self.stacked_widget.addWidget(self.main_menu_page)
        self.stacked_widget.addWidget(self.disk_selection_page)
        self.stacked_widget.addWidget(self.auth_page)
        self.stacked_widget.addWidget(self.progress_page)

    def _create_navigation(self):
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton(self.i18n.get("back"))
        self.next_btn = QPushButton(self.i18n.get("next"))
        
        self.back_btn.setFixedWidth(100)
        self.next_btn.setFixedWidth(100)
        
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        
        return nav_layout

    def update_navigation_buttons(self):
        current_index = self.stacked_widget.currentIndex()
        
        # Hide navigation on main menu and progress page
        if current_index in [1, 4]:  # main_menu_page or progress_page
            self.back_btn.hide()
            self.next_btn.hide()
            return
            
        # Hide back button on first page
        if current_index == 0:
            self.back_btn.hide()
        else:
            self.back_btn.show()
            
        self.next_btn.show()
        
        # Update back button
        self.back_btn.setEnabled(current_index > 0)
        
        # Update next button text and state
        if current_index == 3:  # auth_page
            self.next_btn.setText(self.i18n.get("install"))
        else:
            self.next_btn.setText(self.i18n.get("next"))

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.stacked_widget.setCurrentIndex(current_index - 1)
            self.update_navigation_buttons()

    def go_next(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:  # Language page
            self.stacked_widget.setCurrentWidget(self.main_menu_page)
        elif current_index == 2:  # Disk selection page
            if self.disk_selection_page.validate_selection(self.installer):
                self.stacked_widget.setCurrentWidget(self.auth_page)
        elif current_index == 3:  # Auth page
            auth_method = self.auth_page.validate_and_get_auth()
            if auth_method is not None:
                self.start_install(auth_method)
        
        self.update_navigation_buttons()

    def process_async_tasks(self):
        try:
            self.loop.run_until_complete(asyncio.sleep(0))
        except Exception as e:
            print(f"Async error: {e}")

    def run_async(self, coro):
        """Helper method to run coroutines"""
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future

    def on_language_changed(self, selected_language):
        lang_code = "en" if selected_language == "English" else "zh"
        self.i18n.set_language(lang_code)
        self.update_ui_texts()

    def update_ui_texts(self):
        # Update navigation buttons
        self.back_btn.setText(self.i18n.get("back"))
        self.next_btn.setText(self.i18n.get("next"))
        
        # Update all pages
        self.language_page.update_texts()
        self.main_menu_page.update_texts()
        self.disk_selection_page.update_texts()
        self.auth_page.update_texts()
        self.progress_page.update_texts()

    def start_installation(self):
        # 显示加载对话框
        self.loading_dialog = QProgressDialog(
            self.i18n.get("scanning_disks"),  # 使用扫描磁盘的提示文本
            None,  # 取消按钮文本（None表示不显示取消按钮）
            0,     # 最小值
            0,     # 最大值（0表示显示忙碌指示器）
            self   # 父窗口
        )
        
        self.loading_dialog.setWindowTitle(self.i18n.get("disk_selection"))
        self.loading_dialog.setWindowModality(Qt.WindowModal)
        self.loading_dialog.setAutoClose(True)
        self.loading_dialog.show()

        # 切换到磁盘选择页面并加载磁盘列表
        self.stacked_widget.setCurrentWidget(self.disk_selection_page)
        self.run_async(self.load_disk_list())
        self.update_navigation_buttons()

    async def load_disk_list(self):
        try:
            disks = await list_disks()
            await self.disk_selection_page.refresh_disk_list(disks)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            # 关闭加载对话框
            self.loading_dialog.close()

    def on_disks_selected(self, selected_disks, wipe_disks, set_pmbr):
        self.selected_disks = selected_disks
        self.wipe_disks = wipe_disks
        self.set_pmbr = set_pmbr

    def start_install(self, auth_method):
        self.stacked_widget.setCurrentWidget(self.progress_page)
        self.update_navigation_buttons()
        self.run_async(self.installation_process(auth_method))

    async def installation_process(self, auth_method):
        try:
            await install(
                self.selected_disks,
                self.wipe_disks,
                self.set_pmbr,
                auth_method,
                None,  # post_install
                await serial_sql(),
                self.progress_page.update_progress
            )
            
            self.progress_page.show_completion()
            
            QMessageBox.information(
                self, 
                self.i18n.get("install_success"),
                self.i18n.get(
                    "install_success_message",
                    vendor=self.installer.vendor,
                    disks=', '.join(d.name for d in self.selected_disks),
                    reboot_prompt=self.i18n.get('reboot_prompt')
                )
            )
            
        except InstallError as e:
            self.progress_page.show_error()
            QMessageBox.critical(self, self.i18n.get("install_error"), e.message)
            self.stacked_widget.setCurrentWidget(self.disk_selection_page)
            self.update_navigation_buttons()

    def open_shell(self):
        sys.exit(1)

    async def _async_reboot(self):
        process = await asyncio.create_subprocess_exec("reboot")
        await process.communicate()

    async def _async_shutdown(self):
        process = await asyncio.create_subprocess_exec("shutdown", "now")
        await process.communicate()

    def closeEvent(self, event):
        self.timer.stop()
        self.executor.shutdown(wait=False)
        event.accept()