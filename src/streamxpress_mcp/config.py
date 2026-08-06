"""Configuration loading for the StreamXpress MCP server.

Users copy `config.example.json` to `config.json` at the project root and
fill in the StreamXpress executable path (and optionally a custom SpRcApi
path used as the WSDL source). Lookup order:
  1. file path from env var STREAMXPRESS_MCP_CONFIG
  2. <project root>/config.json
  3. defaults (no file -> empty paths, rc_port=5000)
"""

import json
import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"
ENV_VAR = "STREAMXPRESS_MCP_CONFIG"


@dataclass
class StreamXpressConfig:
    streamxpress_path: str = ""
    sprc_api_path: str = ""
    rc_port: int = 5000


def _find_config_file() -> Path | None:
    env_path = os.environ.get(ENV_VAR)
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p
        raise ValueError(f"{ENV_VAR} 指定的配置文件不存在: {env_path}")
    if DEFAULT_CONFIG_PATH.is_file():
        return DEFAULT_CONFIG_PATH
    return None


def load_config() -> StreamXpressConfig:
    cfg_file = _find_config_file()
    if cfg_file is None:
        return StreamXpressConfig()
    try:
        data = json.loads(cfg_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"配置文件解析失败: {cfg_file} — {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"配置文件格式错误（应为 JSON 对象）: {cfg_file}")
    return StreamXpressConfig(
        streamxpress_path=str(data.get("streamxpress_path", "")),
        sprc_api_path=str(data.get("sprc_api_path", "")),
        rc_port=int(data.get("rc_port", 5000)),
    )


def resolve_wsdl_path(cfg: StreamXpressConfig) -> str | None:
    """Return <sprc_api_path>/WSDL/SpRc.wsdl if it exists, else None."""
    if not cfg.sprc_api_path:
        return None
    candidate = Path(cfg.sprc_api_path) / "WSDL" / "SpRc.wsdl"
    if candidate.is_file():
        return str(candidate)
    return None
