from qfluentwidgets import (
    FluentWindow,
    PushButton,
    FluentIcon as FIF,
    MessageBox,
    InfoBar,
    InfoBarPosition,
    NavigationWidget,
)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
    QFrame,
)
from PyQt5.QtCore import Qt, QTimer
from concurrent.futures import ThreadPoolExecutor
import asyncio
import sys

from .pages.language_page import LanguagePage
from .pages.main_menu_page import MainMenuPage
from .pages.disk_selection_page import DiskSelectionPage
from .pages.auth_page import AuthPage
from .pages.progress_page import ProgressPage
from .pages.storage_pool_page import StoragePoolPage

from ..install import install
from ..serial import serial_sql
from ..disks import list_disks
from ..exception import InstallError
from ..i18n import I18n


class InstallerPage(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(" ", "-"))  # 设置唯一的对象名

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)


class InstallerWindow(FluentWindow):
    def __init__(self, installer, loop):
        super().__init__()

        self.installer = installer
        self.i18n = I18n()
        self.loop = loop
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.selected_disks = []
        self.wipe_disks = []
        self.set_pmbr = False

        self.initWindow()
        self.initPages()

    def initWindow(self):
        # Update window properties
        self.resize(1024, 768)
        self.setWindowTitle("OceanNAS Installer")

        # 设置最小窗口尺寸，防止窗口太小
        self.setMinimumSize(800, 600)

        # 隐藏导航栏
        self.navigationInterface.hide()

        # Center window
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

        # Setup async timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_async_tasks)
        self.timer.start(100)

    def initPages(self):
        # Initialize pages
        self.language_page = LanguagePage(self.i18n, self.installer.version)
        # 暂时注释掉主菜单页面
        # self.main_menu_page = MainMenuPage(self.installer, self.i18n)
        self.disk_selection_page = DiskSelectionPage(self.i18n)
        self.storage_pool_page = StoragePoolPage(self.i18n)
        self.auth_page = AuthPage(self.i18n)
        self.progress_page = ProgressPage(self.i18n)

        # Set object names for all pages
        self.language_page.setObjectName("language-page")
        # self.main_menu_page.setObjectName('main-menu-page')
        self.disk_selection_page.setObjectName("disk-selection-page")
        self.storage_pool_page.setObjectName("storage-pool-page")
        self.auth_page.setObjectName("auth-page")
        self.progress_page.setObjectName("progress-page")

        # Add pages to stacked widget
        self.stackedWidget.addWidget(self.language_page)
        # self.stackedWidget.addWidget(self.main_menu_page)
        self.stackedWidget.addWidget(self.disk_selection_page)
        self.stackedWidget.addWidget(self.storage_pool_page)
        self.stackedWidget.addWidget(self.auth_page)
        self.stackedWidget.addWidget(self.progress_page)

        # Connect signals
        self.language_page.languageChanged.connect(self.on_language_changed)

        # self.main_menu_page.installationRequested.connect(self.start_installation)
        # self.main_menu_page.shellRequested.connect(self.open_shell)
        # self.main_menu_page.rebootRequested.connect(lambda: self.run_async(self._async_reboot()))
        # self.main_menu_page.shutdownRequested.connect(lambda: self.run_async(self._async_shutdown()))
        self.disk_selection_page.disksSelected.connect(self.on_disks_selected)
        self.storage_pool_page.poolConfigured.connect(self.on_pool_configured)
        self.auth_page.installationRequested.connect(self.start_install)
        self.progress_page.rebootRequested.connect(
            lambda: self.run_async(self._async_reboot())
        )

        # Set initial page
        self.stackedWidget.setCurrentWidget(self.language_page)

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
        # Update all pages
        # self.language_page.update_texts()
        # self.main_menu_page.update_texts()  # 暂时注释掉
        self.disk_selection_page.update_texts()
        self.storage_pool_page.update_texts()
        self.auth_page.update_texts()
        self.progress_page.update_texts()

        page_text_mapping = {
            self.language_page.objectName(): "language",
            # self.main_menu_page.objectName(): "main_menu",
            self.disk_selection_page.objectName(): "disk_selection",
            self.storage_pool_page.objectName(): "storage_pool",
            self.auth_page.objectName(): "authentication",
            self.progress_page.objectName(): "progress",
        }

        for item in self.navigationInterface.findChildren(QWidget):
            route_key = item.property("routeKey")
            if route_key in page_text_mapping:
                item.setText(self.i18n.get(page_text_mapping[route_key]))

        # 保持当前页面选中
        current_page = self.stackedWidget.currentWidget()
        if current_page:
            self.navigationInterface.setCurrentItem(current_page.objectName())

    def start_installation(self):
        # 切换到磁盘选择页面并显示加载状态
        self.stackedWidget.setCurrentWidget(self.disk_selection_page)
        self.disk_selection_page.show_loading()
        # 加载磁盘列表
        self.run_async(self.load_disk_list())

    async def load_disk_list(self):
        try:
            disks = await list_disks()
            await self.disk_selection_page.refresh_disk_list(disks)
        except Exception as e:
            box = MessageBox(self.i18n.get("error"), str(e), self)
            box.exec()

    def on_disks_selected(self, selected_disks, wipe_disks, set_pmbr):
        self.selected_disks = selected_disks
        self.wipe_disks = wipe_disks
        self.set_pmbr = set_pmbr
        self.stackedWidget.setCurrentWidget(self.storage_pool_page)

    def on_pool_configured(self, config):
        # 如果是跳过，config 将是空字典
        if config:
            # 处理存储池配置
            self.pool_config = config

        # 无论是否配置了存储池，都继续下一步
        self.stackedWidget.setCurrentWidget(self.auth_page)

    def start_install(self, auth_method):
        self.stackedWidget.setCurrentWidget(self.progress_page)
        self.run_async(self.installation_process(auth_method))

    async def installation_process(self, auth_method):
        try:
            await install(
                self.selected_disks,
                self.wipe_disks,
                self.set_pmbr,
                auth_method,
                None,
                await serial_sql(),
                getattr(self, "pool_config", None),
                self.progress_page.update_progress,
            )

            self.progress_page.show_completion()

        except InstallError as e:
            self.progress_page.show_error()
            self.show_message(self.i18n.get("install_error"), e.message, "error")
            self.stackedWidget.setCurrentWidget(self.disk_selection_page)

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

    def show_message(self, title, message, type="info"):
        if type == "error":
            InfoBar.error(
                title=title,
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self,
            )
        else:
            InfoBar.success(
                title=title,
                content=message,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self,
            )
