import asyncio
import os
import sys

import humanfriendly

from .dialog import dialog_checklist, dialog_menu, dialog_msgbox, dialog_password, dialog_yesno
from .disks import Disk, list_disks
from .exception import InstallError
from .install import install
from .serial import serial_sql
from .i18n import I18n


class InstallerMenu:
    def __init__(self, installer):
        self.installer = installer
        self.i18n = I18n()  # Default to English

    async def run(self):
        # Add language selection before main menu
        languages = {"English": "en", "中文": "zh"}
        await dialog_menu(
            self.i18n.get("language_selection"),
            {name: lambda code=code: self._set_language(code) for name, code in languages.items()}
        )
        await self._main_menu()

    def _set_language(self, language):
        self.i18n = I18n(language)
        return True

    async def _main_menu(self):
        await dialog_menu(
            f"{self.installer.vendor} {self.installer.version} {self.i18n.get('console_setup')}",
            {
                self.i18n.get("install_upgrade"): self._install_upgrade,
                self.i18n.get("shell"): self._shell,
                self.i18n.get("reboot"): self._reboot,
                self.i18n.get("shutdown"): self._shutdown,
            }
        )

    async def _install_upgrade(self):
        while True:
            await self._install_upgrade_internal()
            await self._main_menu()

    async def _install_upgrade_internal(self):
        disks = await list_disks()
        vendor = self.installer.vendor

        if not disks:
            await dialog_msgbox(self.i18n.get("choose_media"), self.i18n.get("no_drives"))
            return False

        while True:
            destination_disks = await dialog_checklist(
                self.i18n.get("choose_media"),
                (
                    f"Install {vendor} to a drive. If desired, select multiple drives to provide redundancy. {vendor} "
                    "installation drive(s) are not available for use in storage pools. Use arrow keys to navigate "
                    "options. Press spacebar to select."
                ),
                {
                    disk.name: " ".join([
                        disk.model[:15].ljust(15, " "),
                        disk.label[:15].ljust(15, " "),
                        "--",
                        humanfriendly.format_size(disk.size, binary=True)
                    ])
                    for disk in disks
                }
            )

            if destination_disks is None:
                # Installation cancelled
                return False

            if not destination_disks:
                await dialog_msgbox(
                    self.i18n.get("choose_media"),
                    self.i18n.get("select_disk"),
                )
                continue

            wipe_disks = [
                disk.name
                for disk in disks
                if (
                    any(zfs_member.pool == "boot-pool" for zfs_member in disk.zfs_members) and
                    disk.name not in destination_disks
                )
            ]
            if wipe_disks:
                # The presence of multiple `boot-pool` disks with different guids leads to boot pool import error
                text = "\n".join([
                    f"Disk(s) {', '.join(wipe_disks)} contain existing TrueNAS boot pool, but they were not "
                    f"selected for TrueNAS installation. This configuration will not work unless these disks "
                    "are erased.",
                    "",
                    f"Proceed with erasing {', '.join(wipe_disks)}?"
                ])
                if not await dialog_yesno("TrueNAS Installation", text):
                    continue

            break

        text = "\n".join([
            f"{self.i18n.get('warning')}",
            f"- This erases ALL partitions and data on {', '.join(sorted(wipe_disks + destination_disks))}.",
            f"- {', '.join(destination_disks)} will be unavailable for use in storage pools.",
            "",
            f"{self.i18n.get('note')}",
            "- Installing on SATA, SAS, or NVMe flash media is recommended.",
            "  USB flash sticks are discouraged.",
            "",
            self.i18n.get("proceed_install")
        ])
        if not await dialog_yesno(f"{self.installer.vendor} Installation", text):
            return False

        authentication_method = await dialog_menu(
            self.i18n.get("web_ui_auth"),
            {
                self.i18n.get("admin_user"): self._authentication_truenas_admin,
                self.i18n.get("configure_webui"): self._authentication_webui,
            }
        )
        if authentication_method is False:
            return False

        set_pmbr = False
        if not self.installer.efi:
            set_pmbr = await dialog_yesno(
                self.i18n.get("legacy_boot"),
                self.i18n.get("efi_prompt"),
            )

        # If the installer was booted with serial mode enabled, we should save these values to the installed system
        sql = await serial_sql()

        try:
            await install(
                self._select_disks(disks, destination_disks),
                self._select_disks(disks, wipe_disks),
                set_pmbr,
                authentication_method,
                None,
                sql,
                self._callback,
            )
        except InstallError as e:
            await dialog_msgbox(self.i18n.get("install_error"), e.message)
            return False

        await dialog_msgbox(
            self.i18n.get("install_success"),
            (
                f"The {self.installer.vendor} installation on {', '.join(destination_disks)} succeeded!\n"
                f"{self.i18n.get('reboot_prompt')}"
            ),
        )
        return True

    def _select_disks(self, disks: list[Disk], disks_names: list[str]):
        disks_dict = {disk.name: disk for disk in disks}
        return [disks_dict[disk_name] for disk_name in disks_names]

    async def _authentication_truenas_admin(self):
        return await self._authentication_password(
            "truenas_admin",
            "Enter your \"truenas_admin\" user password. Root password login will be disabled.",
        )

    async def _authentication_password(self, username, title):
        password = await dialog_password(title)
        if password is None:
            return False

        return {"username": username, "password": password}

    async def _authentication_webui(self):
        return None

    async def _shell(self):
        os._exit(1)

    async def _reboot(self):
        process = await asyncio.create_subprocess_exec("reboot")
        await process.communicate()

    async def _shutdown(self):
        process = await asyncio.create_subprocess_exec("shutdown", "now")
        await process.communicate()

    def _callback(self, progress, message):
        sys.stdout.write(f"[{int(progress * 100)}%] {message}\n")
        sys.stdout.flush()