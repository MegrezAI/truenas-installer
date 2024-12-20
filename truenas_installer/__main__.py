import argparse
import asyncio
import json
import sys
import signal
from aiohttp import web
from PyQt5.QtWidgets import QApplication
from ixhardware import parse_dmi
from qfluentwidgets import FluentWindow, setTheme, Theme, SplashScreen
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtCore import Qt, QTranslator, QSize, QTimer, QEventLoop
from qframelesswindow import FramelessWindow, StandardTitleBar

from .installer import Installer
from .server import InstallerRPCServer
from .server.doc import generate_api_doc
from .installer_menu import InstallerMenu
from .gui.main_window import InstallerWindow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--doc", action="store_true")
    parser.add_argument("--server", action="store_true")
    parser.add_argument("--cli", action="store_true")
    parser.add_argument("--tui", action="store_true")
    args = parser.parse_args()

    with open("/etc/version") as f:
        version = f.read().strip()

    vendor = "OceanNAS"
    try:
        with open("/data/.vendor") as f:
            vendor = json.loads(f.read()).get("name", "OceanNAS")
    except Exception:
        pass

    dmi = parse_dmi()
    installer = Installer(version, dmi, vendor)

    if args.doc:
        generate_api_doc()
    elif args.server:
        rpc_server = InstallerRPCServer(installer)
        app = web.Application()
        app.router.add_routes(
            [
                web.get("/", rpc_server.handle_http_request),
            ]
        )
        app.on_shutdown.append(rpc_server.on_shutdown)
        web.run_app(app, port=80)
    elif args.tui:
        menu = InstallerMenu(installer)
        asyncio.run(menu.run())
    else:
        # GUI mode
        app = QApplication(sys.argv)

        # Initialize QFluentWidgets with proper style
        setTheme(Theme.LIGHT)

        # Create event loop in a separate thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Create main window
        window = InstallerWindow(installer, loop)
        window.setWindowIcon(QIcon(":/qfluentwidgets/images/logo.png"))

        # Create and configure splash screen
        splash = SplashScreen(window.windowIcon(), window)
        splash.setIconSize(QSize(102, 102))

        # Optional: Configure title bar
        titleBar = StandardTitleBar(splash)
        titleBar.setIcon(window.windowIcon())
        titleBar.setTitle(window.windowTitle())
        
        
        titleBar.maxBtn.hide()
        titleBar.minBtn.hide()
        titleBar.closeBtn.hide()
        
        splash.setTitleBar(titleBar)

        # Show main window first
        window.show()

        # Add any initialization code here
        # Example: Simulating loading time
        event_loop = QEventLoop(window)
        QTimer.singleShot(3000, event_loop.quit)
        event_loop.exec()

        # Hide splash screen when done
        splash.finish()

        # Handle Ctrl+C gracefully
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        sys.exit(app.exec_())


if __name__ == "__main__":
    main()
