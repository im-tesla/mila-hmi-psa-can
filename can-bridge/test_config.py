import json
import pytest
import config as cfg_module
from config import Config, load_config, save_config, get_config


@pytest.fixture(autouse=True)
def tmp_config(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg_module, 'CONFIG_PATH', str(tmp_path / 'config.json'))


def test_load_defaults_when_no_file():
    c = load_config()
    assert c.simulation is True
    assert c.port == ''
    assert c.baudrate == 115200


def test_get_config_returns_loaded():
    load_config()
    c = get_config()
    assert c.simulation is True


def test_save_and_reload():
    save_config(Config(simulation=False, port='/dev/ttyUSB0', baudrate=230400))
    c = load_config()
    assert c.simulation is False
    assert c.port == '/dev/ttyUSB0'
    assert c.baudrate == 230400


def test_load_tolerates_corrupt_file():
    with open(cfg_module.CONFIG_PATH, 'w') as f:
        f.write('not json')
    c = load_config()
    assert c.simulation is True
    assert c.baudrate == 115200


def test_save_writes_valid_json(tmp_path):
    save_config(Config(simulation=True, port='COM3', baudrate=9600))
    data = json.loads(open(cfg_module.CONFIG_PATH).read())
    assert data == {'simulation': True, 'port': 'COM3', 'baudrate': 9600}
