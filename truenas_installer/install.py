import asyncio
import json
import os
import subprocess
import tempfile
from typing import Callable

from .disks import Disk
from .exception import InstallError
from .lock import installation_lock
from .utils import get_partitions, run

__all__ = ["InstallError", "install"]

BOOT_POOL = "boot-pool"
POOL = "pool"


async def install(
    destination_disks: list[Disk],
    wipe_disks: list[Disk],
    set_pmbr: bool,
    authentication: dict | None,
    post_install: dict | None,
    sql: str | None,
    storage_pool: dict | None,
    callback: Callable,
):
    """
    执行系统安装流程

    Args:
        destination_disks: 目标安装磁盘列表
        wipe_disks: 需要擦除的磁盘列表
        set_pmbr: 是否设置保护性MBR
        authentication: 认证配置
        post_install: 安装后配置
        sql: SQL配置
        storage_pool: 存储池配置 {
            'name': str,
            'topology_type': str,
            'disks': list[str]
        }
        callback: 进度回调函数
    """
    with installation_lock:
        # 初始化已创建池的列表
        pools_created = []

        try:
            # 验证磁盘选择
            await verify_disk_selection(destination_disks, storage_pool)

            print("\n=== Cleaning Existing Pools and Disks ===")

            # 1. 首先处理需要擦除的磁盘（包含旧的 boot-pool）
            if wipe_disks:
                print("\n=== Cleaning disks with existing boot-pool ===")
                for disk in wipe_disks:
                    print(f"Wiping disk with boot-pool: {disk.name}")
                    await wipe_disk(disk, callback)
                    # 额外清理 ZFS 标签
                    await run(["zpool", "labelclear", "-f", disk.device], check=False)
                    for i in range(1, 16):
                        part_device = f"{disk.device}{i}"
                        await run(
                            ["zpool", "labelclear", "-f", part_device], check=False
                        )

            # 2. 获取所有现有池的信息
            pools = await run(["zpool", "list", "-H", "-o", "name,guid"], check=False)
            existing_pools = []
            for line in pools.stdout.strip().split("\n"):
                if line:
                    pool_name = line.split()[0]
                    existing_pools.append(pool_name)
                    print(f"Found existing pool: {pool_name}")

            # 3. 导出并销毁所有现有池
            for pool_name in existing_pools:
                print(f"Processing pool: {pool_name}")
                # 先尝试导出
                await run(["zpool", "export", "-f", pool_name], check=False)
                # 然后尝试销毁
                await run(["zpool", "destroy", "-f", pool_name], check=False)

            # 4. 对所有目标磁盘进行彻底清理
            for disk in destination_disks:
                print(f"\nCleaning disk: {disk.name}")
                # 清理所有分区和ZFS标签
                await run(["wipefs", "-a", disk.device], check=False)
                await run(["sgdisk", "-Z", disk.device], check=False)

                # 清理磁盘开头和结尾的扇区
                print(f"Wiping disk sectors: {disk.name}")
                await run(
                    ["dd", "if=/dev/zero", f"of={disk.device}", "bs=1M", "count=100"],
                    check=False,
                )
                await run(
                    [
                        "dd",
                        "if=/dev/zero",
                        f"of={disk.device}",
                        "bs=1M",
                        "seek=$((`blockdev --getsize64 "
                        + disk.device
                        + "` / 1024 / 1024 - 100))",
                    ],
                    check=False,
                )

                # 清理所有可能的ZFS标签
                print(f"Clearing ZFS labels: {disk.name}")
                await run(["zpool", "labelclear", "-f", disk.device], check=False)
                for i in range(1, 16):  # 清理更多可能的分区
                    part_device = f"{disk.device}{i}"
                    await run(["zpool", "labelclear", "-f", part_device], check=False)

            # 5. 确保完全销毁目标池
            for pool in [BOOT_POOL, POOL]:
                print(f"Destroying pool: {pool}")
                await run(["zpool", "destroy", "-f", pool], check=False)

            # 6. 清理所有目标磁盘
            for disk in destination_disks:
                callback(0, f"Preparing system disk {disk.name}")
                await run(["wipefs", "-a", disk.device], check=False)
                await run(["sgdisk", "-Z", disk.device], check=False)
                await format_disk(disk, set_pmbr, callback)

            # 7. 获取引导池分区
            disk_parts = []
            part_num = 3  # 使用分区3作为引导池分区
            for disk in destination_disks:
                found = (await get_partitions(disk.device, [part_num]))[part_num]
                if found is None:
                    raise InstallError(f"Failed to find data partition on {disk.name}")
                disk_parts.append(found)

            # 8. 创建引导池
            callback(0, "Creating boot pool")
            await create_boot_pool(disk_parts)
            pools_created.append(BOOT_POOL)

            # 9. 创建存储池（如果配置了）
            if storage_pool:
                await create_storage_pool(
                    topology_type=storage_pool["topology_type"],
                    disks=storage_pool["disks"],
                    callback=callback,
                )
                pools_created.append(POOL)

            # 10. 运行安装程序
            try:
                callback(60, "Running installer")
                await run_installer(
                    [disk.name for disk in destination_disks],
                    authentication,
                    post_install,
                    sql,
                    callback,
                )
            finally:
                print(f"pools_created {pools_created}")
                # 导出所有已创建的池
                for pool in pools_created:
                    await run(["zpool", "export", "-f", pool], check=False)

            callback(100, "Installation completed successfully")
            return True

        except Exception as e:
            print("\n=== Error Recovery ===")
            # 清理所有已创建的池
            for pool in reversed(pools_created):
                try:
                    await run(["zpool", "export", "-f", pool], check=False)
                    await run(["zpool", "destroy", "-f", pool], check=False)
                except Exception as cleanup_error:
                    print(f"Cleanup error for {pool}: {cleanup_error}")

            # 清理所有相关磁盘
            all_disks = [disk.name for disk in destination_disks]
            if storage_pool:
                all_disks.extend(storage_pool["disks"])

            for disk in set(all_disks):  #  去重
                try:
                    await run(["wipefs", "-a", f"/dev/{disk}"], check=False)
                except Exception as cleanup_error:
                    print(f"Cleanup error for disk {disk}: {cleanup_error}")

            if isinstance(e, InstallError):
                raise
            raise InstallError(f"Installation failed: {str(e)}")


async def wipe_disk(disk: Disk, callback: Callable):
    print(f"\nDebug - Wiping disk: {disk.name}")
    print(f"Device path: {disk.device}")

    for zfs_member in disk.zfs_members:
        device_path = f"/dev/{zfs_member.name}"
        print(f"Attempting to clear ZFS label from: {device_path}")

        if (
            result := await run(["zpool", "labelclear", "-f", device_path], check=False)
        ).returncode != 0:
            print(
                f"Debug - Warning: unable to wipe ZFS label from {zfs_member.name}: {result.stderr.strip()}"
            )
            # callback(0, f"Warning: unable to wipe ZFS label from {zfs_member.name}: {result.stderr.strip()}")

    if (
        result := await run(["wipefs", "-a", disk.device], check=False)
    ).returncode != 0:
        print(
            f"Debug - Warning: unable to wipe partition table for {disk.name}: {result.stderr.rstrip()}"
        )
        # callback(0, f"Warning: unable to wipe partition table for {disk.name}: {result.stderr.rstrip()}")

    await run(["sgdisk", "-Z", disk.device], check=False)


async def format_disk(disk: Disk, set_pmbr: bool, callback: Callable):
    await wipe_disk(disk, callback)

    # Create BIOS boot partition
    await run(
        ["sgdisk", "-a4096", "-n1:0:+1024K", "-t1:EF02", "-A1:set:2", disk.device]
    )

    # Create EFI partition (Even if not used, allows user to switch to UEFI later)
    await run(["sgdisk", "-n2:0:+524288K", "-t2:EF00", disk.device])

    # Create data partition
    await run(["sgdisk", "-n3:0:0", "-t3:BF01", disk.device])

    # Bad hardware is bad, but we've seen a few users
    # state that by the time we run `parted` command
    # down below OR the caller of this function tries
    # to do something with the partition(s), they won't
    # be present. This is almost _exclusively_ related
    # to bad hardware, but we will wait up to 30 seconds
    # for the partitions to show up in sysfs.
    disk_parts = await get_partitions(disk.device, [1, 2, 3], tries=30)
    for partnum, part_device in disk_parts.items():
        if part_device is None:
            raise InstallError(
                f"Failed to find partition number {partnum} on {disk.name}"
            )

    if set_pmbr:
        await run(
            ["parted", "-s", disk.device, "disk_set", "pmbr_boot", "on"], check=False
        )


async def create_boot_pool(devices):
    await run(
        [
            "zpool",
            "create",
            "-f",
            "-o",
            "ashift=12",
            "-o",
            "cachefile=none",
            "-o",
            "compatibility=grub2",
            "-O",
            "acltype=off",
            "-O",
            "canmount=off",
            "-O",
            "compression=on",
            "-O",
            "devices=off",
            "-O",
            "mountpoint=none",
            "-O",
            "normalization=formD",
            "-O",
            "relatime=on",
            "-O",
            "xattr=sa",
            BOOT_POOL,
        ]
        + (["mirror"] if len(devices) > 1 else [])
        + devices
    )
    await run(["zfs", "create", "-o", "canmount=off", f"{BOOT_POOL}/ROOT"])
    await run(
        [
            "zfs",
            "create",
            "-o",
            "canmount=off",
            "-o",
            "mountpoint=legacy",
            f"{BOOT_POOL}/grub",
        ]
    )


async def run_installer(disks, authentication, post_install, sql, callback):
    with tempfile.TemporaryDirectory() as src:
        await run(
            [
                "mount",
                "/cdrom/TrueNAS-SCALE.update",
                src,
                "-t",
                "squashfs",
                "-o",
                "loop",
            ]
        )
        try:
            params = {
                "authentication_method": authentication,
                "disks": disks,
                "json": True,
                "pool_name": BOOT_POOL,
                "post_install": post_install,
                "sql": sql,
                "src": src,
            }
            process = await asyncio.create_subprocess_exec(
                "python3",
                "-m",
                "truenas_install",
                cwd=src,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            process.stdin.write(json.dumps(params).encode("utf-8"))
            process.stdin.close()
            error = None
            stderr = ""
            while True:
                line = await process.stdout.readline()
                if not line:
                    break

                line = line.decode("utf-8", "ignore")

                try:
                    data = json.loads(line)
                except ValueError:
                    stderr += line
                else:
                    if "progress" in data and "message" in data:
                        callback(data["progress"], data["message"])
                    elif "error" in data:
                        error = data["error"]
                    else:
                        raise ValueError(f"Invalid truenas_install JSON: {data!r}")
            await process.wait()

            if error is not None:
                result = error
            else:
                result = stderr

            if process.returncode != 0:
                raise InstallError(
                    result
                    or f"Abnormal installer process termination with code {process.returncode}"
                )
        finally:
            await run(["umount", "-f", src])


async def create_storage_pool(topology_type: str, disks: list[str], callback: Callable):
    try:
        print(f"\n=== Storage Pool Creation Debug ===")
        print(f"Topology Type: {topology_type}")
        print(f"Disks: {disks}")

        # 1. 首先彻底清理所有目标磁盘
        print("\n=== Cleaning Storage Disks ===")
        for disk in disks:
            print(f"Cleaning disk: {disk}")
            # 清理所有分区表和文件系统签名
            await run(["wipefs", "-a", f"/dev/{disk}"], check=False)
            # 清除GPT和MBR信息
            await run(["sgdisk", "-Z", f"/dev/{disk}"], check=False)
            # 清理ZFS标签
            await run(["zpool", "labelclear", "-f", f"/dev/{disk}"], check=False)

        # 2. 验证磁盘数量
        min_disks = {
            "STRIPE": 1,
            "MIRROR": 2,
            "RAIDZ1": 3,
            "RAIDZ2": 4,
            "RAIDZ3": 5,
        }
        if len(disks) < min_disks.get(topology_type, 1):
            raise InstallError(
                f"{topology_type} requires at least {min_disks[topology_type]} disks"
            )

        # 3. 验证磁盘是否已被使用
        print("\n=== Checking Disk Usage ===")
        for disk in disks:
            result = await run(["zpool", "status"], check=False)
            print(f"Checking disk {disk}...")
            if f"/dev/{disk}" in result.stdout:
                raise InstallError(f"Disk {disk} is already in use by a ZFS pool")

        # 4. 清理已存在的池
        print("\n=== Cleaning Existing Pools ===")
        await run(["zpool", "export", "-f", POOL], check=False)
        await run(["zpool", "destroy", "-f", POOL], check=False)

        # 5. 构建 zpool create 命令
        base_cmd = [
            "zpool",
            "create",
            "-f",
            # Pool properties
            "-o",
            "ashift=12",
            "-o",
            "autotrim=on",
            # Dataset properties
            "-O",
            "acltype=posixacl",
            "-O",
            "normalization=formD",
            "-O",
            "relatime=on",
            "-O",
            "xattr=sa",
            "-O",
            "dnodesize=auto",
            "-O",
            "compression=lz4",
            "-O",
            "devices=off",
            "-O",
            f"mountpoint=/{POOL}",
            POOL,
        ]

        # 6. 添加拓扑类型
        if topology_type != "STRIPE" and len(disks) > 1:
            base_cmd.append(topology_type.lower())

        # 7. 添加磁盘设备
        base_cmd.extend(f"/dev/{disk}" for disk in disks)

        # 打印完整命令
        print("\n=== ZPool Create Command ===")
        print(" ".join(base_cmd))

        # 8. 创建池
        callback(0, f"Creating storage pool")
        try:
            result = await run(base_cmd)
            print("\n=== Command Output ===")
            print(f"stdout: {result.stdout}")
            print(f"stderr: {result.stderr}")
        except subprocess.CalledProcessError as e:
            print("\n=== Command Error ===")
            print(f"Return code: {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise

        # 9. 验证池状态
        print("\n=== Verifying Pool Status ===")
        result = await run(["zpool", "status", POOL], check=False)
        print(f"Pool Status Output: {result.stdout}")

        if "state: ONLINE" not in result.stdout:
            raise InstallError(f"Storage pool {POOL} creation failed verification")

        callback(0, f"Storage pool {POOL} created successfully")
        print("\n=== Pool Creation Completed Successfully ===")
        return True

    except Exception as e:
        print("\n=== Error Occurred ===")
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")

        # 清理工作
        print("\n=== Cleaning Up ===")
        await run(["zpool", "destroy", "-f", POOL], check=False)

        if isinstance(e, InstallError):
            raise
        raise InstallError(f"Error creating storage pool: {str(e)}")


async def verify_disk_selection(
    destination_disks: list[Disk], storage_pool: dict | None
) -> bool:
    """
    验证磁盘选择的合法性

    Args:
        destination_disks: 用于系统安装的磁盘列表
        storage_pool: 存储池配置 {
            'name': str,
            'topology_type': str,
            'disks': list[str]
        }

    Returns:
        bool: 验证通过返回 True

    Raises:
        InstallError: 当验证失败时抛出
    """
    try:
        print("\n=== Verifying Disk Selection ===")

        # 1. 获取所有磁盘的当前状态
        zpool_status = await run(["zpool", "status"], check=False)
        status_output = zpool_status.stdout

        # 2. 检查系统盘
        print("\nChecking system disks:")
        for disk in destination_disks:
            print(f"\nDetailed check for disk {disk.name}...")

            # 添加详细的分区信息调试
            print(f"Checking partitions for {disk.name}...")
            partitions = await get_partitions(disk.device, [1, 2, 3])
            if any(partitions.values()):
                print(f"Found partitions on {disk.name}:")
                for part_num, part_path in partitions.items():
                    if part_path:
                        print(f"  Partition {part_num}: {part_path}")
                        # 获取分区类型信息
                        try:
                            part_info = await run(["blkid", part_path], check=False)
                            print(f"  Partition {part_num} info: {part_info.stdout}")
                        except Exception as e:
                            print(f"  Error getting partition {part_num} info: {e}")
                print(f"Warning: Disk {disk.name} contains existing partitions")
            else:
                print(f"No partitions found on {disk.name}")

            # 检查ZFS标签
            if f"/dev/{disk.name}" in status_output:
                print(f"Warning: Disk {disk.name} was previously used in a ZFS pool")
                print(f"ZFS status for {disk.name}:")
                print(status_output)

        # 3. 检查存储池磁盘
        if storage_pool:
            print("\nChecking storage pool disks:")
            # 验证存储池磁盘不与系统盘重叠
            boot_disks = {disk.name for disk in destination_disks}
            storage_disks = set(storage_pool["disks"])

            if boot_disks & storage_disks:  # 检查集合交集
                overlapping = boot_disks & storage_disks
                raise InstallError(
                    f"Storage pool disks overlap with boot pool disks: {', '.join(overlapping)}"
                )

            # 检查存储池磁盘的当前状态
            for disk in storage_pool["disks"]:
                print(f"Checking disk {disk}...")
                if f"/dev/{disk}" in status_output:
                    print(f"Warning: Disk {disk} was previously used in a ZFS pool")

        # 4. 验证磁盘数量
        if storage_pool:
            min_disks = {
                "STRIPE": 1,
                "MIRROR": 2,
                "RAIDZ1": 3,
                "RAIDZ2": 4,
                "RAIDZ3": 5,
            }
            required = min_disks.get(storage_pool["topology_type"], 1)
            if len(storage_pool["disks"]) < required:
                raise InstallError(
                    f"Storage pool type {storage_pool['topology_type']} requires at least "
                    f"{required} disks, but only {len(storage_pool['disks'])} provided"
                )

        print("\nDisk verification completed successfully")
        return True

    except Exception as e:
        if isinstance(e, InstallError):
            raise
        raise InstallError(f"Failed to verify disk selection: {str(e)}")
