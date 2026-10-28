"""xarray DataArray accessors for ttt_research.

Registers `.nanerror` accessor when `xarray` is available.
"""
try:
    import xarray as xr
except Exception:  # xarray not installed or import error -> no registration
    xr = None

if xr is not None:
    from .stats.fit import nanerror

    @xr.register_dataarray_accessor("nanerror")
    class NanErrorAccessor:
        def __init__(self, xarray_obj):
            self._obj = xarray_obj

        def __call__(self, dim=None, axis=None, keep_attrs=True, fillna=None):
            # dim -> axis indices
            if dim is not None:
                if isinstance(dim, str):
                    dims = (dim,)
                else:
                    dims = tuple(dim)
                axes = tuple(self._obj.dims.index(d) for d in dims)
            else:
                axes = axis

            vals = self._obj.values
            res = nanerror(vals, axis=axes)

            # Wrap result back to DataArray preserving remaining dims/coords
            if axes is None:
                assert xr is not None
                out = xr.DataArray(res)
            else:
                if isinstance(axes, int):
                    axes = (axes,)
                remaining_dims = [d for i, d in enumerate(self._obj.dims) if i not in axes]
                coords = {d: self._obj.coords[d] for d in remaining_dims}
                assert xr is not None
                out = xr.DataArray(res, coords=coords, dims=remaining_dims)

            if fillna is not None:
                out = out.fillna(fillna)

            if keep_attrs:
                out.attrs = dict(self._obj.attrs)

            return out
