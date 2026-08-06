import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_sprc():
    """Return a MagicMock standing in for SPRC_client instance."""
    m = MagicMock()
    m.open_session.return_value = None
    m.cleanup.return_value = None
    m.scan_ports.return_value = []
    m.select_port.return_value = None
    m.open_file.return_value = None
    m.set_playout_state.return_value = None
    m.set_ts_rate.return_value = None
    m.set_tsiop_pars.return_value = None
    m.set_rf_pars.return_value = None
    m.set_asi_pars.return_value = None
    return m


@pytest.fixture
def client(mock_sprc):
    """Return a StreamXpressClient with SPRC_client() → mock_sprc."""
    # Patch at the point of use: replace the class reference so SPRC_client() returns mock_sprc
    import streamxpress_mcp.client as client_mod

    orig = client_mod.SPRC_client
    client_mod.SPRC_client = MagicMock(return_value=mock_sprc)
    try:
        c = client_mod.StreamXpressClient()
        yield c
    finally:
        client_mod.SPRC_client = orig
