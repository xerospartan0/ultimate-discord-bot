import importlib, sys
def test_env_module_imports():
    # ensure utils.validate_env imports without crashing
    mod = importlib.import_module('utils.validate_env')
    assert mod is not None
