import pytest
from unittest.mock import Mock, patch
from truenas_installer.installer_menu import InstallerMenu

@pytest.fixture
def installer():
    installer_mock = Mock()
    installer_mock.vendor = "TrueNAS"
    installer_mock.version = "24.10.0.2"
    installer_mock.efi = True
    return installer_mock

@pytest.fixture
def menu(installer):
    return InstallerMenu(installer)

@pytest.mark.asyncio
async def test_language_selection(menu, monkeypatch):
    """ Test language selection """
    async def mock_dialog_menu(*args, **kwargs):
        return lambda: menu._set_language("zh")
    
    with patch('truenas_installer.installer_menu.dialog_menu', mock_dialog_menu):
        await menu.run()