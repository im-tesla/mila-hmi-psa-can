import json
import os
from dataclasses import dataclass, asdict

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

_DEFAULTS = {'simulation': True, 'port': '', 'baudrate': 115200}

_config: 'Config | None' = None


@dataclass
class Config:
    simulation: bool
    port: str
    baudrate: int


def get_config() -> 'Config':
    return _config


def load_config() -> 'Config':
    global _config
    try:
        with open(CONFIG_PATH) as f:
            data = json.load(f)
        _config = Config(
            simulation=bool(data.get('simulation', _DEFAULTS['simulation'])),
            port=str(data.get('port', _DEFAULTS['port'])),
            baudrate=int(data.get('baudrate', _DEFAULTS['baudrate'])),
        )
    except (FileNotFoundError, json.JSONDecodeError, ValueError, KeyError):
        _config = Config(**_DEFAULTS)
    return _config


def save_config(cfg: 'Config') -> None:
    global _config
    _config = cfg
    with open(CONFIG_PATH, 'w') as f:
        json.dump(asdict(cfg), f, indent=2)
