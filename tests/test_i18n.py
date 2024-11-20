import pytest
from truenas_installer.i18n import I18n

def test_i18n_english():
    i18n = I18n("en")
    assert i18n.get("console_setup") == "Console Setup"
    assert i18n.get("install_upgrade") == "Install/Upgrade"

def test_i18n_chinese():
    i18n = I18n("zh")
    assert i18n.get("console_setup") == "控制台设置"
    assert i18n.get("install_upgrade") == "安装/升级"

def test_i18n_fallback():
    i18n = I18n("unknown")  
    assert i18n.get("console_setup") == "Console Setup"