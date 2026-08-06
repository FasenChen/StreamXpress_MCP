import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_sprc():
    """Return a MagicMock that mimics SPRC_client."""
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
    """Return a StreamXpressClient with a mocked SPRC_client factory."""
    from streamxpress_mcp.client import StreamXpressClient

    return StreamXpressClient(sprc_factory=MagicMock(return_value=mock_sprc))
