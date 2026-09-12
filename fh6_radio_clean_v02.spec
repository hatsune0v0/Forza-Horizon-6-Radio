# Independent clean-room v0.2 shell; no historical modules or assets included.
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("fh6_radio_clean_v02")

a = Analysis(
    ["fh6_radio_clean_v02/__main__.py"],
    pathex=["."],
    hiddenimports=hiddenimports,
    datas=[],
    binaries=[],
    excludes=["fh6_radio_v02_material_ui", "fh6_radio_material_ui"],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="FH6-Radio-Clean-v0.2", console=False)
coll = COLLECT(exe, a.binaries, a.datas, name="FH6-Radio-Clean-v0.2")
