from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QComboBox, QLabel, QStackedWidget,
                           QCheckBox, QMessageBox, QLineEdit, QGridLayout,
                           QScrollArea, QFrame, 
                           QHeaderView, QProgressBar, QHBoxLayout,
                           QProgressDialog, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
import humanfriendly
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor

from .disks import list_disks
from .install import install
from .serial import serial_sql
from .i18n import I18n
from .exception import InstallError



class InstallerWindow(QMainWindow):
    def __init__(self, installer, loop):
        super().__init__()
        self.installer = installer
        self.i18n = I18n()
        self.selected_disks = []
        self.loop = loop
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OceanNAS Installer')
        self.setFixedSize(800, 600)
        
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

        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Create navigation buttons
        nav_layout = QHBoxLayout()
        self.back_btn = QPushButton(self.i18n.get("back"))
        self.next_btn = QPushButton(self.i18n.get("next"))
        self.back_btn.setFixedWidth(100)
        self.next_btn.setFixedWidth(100)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)

        # Connect navigation buttons
        self.back_btn.clicked.connect(self.go_back)
        self.next_btn.clicked.connect(self.go_next)

        # Create pages
        self.language_page = self.create_language_page()
        self.main_menu_page = self.create_main_menu_page()
        self.disk_selection_page = self.create_disk_selection_page()
        self.auth_page = self.create_auth_page()
        self.progress_page = self.create_progress_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.language_page)
        self.stacked_widget.addWidget(self.main_menu_page)
        self.stacked_widget.addWidget(self.disk_selection_page)
        self.stacked_widget.addWidget(self.auth_page)
        self.stacked_widget.addWidget(self.progress_page)

        # Create timer for async operations
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_async_tasks)
        self.timer.start(100)

        # Update navigation buttons
        self.update_navigation_buttons()

    def update_navigation_buttons(self):
        current_index = self.stacked_widget.currentIndex()
        
        # Hide navigation on main menu and progress page
        if current_index in [1, 4]:  # main_menu_page or progress_page
            self.back_btn.hide()
            self.next_btn.hide()
            return
            
        # Hide back button on first page (language selection)
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
            self.on_language_selected()
        elif current_index == 2:  # Disk selection page
            self.on_disks_selected()
        elif current_index == 3:  # Auth page
            self.start_install()
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

    def create_language_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)

        # Welcome title
        welcome_title = QLabel(self.i18n.get("welcome_title"))
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2980b9;
        """)
        layout.addWidget(welcome_title)

        # Welcome message
        welcome_msg = QLabel(self.i18n.get("welcome_message"))
        welcome_msg.setAlignment(Qt.AlignCenter)
        welcome_msg.setWordWrap(True)
        welcome_msg.setStyleSheet("""
            font-size: 16px;
            color: #666;
            margin-bottom: 20px;
        """)
        layout.addWidget(welcome_msg)

        # Language selection container
        lang_container = QFrame()
        
        lang_layout = QVBoxLayout(lang_container)
        lang_layout.setSpacing(15)

        # Language selection title
        lang_title = QLabel(self.i18n.get("language_selection"))
        lang_title.setAlignment(Qt.AlignCenter)
        lang_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333;
        """)
        lang_layout.addWidget(lang_title)

        # Language combobox
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.setFixedWidth(200)
    
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        combo_container = QWidget()
        combo_layout = QHBoxLayout()
        combo_layout.addStretch()
        combo_layout.addWidget(self.language_combo)
        combo_layout.addStretch()
        combo_container.setLayout(combo_layout)
        
        lang_layout.addWidget(combo_container)
        layout.addWidget(lang_container)
        
        # Add stretches for vertical centering
        layout.addStretch()
        
        # Version info at bottom
        version_label = QLabel(f"Version {self.installer.version}")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #999; font-size: 12px;")
        layout.addWidget(version_label)

        page.setLayout(layout)
        return page

    def on_language_changed(self, selected_language):
        lang_code = "en" if selected_language == "English" else "zh"
        self.i18n = I18n(lang_code)
        self.update_ui_texts()

    def on_language_selected(self):
        self.stacked_widget.setCurrentWidget(self.main_menu_page)
        self.update_navigation_buttons()

    def update_ui_texts(self):
        # Update navigation buttons
        self.back_btn.setText(self.i18n.get("back"))
        self.next_btn.setText(self.i18n.get("next"))
        
        # Update welcome page texts
        welcome_labels = self.language_page.findChildren(QLabel)
        for label in welcome_labels:
            if "font-size: 32px" in label.styleSheet():  # Welcome title
                label.setText(self.i18n.get("welcome_title"))
            elif "font-size: 16px" in label.styleSheet():  # Welcome message
                label.setText(self.i18n.get("welcome_message"))
            elif "font-size: 18px" in label.styleSheet():  # Language selection label
                label.setText(self.i18n.get("language_selection"))
            elif label.text().startswith("Version"):  # Version label
                continue  # Skip version label
        
       
        
        # Update main menu buttons
        main_menu_buttons = self.main_menu_page.findChildren(QPushButton)
        button_texts = [
            self.i18n.get("install_upgrade"),
            self.i18n.get("shell"),
            self.i18n.get("reboot"),
            self.i18n.get("shutdown")
        ]
        for btn, text in zip(main_menu_buttons, button_texts):
            btn.setText(text)
            
        # Update disk selection page
        self.disk_selection_page.findChild(QLabel).setText(self.i18n.get("disk_selection"))
        
        # Update auth page
        auth_page_labels = self.auth_page.findChildren(QLabel)
        auth_page_labels[0].setText(self.i18n.get("authentication"))
        auth_page_labels[1].setText(self.i18n.get("web_ui_auth"))
        
        # Update auth combo box
        self.auth_combo.clear()
        self.auth_combo.addItems([
            self.i18n.get("admin_user"),
            self.i18n.get("configure_webui")
        ])
        
        # Update password labels
        pass_labels = self.password_widget.findChildren(QLabel)
        pass_labels[0].setText(self.i18n.get("password"))
        pass_labels[1].setText(self.i18n.get("confirm_password"))
        
        # Update progress page
        progress_labels = self.progress_page.findChildren(QLabel)
        progress_labels[0].setText(self.i18n.get("installation_progress"))
        self.progress_label.setText(self.i18n.get("please_wait"))

        # Update disk table headers
        if hasattr(self, 'disk_table'):
            self.disk_table.setHorizontalHeaderLabels([
                "",  # Checkbox column
                self.i18n.get("disk_name"),
                self.i18n.get("type"),
                self.i18n.get("model"),
                self.i18n.get("size")
            ])

    def create_main_menu_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel(f"{self.installer.vendor} {self.installer.version}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Buttons container
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)

        buttons = [
            (self.i18n.get("install_upgrade"), self.start_installation),
            (self.i18n.get("shell"), self.open_shell),
            (self.i18n.get("reboot"), lambda: self.run_async(self._async_reboot())),
            (self.i18n.get("shutdown"), lambda: self.run_async(self._async_shutdown()))
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(300)
            btn.setFixedHeight(40)
            btn.clicked.connect(handler)
            buttons_layout.addWidget(btn, alignment=Qt.AlignCenter)

        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def create_disk_selection_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel(self.i18n.get("disk_selection"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Create table for disk list
        self.disk_table = QTableWidget()
        self.disk_table.setColumnCount(5)
        self.disk_table.setHorizontalHeaderLabels([
            "",  # Checkbox column
            self.i18n.get("disk_name"),
            self.i18n.get("type"),
            self.i18n.get("model"),
            self.i18n.get("size")
        ])
        
        # Set table properties
        self.disk_table.setSelectionMode(QTableWidget.NoSelection)
        self.disk_table.verticalHeader().setVisible(False)
        self.disk_table.setShowGrid(False)
        self.disk_table.setAlternatingRowColors(True)
        self.disk_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # 设置列的调整模式
        header = self.disk_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)  # 默认所有列都是 ResizeToContents
        header.setSectionResizeMode(4, QHeaderView.Stretch)  # size 列设置为 Stretch
        
        # 设置 checkbox 列的固定宽度
        self.disk_table.setColumnWidth(0, 30)
        
        layout.addWidget(self.disk_table)
        page.setLayout(layout)
        return page

    def create_auth_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel(self.i18n.get("authentication"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        # Auth method
        auth_label = QLabel(self.i18n.get("web_ui_auth"))
        auth_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(auth_label)

        self.auth_combo = QComboBox()
        self.auth_combo.addItems([
            self.i18n.get("admin_user"),
            self.i18n.get("configure_webui")
        ])
        self.auth_combo.setFixedWidth(300)
        layout.addWidget(self.auth_combo, alignment=Qt.AlignCenter)

        # Password fields
        self.password_widget = QWidget()
        pass_layout = QGridLayout()
        pass_layout.setSpacing(10)
        
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setFixedWidth(200)
        
        self.pass_confirm = QLineEdit()
        self.pass_confirm.setEchoMode(QLineEdit.Password)
        self.pass_confirm.setFixedWidth(200)
        
        pass_layout.addWidget(QLabel(self.i18n.get("password")), 0, 0)
        pass_layout.addWidget(self.pass_input, 0, 1)
        pass_layout.addWidget(QLabel(self.i18n.get("confirm_password")), 1, 0)
        pass_layout.addWidget(self.pass_confirm, 1, 1)
        
        self.password_widget.setLayout(pass_layout)
        layout.addWidget(self.password_widget, alignment=Qt.AlignCenter)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def create_progress_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel(self.i18n.get("installation_progress"))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.progress_label = QLabel(self.i18n.get("please_wait"))
        self.progress_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(400)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)
        layout.addStretch()

        page.setLayout(layout)
        return page

    def start_installation(self):
        # 显示加载对话框
        self.loading_dialog = QProgressDialog(
            self.i18n.get("please_wait"),  # 消息
            None,  # 取消按钮文本（None表示不显示取消按钮）
            0,     # 最小值
            0,     # 最大值（0表示显示忙碌指示器）
            self   # 父窗口,
        )
        
        self.loading_dialog.setWindowTitle(self.i18n.get("disk_selection"))
        self.loading_dialog.setWindowModality(Qt.WindowModal)
        self.loading_dialog.setAutoClose(True)
        self.loading_dialog.show()

        # 启动异步加载
        self.run_async(self.load_disk_selection())

    async def load_disk_selection(self):
        try:
            # 切换到磁盘选择页面
            self.stacked_widget.setCurrentWidget(self.disk_selection_page)
            self.update_navigation_buttons()
            
            # 加载磁盘列表
            await self.refresh_disk_list()
        finally:
            # 关闭加载对话框
            self.loading_dialog.close()

    async def refresh_disk_list(self):
        self.disk_table.setRowCount(0)
        
        try:
            disks = await list_disks()
            
            if not disks:
                self.disk_table.setRowCount(1)
                cell = QTableWidgetItem(self.i18n.get("no_drives"))
                cell.setTextAlignment(Qt.AlignCenter)
                self.disk_table.setSpan(0, 0, 1, 5)
                self.disk_table.setItem(0, 0, cell)
                return

            self.disk_table.setRowCount(len(disks))
            
            for row, disk in enumerate(disks):
                # Checkbox
                checkbox = QCheckBox()
                checkbox.setProperty("disk_obj", disk)
                checkbox.setStyleSheet("QCheckBox { margin-left: 7px; }") 
                self.disk_table.setCellWidget(row, 0, checkbox)
                
                # Disk name
                name_item = QTableWidgetItem(disk.name)
                name_item.setTextAlignment(Qt.AlignCenter)
                self.disk_table.setItem(row, 1, name_item)
                
                # Type
                type_item = QTableWidgetItem(disk.label[:15].ljust(15, " ") if disk.label else "")
                type_item.setTextAlignment(Qt.AlignCenter)
                self.disk_table.setItem(row, 2, type_item)
                
                model_text = disk.model[:15].ljust(15, " ")
                model_item = QTableWidgetItem(model_text)
                model_item.setTextAlignment(Qt.AlignCenter)
                self.disk_table.setItem(row, 3, model_item)
                
                # Size
                size_item = QTableWidgetItem(humanfriendly.format_size(disk.size, binary=True))
                size_item.setTextAlignment(Qt.AlignCenter)
                self.disk_table.setItem(row, 4, size_item)

            # 强更新表格布局
            self.disk_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
            
            # 确保 Model 列占据剩余空间
            total_width = self.disk_table.viewport().width()
            other_columns_width = sum(self.disk_table.columnWidth(i) for i in [0,1,2,4])
            model_column_width = total_width - other_columns_width
            if model_column_width > 0:
                self.disk_table.setColumnWidth(3, model_column_width)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_disks_selected(self):
        self.selected_disks = []
        self.wipe_disks = []
        
        # Get selected disks from table
        for row in range(self.disk_table.rowCount()):
            checkbox = self.disk_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                disk = checkbox.property("disk_obj")
                self.selected_disks.append(disk)

        if not self.selected_disks:
            QMessageBox.warning(self, "Warning", self.i18n.get("select_disk"))
            return

        # 检查其他包含 boot-pool 的磁盘
        for i in range(self.disk_table.rowCount()):
            item = self.disk_table.item(i, 0)
            if item and item.widget():
                checkbox = item.widget()
                disk = checkbox.property("disk_obj")
                if (not checkbox.isChecked() and 
                    any(zfs_member.pool == "boot-pool" for zfs_member in disk.zfs_members)):
                    self.wipe_disks.append(disk)

        # 如果有需要擦除的磁盘，显示确认对话框
        if self.wipe_disks:
            disk_names = ", ".join(disk.name for disk in self.wipe_disks)
            message = self.i18n.get("disk_contains_boot", disk_names=disk_names)
            reply = QMessageBox.question(self, "OceanNAS Installation", message,
                                       QMessageBox.Yes | QMessageBox.No,
                                       defaultButton=QMessageBox.No)
            if reply == QMessageBox.No:
                return

        selected_names = ", ".join(disk.name for disk in self.selected_disks)
        all_disks = sorted([*[d.name for d in self.wipe_disks], *[d.name for d in self.selected_disks]])
        
        warning_text = self.i18n.get("disk_warning", 
                                    disks=", ".join(all_disks),
                                    selected_disks=selected_names)

        reply = QMessageBox.question(self, f"{self.installer.vendor} Installation", 
                                   warning_text, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return

        # 如果是 Legacy 启动模式，询问是否设置 PMBR
        self.set_pmbr = False
        if not self.installer.efi:
            reply = QMessageBox.question(self, self.i18n.get("legacy_boot"),
                                       self.i18n.get("efi_prompt"),
                                       QMessageBox.Yes | QMessageBox.No)
            self.set_pmbr = (reply == QMessageBox.Yes)

        self.stacked_widget.setCurrentWidget(self.auth_page)
        self.update_navigation_buttons()

    def start_install(self):
        self.run_async(self.start_install_process())
        self.update_navigation_buttons()

    async def start_install_process(self):
        if self.auth_combo.currentText() == self.i18n.get("admin_user"):
            if self.pass_input.text() != self.pass_confirm.text():
                QMessageBox.warning(self, "Error", self.i18n.get("passwords_not_match"))
                return
            auth_method = {
                "username": "truenas_admin",
                "password": self.pass_input.text()
            }
        else:
            auth_method = None

        self.stacked_widget.setCurrentWidget(self.progress_page)
        self.update_navigation_buttons()

        try:
            await install(
                self.selected_disks,
                self.wipe_disks,
                self.set_pmbr,
                auth_method,
                None,  # post_install
                await serial_sql(),
                self.installation_progress_callback
            )
            
            self.progress_bar.setValue(100)
            self.progress_label.setText(self.i18n.get("install_complete"))
            
            # reboot button
            reboot_btn = QPushButton(self.i18n.get("reboot"))
            reboot_btn.setFixedWidth(200)
            reboot_btn.clicked.connect(lambda: self.run_async(self._async_reboot()))
            self.progress_page.layout().addWidget(reboot_btn, alignment=Qt.AlignCenter)
            
            QMessageBox.information(
                self, 
                self.i18n.get("install_success"),
                f"The {self.installer.vendor} installation on {', '.join(d.name for d in self.selected_disks)} succeeded!\n"
                f"{self.i18n.get('reboot_prompt')}"
            )
            self.update_navigation_buttons()
        except InstallError as e:
            self.progress_label.setText(self.i18n.get("install_failed"))
            QMessageBox.critical(self, self.i18n.get("install_error"), e.message)
            self.stacked_widget.setCurrentWidget(self.disk_selection_page)
            self.update_navigation_buttons()
            return False

    def installation_progress_callback(self, progress, message):
        percentage = int(progress * 100)
        self.progress_bar.setValue(percentage)
        self.progress_label.setText(message)

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