import importlib
from pathlib import Path
import shutil


def test_set_config(tmp_path, monkeypatch):
    config_mod = importlib.import_module('texiv.config')
    cfg_path = tmp_path / 'config.toml'
    example = Path(__file__).resolve().parents[1] / 'texiv' / 'config' / 'example.config.toml'
    shutil.copy(example, cfg_path)
    monkeypatch.setattr(config_mod.Config, 'CONFIG_FILE_PATH', str(cfg_path))
    cfg = config_mod.Config()
    monkeypatch.setattr(config_mod.Config, '_write_config_to_disk', lambda self: None)
    cfg.set_config('embed.ollama.MODEL', 'foo')
    assert cfg.cfg['embed']['ollama']['MODEL'] == 'foo'
