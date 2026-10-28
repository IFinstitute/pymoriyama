import os
import urllib.request
import shutil
import inspect
import datetime as dt
import numpy as np
import numpy.core.numeric as _nx
DEFAULT_URLOPEN_TIMEOUT = 10.0

def download_file(url, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    with urllib.request.urlopen(url, timeout=DEFAULT_URLOPEN_TIMEOUT) as web_file:
        with open(dst_path, "wb") as local_file:
            shutil.copyfileobj(web_file, local_file)
            local_file.write(web_file.read())


def dump_plot_numeric_info(dump1, suffix=""):

    frame = inspect.currentframe()
    if frame is None:
        return None
    caller = frame.f_back  # 安全にアクセス
    if caller is None:
    # 呼び出し元が取れない場合は安全に抜ける（必要なら例外に変更）
        del frame
        return None
    filename = caller.f_code.co_filename

    file_name, file_ext = os.path.splitext(os.path.basename(filename))
    parent_dir = os.path.dirname(os.path.dirname(filename))
    save_dir = os.path.join(parent_dir, "img", file_name, "dump")
    os.makedirs(save_dir, exist_ok=True)
    dump_name = os.path.join(save_dir, f"{suffix}.csv")
    dump1.T.to_csv(dump_name)
    print(f"saved {dump_name} ..")

def gen_date_series(start_date, end_date):
    date_tmp = start_date
    date = [date_tmp]
    for i in range((end_date - start_date).days):
        date_tmp += dt.timedelta(days=1)
        date.append(date_tmp)

    return np.array(date)


def calc_saturation_ratio(tmp_var, tmp_std, h2o_var, h2o_std, lev):
    tmp_var = np.asarray(tmp_var)
    tmp_std = np.asarray(tmp_std)
    h2o_var = np.asarray(h2o_var)
    h2o_std = np.asarray(h2o_std)
    lev = np.asarray(lev)

    # broadcast pressure levels to (time, lat, lev)
    p = lev[np.newaxis, np.newaxis, :]

    with np.errstate(divide="ignore", invalid="ignore"):
        pice = 0.01 * np.exp(
            9.550426 - (5723.265 / tmp_var)
            + (3.53068 * np.log(tmp_var))
            - (0.00728332 * tmp_var)
        )  # (hPa) MK05
        ph2o = h2o_var * 1e-6 * p
        satr = ph2o / pice

        term1 = (h2o_std * 1e-6 * p) ** 2
        deriv = (5723.265 / (tmp_var ** 2)) + (3.53068 / tmp_var) - 0.00728332
        term2 = (ph2o * deriv * tmp_std) ** 2
        satr_err = (1 / pice) * np.sqrt(term1 + term2)

    return satr * 1e2, satr_err * 1e2

def uncertain_grad(f, *varargs, axis=None, edge_order=1):
    """Calculate uncertainity of gradient

    Args:
        f (array_like): An N-dimensional array containing samples of a scalar function.
        axis (list of scalar or array, optional): Spacing between f values. Default unitary spacing for all dimensions.
        Spacing can be specified using:

        1. single scalar to specify a sample distance for all dimensions.
        2. N scalars to specify a constant sample distance for each dimension.
           i.e. `dx`, `dy`, `dz`, ...
        3. N arrays to specify the coordinates of the values along each
           dimension of F. The length of the array must match the size of
           the corresponding dimension
        4. Any combination of N scalars/arrays with the meaning of 2. and 3.

        If `axis` is given, the number of varargs must equal the number of axes. Defaults to None.
        edge_order (int, {1, 2}, optional): Gradient is calculated using N-th order accurate differences
        at the boundaries. Defaults to 1.

    Returns:
        uncertainity of gradient : ndarray or list of ndarray
        A list of ndarrays (or a single ndarray if there is only one dimension)
        corresponding to the derivatives of f with respect to each dimension.
        Each derivative has the same shape as f.
    """
    f = np.asanyarray(f)
    N = f.ndim  # number of dimensions

    if axis is None:
        axes = tuple(range(N))
    else:
        axes = _nx.normalize_axis_tuple(axis, N)  # type: ignore

    len_axes = len(axes)
    n = len(varargs)
    if n == 0:
        # no spacing argument - use 1 in all axes
        dx = [1.0] * len_axes
    elif n == 1 and np.ndim(varargs[0]) == 0:
        # single scalar for all axes
        dx = varargs * len_axes
    elif n == len_axes:
        # scalar or 1d array for each axis
        dx = list(varargs)
        for i, distances in enumerate(dx):
            distances = np.asanyarray(distances)
            if distances.ndim == 0:
                continue
            elif distances.ndim != 1:
                raise ValueError("distances must be either scalars or 1d")
            if len(distances) != f.shape[axes[i]]:
                raise ValueError("when 1d, distances must match "
                                 "the length of the corresponding dimension")
            if np.issubdtype(distances.dtype, np.integer):
                # Convert numpy integer types to float64 to avoid modular
                # arithmetic in np.diff(distances).
                distances = distances.astype(np.float64)
            diffx = np.diff(distances)
            # if distances are constant reduce to the scalar case
            # since it brings a consistent speedup
            if (diffx == diffx[0]).all():
                diffx = diffx[0]
            dx[i] = diffx
    else:
        raise TypeError("invalid number of arguments")

    if edge_order > 2:
        raise ValueError("'edge_order' greater than 2 not supported")

    # use central differences on interior and one-sided differences on the
    # endpoints. This preserves second order-accuracy over the full domain.

    outvals = []

    # create slice objects --- initially all are [:, :, ..., :]
    slice1 = [slice(None)]*N
    slice2 = [slice(None)]*N
    slice3 = [slice(None)]*N
    slice4 = [slice(None)]*N

    otype = f.dtype
    if otype.type is np.datetime64:
        # the timedelta dtype with the same unit information
        otype = np.dtype(otype.name.replace('datetime', 'timedelta'))
        # view as timedelta to allow addition
        f = f.view(otype)
    elif otype.type is np.timedelta64:
        pass
    elif np.issubdtype(otype, np.inexact):
        pass
    else:
        # All other types convert to floating point.
        # First check if f is a numpy integer type; if so, convert f to float64
        # to avoid modular arithmetic when computing the changes in f.
        if np.issubdtype(otype, np.integer):
            f = f.astype(np.float64)
        otype = np.float64

    for axis, ax_dx in zip(axes, dx):
        if f.shape[axis] < edge_order + 1:
            raise ValueError(
                "Shape of array too small to calculate a numerical gradient, "
                "at least (edge_order + 1) elements are required.")
        # result allocation
        out = np.empty_like(f, dtype=otype)

        # spacing for the current axis
        uniform_spacing = np.ndim(ax_dx) == 0

        # Numerical differentiation: 2nd order interior
        slice1[axis] = slice(1, -1)
        slice2[axis] = slice(None, -2)
        slice3[axis] = slice(1, -1)
        slice4[axis] = slice(2, None)

        if uniform_spacing:
            out[tuple(slice1)] = np.sqrt((f[tuple(slice4)]**2 + f[tuple(slice2)]**2) / (2. * ax_dx)**2)
        else:
            dx1 = ax_dx[0:-1]  # type: ignore
            dx2 = ax_dx[1:]  # type: ignore
            a = -(dx2)/(dx1 * (dx1 + dx2))
            b = (dx2 - dx1) / (dx1 * dx2)
            c = dx1 / (dx2 * (dx1 + dx2))
            # fix the shape for broadcasting
            shape = np.ones(N, dtype=int)
            shape[axis] = -1
            a.shape = b.shape = c.shape = shape
            # 1D equivalent -- out[1:-1] = a * f[:-2] + b * f[1:-1] + c * f[2:]
            out[tuple(slice1)] = np.sqrt((a**2) * (f[tuple(slice2)]**2) + (b**2) * (f[tuple(slice3)]**2) + (c**2) * (f[tuple(slice4)]**2))

        # Numerical differentiation: 1st order edges
        if edge_order == 1:
            slice1[axis] = 0
            slice2[axis] = 1
            slice3[axis] = 0
            dx_0 = ax_dx if uniform_spacing else ax_dx[0]  # type: ignore
            # 1D equivalent -- out[0] = (f[1] - f[0]) / (x[1] - x[0])
            out[tuple(slice1)] = np.sqrt((f[tuple(slice2)]**2 + f[tuple(slice3)]**2) / dx_0**2)

            slice1[axis] = -1
            slice2[axis] = -1
            slice3[axis] = -2
            dx_n = ax_dx if uniform_spacing else ax_dx[-1]  # type: ignore
            # 1D equivalent -- out[-1] = (f[-1] - f[-2]) / (x[-1] - x[-2])
            out[tuple(slice1)] = np.sqrt((f[tuple(slice2)]**2 + f[tuple(slice3)]**2) / dx_n**2)

        # Numerical differentiation: 2nd order edges
        else:
            slice1[axis] = 0
            slice2[axis] = 0
            slice3[axis] = 1
            slice4[axis] = 2
            if uniform_spacing:
                a = -1.5 / ax_dx
                b = 2. / ax_dx
                c = -0.5 / ax_dx
            else:
                dx1 = ax_dx[0]  # type: ignore
                dx2 = ax_dx[1]  # type: ignore
                a = -(2. * dx1 + dx2)/(dx1 * (dx1 + dx2))
                b = (dx1 + dx2) / (dx1 * dx2)
                c = - dx1 / (dx2 * (dx1 + dx2))
            # 1D equivalent -- out[0] = a * f[0] + b * f[1] + c * f[2]
            out[tuple(slice1)] = np.sqrt((a**2) * (f[tuple(slice2)]**2) + (b**2) * (f[tuple(slice3)]**2) + (c**2) * (f[tuple(slice4)]**2))

            slice1[axis] = -1
            slice2[axis] = -3
            slice3[axis] = -2
            slice4[axis] = -1
            if uniform_spacing:
                a = 0.5 / ax_dx
                b = -2. / ax_dx
                c = 1.5 / ax_dx
            else:
                dx1 = ax_dx[-2]  # type: ignore
                dx2 = ax_dx[-1]  # type: ignore
                a = (dx2) / (dx1 * (dx1 + dx2))
                b = - (dx2 + dx1) / (dx1 * dx2)
                c = (2. * dx2 + dx1) / (dx2 * (dx1 + dx2))
            # 1D equivalent -- out[-1] = a * f[-3] + b * f[-2] + c * f[-1]
            out[tuple(slice1)] = np.sqrt((a**2) * (f[tuple(slice2)]**2) + (b**2) * (f[tuple(slice3)]**2) + (c**2) * (f[tuple(slice4)]**2))

        outvals.append(out)

        # reset the slice object in this dimension to ":"
        slice1[axis] = slice(None)
        slice2[axis] = slice(None)
        slice3[axis] = slice(None)
        slice4[axis] = slice(None)

    if len_axes == 1:
        return outvals[0]
    elif np._using_numpy2_behavior():  # type: ignore
        return tuple(outvals)
    else:
        return outvals

