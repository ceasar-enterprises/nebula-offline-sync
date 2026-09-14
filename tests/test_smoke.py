"""Smoke tests for the engine package scaffold."""

import nebula_offline_sync as engine


def test_package_imports_and_has_version():
    assert engine.__version__
    assert engine.__version__.count(".") == 2


def test_engine_namespace_is_structured():
    # Phase 0 checkpoint: package, docs, and tests exist and import cleanly.
    assert hasattr(engine, "__version__")