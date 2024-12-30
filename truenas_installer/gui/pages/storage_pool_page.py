from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QScrollArea,
    QWidget,
)
from qfluentwidgets import (
    SubtitleLabel,
    setFont,
    PrimaryPushButton,
    CardWidget,
    BodyLabel,
    ComboBox,
    FluentIcon as FIF,
    ScrollArea,
)
from ...utils import GiB, RAID_MIN_DISKS
from ...disks import list_disks
from ..progress_indicator import ProgressIndicator
import humanfriendly
from ..message_dialog import MessageDialog


class DiskCard(CardWidget):
    clicked = pyqtSignal()

    def __init__(self, name, size, model, parent=None):
        super().__init__(parent)
        self.selected = False
        self.name = name
        self.size = size
        self.model = model
        self.initUI()

    def initUI(self):
        self.setFixedSize(140, 90)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Disk info
        self.name_label = SubtitleLabel(self.name, self)
        setFont(self.name_label, 14)
        layout.addWidget(self.name_label)

        self.size_label = BodyLabel(self.size, self)
        setFont(self.size_label, 14)
        layout.addWidget(self.size_label)

        self.model_label = BodyLabel(self.model, self)
        self.model_label.setWordWrap(True)
        setFont(self.model_label, 14)
        layout.addWidget(self.model_label)

        self.updateStyle()

    def updateStyle(self):
        self.setStyleSheet(
            """
            DiskCard {
                background-color: %s;
                border: 2px solid %s;
                border-radius: 8px;
            }
            DiskCard:hover {
                background-color: %s;
                border: 2px solid #2980b9;
            }
        """
            % (
                "#e3f2fd" if self.selected else "#ffffff",
                "#2980b9" if self.selected else "#cccccc",
                "#f0f9ff" if self.selected else "#f5f5f5",
            )
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selected = not self.selected
            self.updateStyle()
            self.clicked.emit()
            event.accept()


class StoragePoolPage(QFrame):
    poolConfigured = pyqtSignal(dict)

    def __init__(self, i18n, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.disk_cards = []
        # 更新RAID选项为新的拓扑类型
        self.raid_options = [
            ("STRIPE", "stripe_description"),
            ("MIRROR", "mirror_description"),
            ("RAIDZ1", "raidz1_description"),
            ("RAIDZ2", "raidz2_description"),
            ("RAIDZ3", "raidz3_description"),
        ]
        self.selected_raid = None
        self.initUI()

    def update_texts(self):
        self.title.setText(self.i18n.get("create_storage_pool"))
        self.description.setText(self.i18n.get("storage_pool_description"))
        self.progress_indicator.setText(self.i18n.get("loading_disks"))

        # 更新RAID相关文本
        raid_label = self.raid_combo.parentWidget().findChild(SubtitleLabel)
        if raid_label:
            raid_label.setText(self.i18n.get("raid_level"))

        # 更新RAID下拉框选项
        self.raid_combo.clear()
        for topology_type, _ in self.raid_options:
            self.raid_combo.addItem(
                self.i18n.get(topology_type)
            ) 

        # 更新RAID描述
        current_index = self.raid_combo.currentIndex()
        self.updateRaidDescription(current_index)

        # 更新已选磁盘标题
        self.selected_disks_title.setText(self.i18n.get("selected_disks"))

        # 更新可用磁盘标题
        disks_label = self.findChild(SubtitleLabel, "available_disks_label")
        if disks_label:
            disks_label.setText(self.i18n.get("available_disks"))

        # 更新按钮文本
        self.back_button.setText(self.i18n.get("back"))
        self.skip_button.setText(self.i18n.get("skip"))
        self.next_button.setText(self.i18n.get("next"))

        # 更新已选磁盘信息（如果有）
        self.updateDiskSelection()

    def initUI(self):
        # 主布局，不使用滚动区域，直接使用 QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # 与硬盘选择页一致
        layout.setSpacing(10)  # 与硬盘选择页一致

        # 标题
        self.title = SubtitleLabel(self.i18n.get("create_storage_pool"), self)
        setFont(self.title, 24)
        layout.addWidget(self.title)

        # 描述（如果需要的话）
        self.description = SubtitleLabel(
            self.i18n.get("storage_pool_description"), self
        )
        setFont(self.description, 14)
        layout.addWidget(self.description)

        # Summary Card (RAID info and Selected Disks)
        self.summary_card = CardWidget(self)
        summary_layout = QVBoxLayout(self.summary_card)
        summary_layout.setContentsMargins(16, 16, 16, 16)
        summary_layout.setSpacing(8)

        # RAID Selection
        raid_layout = QHBoxLayout()
        raid_label = SubtitleLabel(self.i18n.get("raid_level"), self)
        self.raid_combo = ComboBox(self)

        for topology_type, _ in self.raid_options:
            self.raid_combo.addItem(self.i18n.get(topology_type))

        # 添加 RAID 类型改变的信号连接
        self.raid_combo.currentIndexChanged.connect(self.onRaidTypeChanged)

        raid_layout.addWidget(raid_label)
        raid_layout.addWidget(self.raid_combo)
        raid_layout.addStretch()

        # RAID Description
        self.raid_desc = BodyLabel("", self)
        self.raid_desc.setWordWrap(True)

        # Selected Disks Summary
        self.selected_disks_title = SubtitleLabel(self.i18n.get("selected_disks"), self)
        self.selected_disks_label = BodyLabel("", self)
        self.selected_disks_label.setWordWrap(True)

        summary_layout.addLayout(raid_layout)
        summary_layout.addWidget(self.raid_desc)
        summary_layout.addWidget(self.selected_disks_title)
        summary_layout.addWidget(self.selected_disks_label)

        layout.addWidget(self.summary_card)

        # 创建磁盘容器卡片
        self.disks_container = CardWidget(self)
        disks_layout = QVBoxLayout(self.disks_container)
        disks_layout.setContentsMargins(16, 16, 16, 16)
        disks_layout.setSpacing(16)
        disks_layout.setAlignment(Qt.AlignTop)

        # 添加进度指示器
        self.progress_indicator = ProgressIndicator(
            self.i18n.get("loading_disks"), self
        )
        self.progress_indicator.hide()
        disks_layout.addWidget(self.progress_indicator)

        # 创建磁盘网格的容器widget
        self.disks_grid_widget = QWidget()
        self.disks_grid = QGridLayout(self.disks_grid_widget)
        self.disks_grid.setSpacing(16)
        self.disks_grid.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        disks_layout.addWidget(self.disks_grid_widget)

        # 添加一个弹性空间到磁盘容器布局的底部
        disks_layout.addStretch()

        scroll_area = ScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setViewportMargins(0, 0, 0, 0)

        # 将磁盘容器放入滚动区域
        scroll_area.setWidget(self.disks_container)
        
        # 设置滚动区域为伸展的
        layout.addWidget(scroll_area, 1)

        # 添加按钮布局
        button_layout = QHBoxLayout()

        # 添加返回按钮
        self.back_button = PrimaryPushButton(self.i18n.get("back"), self)
        self.back_button.setFixedWidth(120)
        button_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        button_layout.addStretch()

        # 添加跳过和下一步按钮
        self.skip_button = PrimaryPushButton(self.i18n.get("skip"), self)
        self.skip_button.setFixedWidth(120)
        self.next_button = PrimaryPushButton(self.i18n.get("next"), self)
        self.next_button.setFixedWidth(120)
        button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.next_button)

        # 将按钮布局添加到主布局
        layout.addLayout(button_layout)

        # Connect signals
        self.raid_combo.currentIndexChanged.connect(self.updateRaidDescription)
        self.back_button.clicked.connect(self.onBack)
        self.next_button.clicked.connect(self.onNext)
        self.skip_button.clicked.connect(self.onSkip)

        # Set initial RAID description
        self.updateRaidDescription(0)

    async def load_disks(self, selected_disks):
        """加载可用磁盘列表"""
        try:
            # 显示加载状态
            self.disks_grid_widget.hide()
            self.progress_indicator.show()

            # 清除现有的磁盘卡片
            self.clear_disk_cards()

            # 获取磁盘列表
            disks = await list_disks()

            # 过滤掉已经在安装目标中选择的磁盘
            available_disks = [disk for disk in disks if disk not in selected_disks]

            # 创建新的磁盘卡片
            num_columns = 4
            for i, disk in enumerate(available_disks):
                size_str = humanfriendly.format_size(disk.size, binary=True)
                card = DiskCard(f"/dev/{disk.name}", size_str, disk.model or "Unknown")
                card.setFixedSize(200, 120)
                self.disk_cards.append(card)
                card.clicked.connect(self.updateDiskSelection)

                row = i // num_columns
                col = i % num_columns
                self.disks_grid.addWidget(card, row, col)

            self.updateDiskSelection()

        except Exception as e:
            MessageDialog(self.i18n.get("error"), str(e), self).exec()
        finally:
            # 隐藏加载状态，显示磁盘网格
            self.progress_indicator.hide()
            self.disks_grid_widget.show()

    def clear_disk_cards(self):
        """清除所有磁盘卡片"""
        # 确保在清除卡片时隐藏网格容器
        self.disks_grid_widget.hide()
        for card in self.disk_cards:
            self.disks_grid.removeWidget(card)
            card.deleteLater()
        self.disk_cards.clear()

    def showEvent(self, event):
        """当页面显示时加载磁盘"""
        super().showEvent(event)
        window = self.window()
        if hasattr(window, "selected_disks"):
            # 显示加载状态
            self.disks_grid_widget.hide()
            self.progress_indicator.show()
            window.run_async(self.load_disks(window.selected_disks))

    def validate_raid_configuration(self, topology_type, selected_disks):
        """
        验证RAID配置是否合法
        返回 (is_valid, error_message)
        """
        # 基本磁盘数量要求
        min_disks = RAID_MIN_DISKS

        disk_count = len(selected_disks)

        # 1. 检查最小磁盘数量
        if disk_count < min_disks[topology_type]:
            return False, self.i18n.get(
                "min_disks_required", count=min_disks[topology_type]
            )

        # 修复磁盘大小计算
        disk_sizes = []
        for disk in selected_disks:
            size_str = disk.size
            try:
                size_bytes = humanfriendly.parse_size(size_str)
                disk_sizes.append(size_bytes)
            except Exception:
                return False, self.i18n.get("disk_size_parse_error")

        # 检查总容量是否足够（10GB）
        min_total_size = 10 * GiB  # 使用 GiB 常量
        total_size = sum(disk_sizes)
        if total_size < min_total_size:
            return False, self.i18n.get("insufficient_total_size")

        return True, ""

    def calculate_usable_space(self, topology_type, selected_disks):
        """
        计算RAID配置的可用空间
        """
        disk_sizes = []
        for disk in selected_disks:
            try:
                size_bytes = humanfriendly.parse_size(disk.size)
                disk_sizes.append(size_bytes)
            except Exception:
                continue

        if not disk_sizes:
            return 0

        smallest_disk = min(disk_sizes)
        disk_count = len(disk_sizes)

        # 根据不同的RAID类型计算可用空间（单位：字节）
        if topology_type == "STRIPE":
            return sum(disk_sizes)
        elif topology_type == "MIRROR":
            return smallest_disk * (disk_count // 2)
        elif topology_type.startswith("RAIDZ"):
            parity_disks = int(topology_type[-1])
            return smallest_disk * (disk_count - parity_disks)

    def onNext(self):
        """处理下一步按钮点击事件"""
        selected_disks = [card for card in self.disk_cards if card.selected]
        if not selected_disks:
            MessageDialog(
                self.i18n.get("warning"), self.i18n.get("select_disk"), self
            ).exec()
            return

        # 获取选中的拓扑类型
        topology_type = self.raid_options[self.raid_combo.currentIndex()][0]

        # 验证RAID配置
        is_valid, error_message = self.validate_raid_configuration(
            topology_type, selected_disks
        )
        if not is_valid:
            MessageDialog(
                self.i18n.get("warning"), error_message, self, show_cancel=False
            ).exec()
            return

        # 计算可用空间
        usable_space = self.calculate_usable_space(topology_type, selected_disks)

        disk_names = ", ".join([disk.name for disk in selected_disks])
        warning_message = self.i18n.get(
            "pool_creation_warning",
            topology=topology_type,
            disk_count=len(selected_disks),
            usable_space=humanfriendly.format_size(usable_space, binary=True),
            disk_names=disk_names
        )

        # 显示确认对话框
        confirm_dialog = MessageDialog(
            self.i18n.get("warning"),
            warning_message,
            self,
        )

        if confirm_dialog.exec() != MessageDialog.Accepted:
            return

        # 构建存储池配置
        config = {
            "topology_type": topology_type,
            "disks": [disk.name.replace("/dev/", "") for disk in selected_disks],
        }

        self.poolConfigured.emit(config)

    def onSkip(self):
        self.poolConfigured.emit({})  # 发送空配置表示跳过

    def updateRaidDescription(self, index):
        """更新RAID描述"""
        topology_type, desc_key = self.raid_options[index]
        self.selected_raid = topology_type
        self.raid_desc.setText(self.i18n.get(desc_key))

    def updateDiskSelection(self):
        selected_disks = [card for card in self.disk_cards if card.selected]

        if selected_disks:
            try:
                # 获取当前选择的 RAID 类型
                topology_type = self.raid_options[self.raid_combo.currentIndex()][0]

                # 计算实际可用空间
                usable_space = self.calculate_usable_space(
                    topology_type, selected_disks
                )
                formatted_usable_size = humanfriendly.format_size(
                    usable_space, binary=True
                )

                # 计算总物理空间
                total_size = sum(
                    humanfriendly.parse_size(disk.size) for disk in selected_disks
                )
                formatted_total_size = humanfriendly.format_size(
                    total_size, binary=True
                )

                disk_names = [disk.name for disk in selected_disks]

                # 使用正确的翻译键
                summary_text = (
                    f"{self.i18n.get('selected_disks')}: {len(selected_disks)}\n"
                    f"{self.i18n.get('total_size')}: {formatted_total_size}\n"
                    f"{self.i18n.get('usable_space')}: {formatted_usable_size}\n"  # 确保这个键存在于翻译文件中
                    f"{self.i18n.get('disk_name')}: {', '.join(disk_names)}"
                )

                self.selected_disks_label.setText(summary_text)
                self.next_button.setEnabled(True)
            except Exception as e:
                # 打印更详细的错误信息
                import traceback

                print(f"Error in updateDiskSelection: {str(e)}")
                print(traceback.format_exc())
                self.selected_disks_label.setText(
                    self.i18n.get("disk_size_parse_error")
                )
                self.next_button.setEnabled(False)
        else:
            self.selected_disks_label.setText(self.i18n.get("select_disk"))
            self.next_button.setEnabled(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 可以在这里动态调整列数
        width = event.size().width()
        # 根据窗口宽度调整列数的逻辑可以放在这里

    def onBack(self):
        window = self.window()
        window.stackedWidget.setCurrentWidget(window.disk_selection_page)

    def onRaidTypeChanged(self, index):
        """处理 RAID 类型改变事件"""
        topology_type = self.raid_options[index][0]
        selected_disks = [card for card in self.disk_cards if card.selected]

        # RAID类型最小磁盘数要求
        min_disks = RAID_MIN_DISKS
        # 如果已选磁盘数量不满足新RAID类型的要求
        if len(selected_disks) > 0 and len(selected_disks) < min_disks.get(
            topology_type, 1
        ):
            # 先清除所有已选择的磁盘
            for card in self.disk_cards:
                if card.selected:
                    card.selected = False
                    card.updateStyle()

            # 更新磁盘选择显示（会显示"请选择磁盘"）
            self.updateDiskSelection()
            self.updateRaidDescription(index)

            # 然后显示提示信息
            MessageDialog(
                self.i18n.get("warning"),
                self.i18n.get(
                    "raid_type_changed_clear",
                    type=self.i18n.get(topology_type),
                    required=min_disks[topology_type],
                    current=len(selected_disks),
                ),
                self,
                show_cancel=False,
            ).exec()

        # 更新当前选择的RAID类型
        self.selected_raid = topology_type
        # 更新 RAID 描述
        self.updateRaidDescription(index)
        # 更新磁盘选择显示
        self.updateDiskSelection()
