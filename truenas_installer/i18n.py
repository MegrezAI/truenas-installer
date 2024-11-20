TRANSLATIONS = {
    "en": {
        "language_selection": "Select Language / 选择语言",
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
        "admin_user": "Administrative user (truenas_admin)",
        "configure_webui": "Configure using Web UI",
        "legacy_boot": "Legacy Boot",
        "efi_prompt": (
            "Allow EFI boot? Enter Yes for systems with newer components such as NVMe devices. Enter No when "
            "system hardware requires legacy BIOS boot workaround."
        ),
        "install_error": "Installation Error",
        "install_success": "Installation Succeeded",
        "reboot_prompt": "Please reboot and remove the installation media.",
      
    },
    "zh": {
        "language_selection": "选择语言 / Select Language",
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
        "admin_user": "管理员用户 (truenas_admin)",
        "configure_webui": "使用Web界面配置",
        "legacy_boot": "传统引导",
        "efi_prompt": (
            "是否允许EFI引导？对于带有NVMe设备等较新组件的系统，选择是。"
            "如果系统硬件需要传统BIOS引导解决方案，选择否。"
        ),
        "install_error": "安装错误",
        "install_success": "安装成功",
        "reboot_prompt": "请重启并移除安装媒体。",
    }
}

class I18n:
    def __init__(self, language="en"):
        self.language = language

    def get(self, key, **kwargs):
        text = TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"][key])
        return text.format(**kwargs) if kwargs else text