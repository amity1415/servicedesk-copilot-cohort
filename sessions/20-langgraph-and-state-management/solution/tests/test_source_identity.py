from pathlib import Path

import copilot


def test_imports_this_checkpoint_not_the_installed_final_app():
    expected = Path(__file__).resolve().parents[1] / "src/copilot"
    assert Path(copilot.__file__).resolve().parent == expected
