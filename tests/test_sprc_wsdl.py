from pathlib import Path
from streamxpress_mcp.sprc_import import SPRC_client


def test_custom_wsdl_template_used(tmp_path):
    custom = tmp_path / "SpRc.wsdl"
    custom.write_text("CUSTOM-MARKER-123", encoding="utf-8")
    spr = SPRC_client(wsdl_template=str(custom))

    wsdl_file = spr._SPRC_client__create_wsdl_file_for_service(5000, "http://localhost")
    try:
        content = Path(wsdl_file).read_text(encoding="utf-8")
        assert "CUSTOM-MARKER-123" in content
    finally:
        Path(wsdl_file).unlink(missing_ok=True)


def test_default_template_used_when_not_specified():
    spr = SPRC_client()

    wsdl_file = spr._SPRC_client__create_wsdl_file_for_service(5000, "http://localhost")
    try:
        content = Path(wsdl_file).read_text(encoding="utf-8")
        assert "<definitions" in content
    finally:
        Path(wsdl_file).unlink(missing_ok=True)


class TestSprcImportExports:
    """从 test_server.py 拆分迁入"""

    def test_sprc_import_exports_new_types(self):
        from streamxpress_mcp.sprc_import import (
            SpRcVersion, SpRcCmmbPars, SpRcCmPars, SpRcCmPath, SpRcDvbT2Group,
            SpRcDvbT2Pars, SpRcHwNoisePars, SpRcIsdbtPars, SpRcIsdbtLayerPars,
            SpRcPlayoutSfnPars, SpRcSpiPars, SpRcSubLoopPars, SpRcDateTime,
            SpRcTdtAdaptPars, SpRcTsgPars, SpRcSfnStatus,
        )

        assert SpRcVersion(MajorVersion=1, MinorVersion=2, BugFixVersion=3, BuildNumber=4).MajorVersion == 1
        assert SpRcCmmbPars(Bandwidth=0, AreaId=1, TxId=2).AreaId == 1
