from PyQt5.QtCore import Qt, pyqtSignal, QAbstractTableModel
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QHeaderView
from qfluentwidgets import (
    SubtitleLabel,
    setFont,
    CardWidget,
    TableView,
    PrimaryPushButton,
)
import humanfriendly
from ..progress_indicator import ProgressIndicator
from ..message_dialog import MessageDialog


class DiskTableModel(QAbstractTableModel):
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.disks = []
        self.checked_disk_names = set()
        self.headers = [
            "",  # Checkbox column
            i18n.get("disk_name"),
            i18n.get("type"),
            i18n.get("model"),
            i18n.get("size"),
        ]

    def rowCount(self, parent=None):
        return len(self.disks) if self.disks else 1  # 1 for "no drives" message

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if not self.disks:
            if role == Qt.DisplayRole and index.column() == 0:
                return self.i18n.get("no_drives")
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
            return None

        if role == Qt.DisplayRole:
            disk = self.disks[index.row()]
            col = index.column()
            if col == 0:
                return None  # Checkbox column
            elif col == 1:
                return disk.name
            elif col == 2:
                return disk.label[:15] if disk.label else ""
            elif col == 3:
                return disk.model[:15]
            elif col == 4:
                return humanfriendly.format_size(disk.size, binary=True)

        elif role == Qt.CheckStateRole and index.column() == 0:
            return (
                Qt.Checked
                if self.disks[index.row()].name in self.checked_disk_names
                else Qt.Unchecked
            )

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def flags(self, index):
        if not self.disks:
            return Qt.ItemIsEnabled
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsEnabled

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.column() == 0 and self.disks:
            disk = self.disks[index.row()]
            if value == Qt.Checked:
                self.checked_disk_names.add(disk.name)
            else:
                self.checked_disk_names.discard(disk.name)
            return True
        return False

    def update_disks(self, disks):
        self.beginResetModel()
        self.disks = disks
        self.checked_disk_names.clear()
        self.endResetModel()

    @property
    def checked_disks(self):
        """返回选中的磁盘对象列表"""
        return [disk for disk in self.disks if disk.name in self.checked_disk_names]


class DiskSelectionPage(QFrame):
    disksSelected = pyqtSignal(list, list, bool)  # selected_disks, wipe_disks, set_pmbr

    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.selected_disks = []
        self.wipe_disks = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        self.title = SubtitleLabel(self.i18n.get("disk_selection"), self)
        setFont(self.title, 24)
        layout.addWidget(self.title)

        # 创建卡片容器
        card = CardWidget(self)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(8)

        # 使用 ProgressIndicator
        self.progress_indicator = ProgressIndicator(
            self.i18n.get("loading_disks"), self
        )
        self.progress_indicator.hide()
        card_layout.addWidget(self.progress_indicator)

        # 创建表格模型和视图
        self.model = DiskTableModel(self.i18n)
        self.disk_table = TableView(card)
        self.disk_table.setModel(self.model)

        # 设置表格属性
        self.disk_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.disk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.disk_table.setColumnWidth(0, 40)
        self.disk_table.verticalHeader().hide()

        # 将表格添加到卡片中
        card_layout.addWidget(self.disk_table)

        # 将卡片添加到主布局并设置伸展
        layout.addWidget(card, stretch=1)

        # 添加弹性空间
        layout.addStretch()

        # 添加按钮布局
        button_layout = QHBoxLayout()

        # 添加返回按钮
        self.back_button = PrimaryPushButton(self.i18n.get("back"), self)
        self.back_button.setFixedWidth(120)
        self.back_button.clicked.connect(self.on_back_clicked)
        button_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        button_layout.addStretch()

        # 添加下一步按钮
        self.next_button = PrimaryPushButton(self.i18n.get("next"), self)
        self.next_button.setFixedWidth(120)
        self.next_button.clicked.connect(
            lambda: self.validate_selection(self.window().installer)
        )
        button_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

    async def refresh_disk_list(self, disks):
        """刷新磁盘列表"""
        self.progress_indicator.hide()
        self.disk_table.show()
        self.model.update_disks(disks)

    def show_loading(self):
        """显示加载状态"""
        self.disk_table.hide()
        self.progress_indicator.show()

    def validate_selection(self, installer):
        self.selected_disks = list(self.model.checked_disks)
        self.wipe_disks = []

        if not self.selected_disks:
            MessageDialog(
                self.i18n.get("warning"), self.i18n.get("select_disk"), self
            ).exec()
            return False

        # 检查其他包含 boot-pool 的磁盘
        for disk in self.model.disks:
            if disk not in self.selected_disks and any(
                zfs_member.pool == "boot-pool" for zfs_member in disk.zfs_members
            ):
                self.wipe_disks.append(disk)

        # 如果需要，确认擦除
        if self.wipe_disks:
            disk_names = ", ".join(disk.name for disk in self.wipe_disks)
            message = self.i18n.get("disk_contains_boot", disk_names=disk_names)
            box = MessageDialog(self.i18n.get("warning"), message, self)
            if not box.exec():
                return False

        # 最终确认
        selected_names = ", ".join(disk.name for disk in self.selected_disks)
        all_disks = sorted(
            [*[d.name for d in self.wipe_disks], *[d.name for d in self.selected_disks]]
        )

        warning_text = self.i18n.get(
            "disk_warning", disks=", ".join(all_disks), selected_disks=selected_names
        )

        box = MessageDialog(self.i18n.get("warning"), warning_text, self)
        if not box.exec():
            return False

        # 检查 Legacy 启动模式
        set_pmbr = False
        if not installer.efi:
            box = MessageDialog(
                self.i18n.get("legacy_boot"), self.i18n.get("efi_prompt"), self
            )
            set_pmbr = box.exec()

        self.disksSelected.emit(self.selected_disks, self.wipe_disks, set_pmbr)
        return True

    def on_back_clicked(self):
        window = self.window()
        window.stackedWidget.setCurrentWidget(window.language_page)
        # window.switchTo(window.main_menu_page)

    def update_texts(self):
        self.title.setText(self.i18n.get("disk_selection"))
        self.next_button.setText(self.i18n.get("next"))
        self.back_button.setText(self.i18n.get("back"))
        self.progress_indicator.setText(self.i18n.get("loading_disks"))
        self.model.headers = [
            "",
            self.i18n.get("disk_name"),
            self.i18n.get("type"),
            self.i18n.get("model"),
            self.i18n.get("size"),
        ]
        self.model.layoutChanged.emit()
