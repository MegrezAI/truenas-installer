from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                           QTableWidgetItem, QCheckBox, QHeaderView, QMessageBox,
                           QProgressDialog)
from PyQt5.QtCore import Qt, pyqtSignal
import humanfriendly

class DiskSelectionPage(QWidget):
    disksSelected = pyqtSignal(list, list, bool)  # selected_disks, wipe_disks, set_pmbr
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.selected_disks = []
        self.wipe_disks = []
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        self.title = QLabel(self.i18n.get("disk_selection"))
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title)

        # Create table
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

        # Set column resize modes
        header = self.disk_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.disk_table.setColumnWidth(0, 30)
        
        layout.addWidget(self.disk_table)
        self.setLayout(layout)

    async def refresh_disk_list(self, disks):
        # 如果表格已经有内容（排除只有"no drives"消息的情况），就跳过加载
        if (self.disk_table.rowCount() > 0 and 
            not (self.disk_table.rowCount() == 1 and 
                 self.disk_table.columnSpan(0, 0) == 5)):  # 检查是否是"no drives"的情况
            return

        self.disk_table.setRowCount(0)
        
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
            
            # Disk info
            items = [
                (disk.name, Qt.AlignCenter),
                (disk.label[:15].ljust(15, " ") if disk.label else "", Qt.AlignCenter),
                (disk.model[:15].ljust(15, " "), Qt.AlignCenter),
                (humanfriendly.format_size(disk.size, binary=True), Qt.AlignCenter)
            ]
            
            for col, (text, alignment) in enumerate(items, 1):
                item = QTableWidgetItem(text)
                item.setTextAlignment(alignment)
                self.disk_table.setItem(row, col, item)

        # Update layout
        self.disk_table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        
        # Ensure Model column takes remaining space
        total_width = self.disk_table.viewport().width()
        other_columns_width = sum(self.disk_table.columnWidth(i) for i in [0,1,2,4])
        model_column_width = total_width - other_columns_width
        if model_column_width > 0:
            self.disk_table.setColumnWidth(3, model_column_width)

    def validate_selection(self, installer):
        self.selected_disks = []
        self.wipe_disks = []
        
        # Get selected disks
        for row in range(self.disk_table.rowCount()):
            checkbox = self.disk_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                disk = checkbox.property("disk_obj")
                self.selected_disks.append(disk)

        if not self.selected_disks:
            QMessageBox.warning(self, "Warning", self.i18n.get("select_disk"))
            return False

        # Check for other disks containing boot-pool
        for row in range(self.disk_table.rowCount()):
            checkbox = self.disk_table.cellWidget(row, 0)
            if checkbox:
                disk = checkbox.property("disk_obj")
                if (not checkbox.isChecked() and 
                    any(zfs_member.pool == "boot-pool" for zfs_member in disk.zfs_members)):
                    self.wipe_disks.append(disk)

        # Confirm wipe if necessary
        if self.wipe_disks:
            disk_names = ", ".join(disk.name for disk in self.wipe_disks)
            message = self.i18n.get("disk_contains_boot", disk_names=disk_names)
            reply = QMessageBox.question(self, "OceanNAS Installation", message,
                                       QMessageBox.Yes | QMessageBox.No,
                                       defaultButton=QMessageBox.No)
            if reply == QMessageBox.No:
                return False

        # Final confirmation
        selected_names = ", ".join(disk.name for disk in self.selected_disks)
        all_disks = sorted([*[d.name for d in self.wipe_disks], *[d.name for d in self.selected_disks]])
        
        warning_text = self.i18n.get("disk_warning", 
                                    disks=", ".join(all_disks),
                                    selected_disks=selected_names)

        reply = QMessageBox.question(self, f"{installer.vendor} Installation", 
                                   warning_text, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No:
            return False

        # Check for Legacy boot mode
        set_pmbr = False
        if not installer.efi:
            reply = QMessageBox.question(self, self.i18n.get("legacy_boot"),
                                       self.i18n.get("efi_prompt"),
                                       QMessageBox.Yes | QMessageBox.No)
            set_pmbr = (reply == QMessageBox.Yes)

        self.disksSelected.emit(self.selected_disks, self.wipe_disks, set_pmbr)
        return True

    def update_texts(self):
        self.title.setText(self.i18n.get("disk_selection"))
        self.disk_table.setHorizontalHeaderLabels([
            "",
            self.i18n.get("disk_name"),
            self.i18n.get("type"),
            self.i18n.get("model"),
            self.i18n.get("size")
        ])