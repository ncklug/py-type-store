
import os

__all_settings = dict(
    local=dict(
        engine = 'sqlite:///:memory:'
    )
)

_settings = None


def get(key):
    global _settings
    if not _settings:
        env_name = os.getenv('ENV_NAME', 'local')
        _settings = dict(__all_settings[env_name])
    return _settings[key]