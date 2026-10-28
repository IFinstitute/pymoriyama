# Public API for ttt_research
# Export commonly used functions/classes so users can import them from
# `import ttt_research` or `from ttt_research import ...`.

from .plotting.colors import (
	cmap_blue,
	oklch_to_hex,
	ud_accent,
	ud_base,
)
from .plotting.map import (
	deg2dms,
	dms2deg,
	grid_collection,
	read_grid_text,
)
from .plotting.mpl_helpers import (
	add_color_axis,
	add_subplot_labels,
	path_settings,
	save_plot_image,
)
from .stats.fit import (
	calc_correration,
	calc_linear_fit,
	compute_periodic_averages,
	nanerror,
	valid_convolve,
)
from .stats.hp_filter import D2_sparse, hp_filter
from .stats.running import (
	moving_average,
	moving_error,
	moving_standardization,
	moving_std,
	moving_std_fast,
	running_error,
	running_mean,
	stream_running_error,
	stream_running_mean,
)
from .stats.wavelet import (
	compute_coi,
	compute_coi_stockwell,
	compute_cwt,
	fast_s_transform,
)
from .timeutils.solstice import (
	days_since_solstice,
	summer_solstice_dates,
	winter_solstice_dates,
)
from .timeutils.solstice import (
	days_since_summer_solstice as days_since_summer,
)
from .timeutils.solstice import (
	days_since_winter_solstice as days_since_winter,
)

__all__ = [
	"D2_sparse",
	"add_color_axis",
	"add_subplot_labels",
	"calc_correration",
	"calc_linear_fit",
	"cmap_blue",
	"compute_coi",
	"compute_coi_stockwell",
	"compute_cwt",
	"compute_periodic_averages",
	"days_since_solstice",
	"days_since_summer",
	"days_since_winter",
	"deg2dms",
	"dms2deg",
	"fast_s_transform",
	"grid_collection",
	"hp_filter",
	"moving_average",
	"moving_error",
	"moving_standardization",
	"moving_std",
	"moving_std_fast",
	"nanerror",
	"oklch_to_hex",
	"path_settings",
	"read_grid_text",
	"running_error",
	"running_mean",
	"save_plot_image",
	"stream_running_error",
	"stream_running_mean",
	"summer_solstice_dates",
	"ud_accent",
	"ud_base",
	"valid_convolve",
	"winter_solstice_dates",
]

# register xarray accessors when xarray is available
try:
	import xarray as _xr  # type: ignore
except Exception:
	_xr = None

if _xr is not None:
	try:
		from . import xarray_accessors  # noqa: F401
	except Exception:
		# keep import-time errors from preventing package import
		pass

