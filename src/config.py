"""
config.py — User configuration loader/saver for Plans.

Config is stored as JSON at ~/.plans_config.json.
Falls back to DEFAULTS if the file doesn't exist.
"""

import os
import json

CONFIG_PATH = os.path.expanduser("~/.plans_config.json")

DEFAULTS = {
    "vault_path": os.path.expanduser("~/Documents/ObsidianVault/plans"),
    "theme": "dark",
}

def load_config():
    """Load config from disk, merging with DEFAULTS for any missing keys."""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return {**DEFAULTS, **json.load(f)}
    return DEFAULTS

def save_config(config):
    """Write config dict to disk as JSON."""
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def get(key):
    """Return a single config value by key, falling back to DEFAULTS."""
    return load_config().get(key, DEFAULTS.get(key))
