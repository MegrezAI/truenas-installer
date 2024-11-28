TRANSLATIONS = {
    "en": {
        "language_selection": "Select Language",
        "console_setup": "Console Setup",
        "install_upgrade": "Install/Upgrade",
        "shell": "Shell",
        "reboot": "Reboot System",
        "shutdown": "Shutdown System",
        "choose_media": "Choose Destination Media",
        "no_drives": "No drives available",
        "select_disk": "Select at least one disk to proceed with the installation.",
        "warning": "WARNING:",
        "note": "NOTE:",
        "proceed_install": "Proceed with the installation?",
        "web_ui_auth": "Web UI Authentication Method",
        "admin_user": "Administrative user (oceannas_admin)",
        "configure_webui": "Configure using Web UI",
        "legacy_boot": "Legacy Boot",
        "efi_prompt": (
            "Allow EFI boot? Enter Yes for systems with newer components such as NVMe devices. Enter No when "
            "system hardware requires legacy BIOS boot workaround."
        ),
        "install_error": "Installation Error",
        "install_success": "Installation Succeeded",
        "install_complete": "Installation Complete",
        "reboot_prompt": "Please reboot and remove the installation media.",
        "continue": "Continue",
        "next": "Next",
        "back": "Back",
        "cancel": "Cancel",
        "password": "Password:",
        "confirm_password": "Confirm Password:",
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
        "no_drives": "No drives found",
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
            "The {vendor} installation on {disks} succeeded!\n"
            "{reboot_prompt}"
        ),
    },
    "zh": {
        "language_selection": "选择语言",
        "console_setup": "控制台设置",
        "install_upgrade": "安装/升级",
        "shell": "命令行",
        "reboot": "重启系统",
        "shutdown": "关闭系统",
        "choose_media": "选择目标媒体",
        "no_drives": "没有可用的驱动器",
        "select_disk": "请至少选择一个磁盘以继续安装。",
        "warning": "警告：",
        "note": "注意：",
        "proceed_install": "是否继续安装？",
        "web_ui_auth": "Web界面认证方式",
        "admin_user": "管理员用户 (oceannas_admin)",
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
        "password": "密码：",
        "confirm_password": "确认密码：",
        "passwords_not_match": "密码不匹配",
        "install": "安装",
        "installation_progress": "安装进度",
        "please_wait": "请稍候...",
        "main_menu": "主菜单",
        "disk_selection": "选择磁盘",
        "authentication": "认证设置",
        "loading_disks": "正在加载磁盘信息...",
        "disk_name": "磁盘名称",
        "type": "类型",
        "model": "型号",
        "size": "容量",
        "no_drives": "未找到磁盘",
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
            "{vendor} 安装在 {disks} 上成功！\n"
            "{reboot_prompt}"
        ),
    }
}

class I18n:
    def __init__(self, language="en"):
        self.language = language

    def get(self, key, **kwargs):
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"][key])
        return text.format(**kwargs) if kwargs else text

    def set_language(self, language):
        """Set the current language"""
        if language in TRANSLATIONS:
            self.language = language