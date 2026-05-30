"""Eye-verified MTF reference charts for digitizer calibration (#933).

See `REFERENCE_SET.md` for the verified-shape notes per chart and the
reasoning behind the proposed render-match threshold and offset tolerance
band.

`charts.py` is the machine-readable form, loadable by the extractor and
its tests.
"""

from .charts import REFERENCE_CHARTS, ReferenceChart

__all__ = ["REFERENCE_CHARTS", "ReferenceChart"]
