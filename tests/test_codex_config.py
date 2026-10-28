"""Configuration tests use only temporary fixtures, never the user's .codex."""
import importlib.util
from pathlib import Path
import tomllib

import pytest

spec = importlib.util.spec_from_file_location('prepare_codex_config', Path(__file__).resolve().parents[1] / 'scripts' / 'prepare_codex_config.py')
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)


def test_prepare_and_apply_preserve_other_entries(tmp_path):
    config = tmp_path / 'config.toml'
    original = ('# Preserve this comment\nmodel = "existing"\n[mcp_servers.other]\ncommand = "other.exe"\n'
                '[mcp_servers.ms365]\ncommand = "node.exe"\n[mcp_servers.ms365.env]\nOPTION = "unchanged"\n')
    config.write_text(original, encoding='utf-8')
    root = tmp_path / 'runtime'
    config_module.prepare(config, root)
    assert config.read_text(encoding='utf-8') == original
    config_module.apply(config, root)
    parsed = tomllib.loads(config.read_text(encoding='utf-8'))
    assert parsed['model'] == 'existing'
    assert parsed['mcp_servers']['other'] == {'command': 'other.exe'}
    assert parsed['mcp_servers']['ms365'] == {'command': 'node.exe', 'enabled': False, 'env': {'OPTION': 'unchanged'}}
    assert len(parsed['mcp_servers']['outlook_classic']['enabled_tools']) == 12
    assert next(root.glob('codex-config-before-*.toml')).read_text(encoding='utf-8') == original
    with pytest.raises(ValueError):
        config_module.prepare(config, root)


def test_apply_refuses_concurrent_or_proposal_change(tmp_path):
    config = tmp_path / 'config.toml'
    config.write_text('model = "old"', encoding='utf-8')
    root = tmp_path / 'runtime'
    config_module.prepare(config, root)
    config.write_text('model = "new"', encoding='utf-8')
    with pytest.raises(ValueError):
        config_module.apply(config, root)
    assert config.read_text(encoding='utf-8') == 'model = "new"'
    config_module.prepare(config, root)
    with (root / 'codex-config-proposed.toml').open('a') as handle:
        handle.write('\n# Edited after review')
    with pytest.raises(ValueError):
        config_module.apply(config, root)


def test_only_ms365_enabled_flag_changes(tmp_path):
    config = tmp_path / 'config.toml'
    config.write_text('[mcp_servers.ms365]\nenabled = true\ncommand = "node.exe"\n', encoding='utf-8')
    root = tmp_path / 'runtime'
    config_module.prepare(config, root)
    parsed = tomllib.loads((root / 'codex-config-proposed.toml').read_text(encoding='utf-8'))
    assert parsed['mcp_servers']['ms365'] == {'enabled': False, 'command': 'node.exe'}
