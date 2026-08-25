import json
import pytest
from streamxpress_mcp import config as config_mod


def test_load_config_defaults_when_no_file(monkeypatch, tmp_path):
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", tmp_path / "config.json")
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == ""
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 5000


def test_load_config_from_env_path(monkeypatch, tmp_path):
    cfg_file = tmp_path / "cfg.json"
    cfg_file.write_text(
        json.dumps({"streamxpress_path": "C:/sx.exe", "rc_port": 6000}),
        encoding="utf-8",
    )
    monkeypatch.setenv(config_mod.ENV_VAR, str(cfg_file))
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == "C:/sx.exe"
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 6000


def test_load_config_from_project_root(monkeypatch, tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"sprc_api_path": "D:/SpRcApi"}), encoding="utf-8")
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", cfg_file)
    cfg = config_mod.load_config()
    assert cfg.sprc_api_path == "D:/SpRcApi"


def test_load_config_type_mismatch_uses_defaults(monkeypatch, tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(
        json.dumps(
            {"streamxpress_path": None, "sprc_api_path": 123, "rc_port": "abc"}
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv(config_mod.ENV_VAR, str(cfg_file))
    cfg = config_mod.load_config()
    assert cfg.streamxpress_path == ""
    assert cfg.sprc_api_path == ""
    assert cfg.rc_port == 5000


def test_load_config_invalid_json_raises(monkeypatch, tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text("{not json", encoding="utf-8")
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    monkeypatch.setattr(config_mod, "DEFAULT_CONFIG_PATH", cfg_file)
    with pytest.raises(ValueError, match="配置文件解析失败"):
        config_mod.load_config()


def test_resolve_wsdl_path_empty_returns_none():
    cfg = config_mod.StreamXpressConfig(sprc_api_path="")
    assert config_mod.resolve_wsdl_path(cfg) is None


def test_resolve_wsdl_path_missing_returns_none(tmp_path):
    cfg = config_mod.StreamXpressConfig(sprc_api_path=str(tmp_path))
    assert config_mod.resolve_wsdl_path(cfg) is None


def test_resolve_wsdl_path_found(tmp_path):
    wsdl_dir = tmp_path / "WSDL"
    wsdl_dir.mkdir()
    (wsdl_dir / "SpRc.wsdl").write_text("x", encoding="utf-8")
    cfg = config_mod.StreamXpressConfig(sprc_api_path=str(tmp_path))
    assert config_mod.resolve_wsdl_path(cfg) == str(wsdl_dir / "SpRc.wsdl")


def test_repo_root_config_json_loads_as_defaults(monkeypatch):
    """仓库自带的 config.json 必须字段留空、等价于文件缺失时的默认值。"""
    monkeypatch.delenv(config_mod.ENV_VAR, raising=False)
    assert config_mod.DEFAULT_CONFIG_PATH.is_file(), (
        f"仓库根 config.json 不存在: {config_mod.DEFAULT_CONFIG_PATH}"
    )
    cfg = config_mod.load_config()
    assert isinstance(cfg.streamxpress_path, str)
    assert isinstance(cfg.sprc_api_path, str)
    assert cfg.rc_port == 5000
