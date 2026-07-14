from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "relative_path",
    [
        "app.py",
        "pages/1_Analyze.py",
        "pages/2_Compare_Strategies.py",
        "pages/3_Batch_Evaluation.py",
        "pages/4_Evaluation_Dashboard.py",
        "pages/5_Project_Info.py",
    ],
)
def test_streamlit_page_loads_without_exception(relative_path: str) -> None:
    app = AppTest.from_file(str(ROOT / relative_path), default_timeout=30).run()
    assert not app.exception
