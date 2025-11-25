import importlib
def test_bot_imports():
    mod = importlib.import_module('bot')
    assert hasattr(mod, 'bot')
