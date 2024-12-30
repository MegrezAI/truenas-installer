TRANSLATIONS = {
    "en": {
        "language_selection": "Select Language",
        "language": "Language",
        "console_setup": "Console Setup",
        "install_upgrade": "Install/Upgrade",
        "shell": "Shell",
        "reboot": "Reboot System",
        "shutdown": "Shutdown System",
        "choose_media": "Choose Destination Media",
        "no_drives": "No drives available",
        "select_disk": "Select at least one disk to proceed with the installation.",
        "warning": "WARNING",
        "note": "NOTE:",
        "proceed_install": "Proceed with the installation?",
        "web_ui_auth": "Web UI Authentication Method",
        "admin_user": "Administrative user (admin)",
        "configure_webui": "Configure using Web UI",
        "legacy_boot": "Legacy Boot",
        "efi_prompt": (
            "Allow EFI boot? Enter Yes for systems with newer components such as NVMe devices. Enter No when "
            "system hardware requires legacy BIOS boot workaround."
        ),
        "install_error": "Installation Error",
        "install_success": "Installation Success",
        "install_complete": "Installation Complete",
        "reboot_prompt": "Please reboot and remove the installation media.",
        "continue": "Continue",
        "next": "Next",
        "back": "Back",
        "cancel": "Cancel",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "passwords_not_match": "Passwords do not match",
        "install": "Install",
        "installation_progress": "Installation Progress",
        "please_wait": "Please wait...",
        "main_menu": "Main Menu",
        "disk_selection": "Disk Selection",
        "authentication": "Authentication",
        "loading_disks": "Loading disk information...",
        "disk_name": "Disk Name",
        "type": "Type",
        "model": "Model",
        "size": "Size",
        "scanning_disks": "Scanning disks...",
        "install_failed": "Installation Failed",
        "disk_contains_boot": (
            "Disk(s) {disk_names} contain existing OceanNAS boot pool, but they were not "
            "selected for OceanNAS installation. This configuration will not work unless these disks "
            "are erased.\n\nProceed with erasing {disk_names}?"
        ),
        "disk_warning": (
            "This erases ALL partitions and data on {disks}.\n"
            "- {selected_disks} will be unavailable for use in storage pools.\n\n"
            "NOTE:\n"
            "- Installing on SATA, SAS, or NVMe flash media is recommended.\n"
            "  USB flash sticks are discouraged.\n\n"
            "Proceed with installation?"
        ),
        "yes": "Yes",
        "no": "No",
        "welcome_title": "Welcome to OceanNAS",
        "welcome_message": "Thank you for choosing OceanNAS. This installer will guide you through the installation process. Please select your preferred language to begin.",
        "install_success_message": (
            "OceanNAS has been successfully installed!\n"
            "Please remove the installation media and restart the system."
        ),
        "progress": "Progress",
        "scan_complete": "Scan Complete",
        "installing": "Installing...",
        "progress_page": "Installation Progress",
        "confirm": "Confirm",
        "error": "Error",
        "set_admin_password": "Set administrator password",
        "storage_pool": "Storage Pool",
        "create_storage_pool": "Create Storage Pool",
        "storage_pool_description": (
            "Please select the RAID level and disks for your storage pool.\n"
            "You can also skip this step and create storage pools later through the web interface."
        ),
        "raid_level": "RAID Level",
        "available_disks": "Available Disks",
        "selected_disks": "Selected Disks",
        "skip": "Skip",
        "STRIPE": "Stripe",
        "MIRROR": "Mirror",
        "RAIDZ1": "RAID-Z1",
        "RAIDZ2": "RAID-Z2",
        "RAIDZ3": "RAID-Z3",
        "DRAID1": "DRAID1",
        "DRAID2": "DRAID2",
        "DRAID3": "DRAID3",
        "stripe_description": "Stripes data across disks for maximum performance. No redundancy.",
        "mirror_description": "Mirrors data across disks for redundancy.",
        "raidz1_description": "Single parity RAID-Z. Can survive 1 disk failure.",
        "raidz2_description": "Double parity RAID-Z. Can survive 2 disk failures.",
        "raidz3_description": "Triple parity RAID-Z. Can survive 3 disk failures.",
        "draid1_description": "Distributed single parity RAID. Can survive 1 disk failure.",
        "draid2_description": "Distributed double parity RAID. Can survive 2 disk failures.",
        "draid3_description": "Distributed triple parity RAID. Can survive 3 disk failures.",
        "min_disks_required": "This RAID level requires at least {count} disks.",
        "pool_name": "Pool Name",
        "pool_name_placeholder": "Enter pool name",
        "disk_size_mismatch": "All disks in the pool should be of similar size",
        "mirror_even_disks": "Mirror configuration requires an even number of disks",
        "raidz_recommended_disks": "{type} works best with {counts} disks",
        "insufficient_total_size": "The total pool size must be at least 10GB",
        "confirm_pool_creation": "Confirm Pool Creation",
        "pool_creation_summary": "Creating {topology} pool with {disk_count} disks\nUsable space: {usable_space}",
        "raid_validation": "RAID Validation",
        "raid_config_warning": "Warning: Current RAID configuration may not be optimal",
        "raid_disk_count_warning": "Warning: Selected disk count may affect performance",
        "usable_space": "Usable Space",
        "total_size": "Total Size",
        "proceed_anyway": "Proceed Anyway",
        "disk_size_parse_error": "Error parsing disk size",
        "raid_insufficient_disks": (
            "{type} requires at least {required} disks, but only {current} disk(s) selected.\n"
            "Please select additional disks to meet the minimum requirement."
        ),
        "raid_type_changed_clear": (
            "{type} requires at least {required} disks, but only {current} disk(s) selected.\n"
            "Current disk selection will be cleared. Please select disks again."
        ),
        "disk_selection_description": (
            "Please select the disk(s) for system installation. If more than one disk is selected, "
            "a RAID1 device will be created.\n"
            "System installation disks are only used for the system and cannot be used for storage pools."
        ),
        "pool_creation_warning": """
            This operation will erase ALL data on the following disks:
            {disk_names}

            Pool Configuration:
            - RAID Level: {topology}
            - Number of Disks: {disk_count}
            - Usable Space: {usable_space}
            
            Do you want to proceed with creating the storage pool?
        """,
    },
    "zh": {
        "language": "语言",
        "language_selection": "选择语言",
        "console_setup": "控制台设置",
        "install_upgrade": "安装/升级",
        "shell": "命令行",
        "reboot": "重启系统",
        "shutdown": "关闭系统",
        "choose_media": "选择目标媒体",
        "no_drives": "没有可用的驱动器",
        "select_disk": "请至少选择一个磁盘以继续安装。",
        "warning": "警告",
        "note": "注意：",
        "proceed_install": "是否继续安装？",
        "web_ui_auth": "Web界面认证方式",
        "admin_user": "管理员用户 (admin)",
        "configure_webui": "使用Web界面配置",
        "legacy_boot": "传统引导",
        "efi_prompt": (
            "是否允许EFI引导？对于带有NVMe设备等较新组件的系统，选择是。"
            "如果系统硬件需要传统BIOS引导解决方案，选择否。"
        ),
        "install_error": "安装错误",
        "install_success": "安装成功",
        "install_complete": "安装完成",
        "reboot_prompt": "请重启并移除安装媒体。",
        "continue": "继续",
        "next": "下一步",
        "back": "返回",
        "cancel": "取消",
        "password": "密码",
        "confirm_password": "确认密码",
        "passwords_not_match": "密码不匹配",
        "install": "安装",
        "installation_progress": "安装进度",
        "please_wait": "请稍候...",
        "main_menu": "主菜单",
        "disk_selection": "选择系统安装磁盘",
        "authentication": "认证设置",
        "loading_disks": "正在加载磁盘信息...",
        "disk_name": "磁盘名称",
        "type": "类型",
        "model": "型号",
        "size": "容量",
        "scanning_disks": "正在扫描磁盘...",
        "install_failed": "安装失败",
        "disk_contains_boot": (
            "磁盘 {disk_names} 包含现有的 OceanNAS 引导池，但未被选择用于 OceanNAS 安装。"
            "除非擦除这些磁盘，否则此配置将无法工作。\n\n"
            "是否继续擦除 {disk_names}？"
        ),
        "disk_warning": (
            "这将擦除 {disks} 上的所有分区和数据。\n"
            "- {selected_disks} 将无法用于存储池。\n\n"
            "注意：\n"
            "- 建议安装在 SATA、SAS 或 NVMe 闪存介质上。\n"
            "  不建议使用 USB 闪存盘。\n\n"
            "是否继续安装？"
        ),
        "yes": "是",
        "no": "否",
        "welcome_title": "欢迎使用 OceanNAS",
        "welcome_message": "感谢您选择 OceanNAS。本安装程序将指导您完成安装过程。请选择您偏好的语言以开始安装。",
        "install_success_message": (
            "OceanNAS已经安装成功！\n" "请移除安装媒体并重启系统。"
        ),
        "progress": "进度",
        "scan_complete": "扫描完成",
        "installing": "正在安装...",
        "progress_page": "安装进度",
        "confirm": "确认",
        "error": "错误",
        "set_admin_password": "设置管理员密码",
        "storage_pool": "存储池",
        "create_storage_pool": "创建存储池",
        "storage_pool_description": (
            "请选择存储池的RAID级别和所用的磁盘设备。\n"
            "您也可以跳过该步骤在系统安装后通过管理后台创建存储池。"
        ),
        "disk_selection_description": (
            "请选择系统安装所用的磁盘，如果选择的磁盘数量超过1个，将会用RAID1创建磁盘设备。 \n"
            "系统安装磁盘只用于安装系统，不能用于创建存储池。"
        ),
        "raid_level": "RAID级别",
        "available_disks": "可用磁盘",
        "selected_disks": "已选择的磁盘",
        "skip": "跳过",
        "STRIPE": "条带",
        "MIRROR": "镜像",
        "RAIDZ1": "RAID-Z1",
        "RAIDZ2": "RAID-Z2",
        "RAIDZ3": "RAID-Z3",
        "DRAID1": "DRAID1",
        "DRAID2": "DRAID2",
        "DRAID3": "DRAID3",
        "stripe_description": "数据条带化以获得最大性能。无冗余保护。",
        "mirror_description": "数据镜像以实现冗余。",
        "raidz1_description": "单奇偶校验RAID-Z。可以承受1个磁盘故障。",
        "raidz2_description": "双奇偶校验RAID-Z。可以承受2个磁盘故障。",
        "raidz3_description": "三奇偶校验RAID-Z。可以承受3个磁盘故障。",
        "draid1_description": "分布式单奇偶校验RAID。可以承受1个磁盘故障。",
        "draid2_description": "分布式双奇偶校验RAID。可以承受2个磁盘故障。",
        "draid3_description": "分布式三奇偶校验RAID。可以承受3个磁盘故障。",
        "min_disks_required": "此RAID级别需要至少 {count} 个磁盘。",
        "pool_name": "池名称",
        "pool_name_placeholder": "请输入存储池名称",
        "disk_size_mismatch": "存储池中的所有磁盘大小应该相近",
        "mirror_even_disks": "镜像配置需要偶数个磁盘",
        "raidz_recommended_disks": "{type} 建议使用 {counts} 个磁盘",
        "insufficient_total_size": "存储池总容量必须至少为10GB",
        "confirm_pool_creation": "确认创建存储池",
        "pool_creation_summary": "正在创建 {topology} 存储池，使用 {disk_count} 个磁盘\n可用空间: {usable_space}",
        "raid_validation": "RAID 配置验证",
        "raid_config_warning": "警告：当前RAID配置可能不是最优的",
        "raid_disk_count_warning": "警告：所选磁盘数量可能会影响性能",
        "usable_space": "可用空间",
        "total_size": "总容量",
        "proceed_anyway": "仍然继续",
        "disk_size_parse_error": "磁盘容量解析错误",
        "raid_insufficient_disks": (
            "{type} 需要至少 {required} 个磁盘，但当前只选择了 {current} 个磁盘。\n"
            "请选择额外的磁盘以满足最低要求。"
        ),
        "raid_type_changed_clear": (
            "{type} 需要至少 {required} 个磁盘，但当前只选择了 {current} 个磁盘。\n"
            "已清除当前磁盘选择，请重新选择磁盘。"
        ),
        "pool_creation_warning": """
            此操作将删除以下磁盘上的所有数据：
            {disk_names}

            存储池配置信息：
            - RAID级别：{topology}
            - 磁盘数量：{disk_count}
            - 可用空间：{usable_space}

            是否继续创建存储池？
        """,
    },
}


class I18n:
    def __init__(self, language="en"):
        self.language = language

    def get(self, key, **kwargs):
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(
            key, TRANSLATIONS["en"][key]
        )
        return text.format(**kwargs) if kwargs else text

    def set_language(self, language):
        """Set the current language"""
        if language in TRANSLATIONS:
            self.language = language
