import numpy as np
import math
import torch
from waveprop.util import sample_points
from waveprop.pytorch_util import fftconvolve as fftconvolve_torch
from scipy.signal import fftconvolve
from waveprop.rs import _get_dtypes


def spherical_prop(u_in, d1=None, wv=None, dz=None, return_psf=False, psf=None, dtype=None):
    """

    Similar to: https://github.com/vsitzmann/deepoptics/blob/defbb975309a6a3f3d2a86b92e82d02156ab213e/src/layers/optics.py#L1010

    Parameters
    ----------
    u_in
    d1
    wv
    dz
    return_psf
    psf
    dtype

    Returns
    -------

    """

    if torch.is_tensor(u_in):
        is_torch = True
    else:
        is_torch = False
    if dtype is None:
        dtype = u_in.dtype
    ctype, ctype_np = _get_dtypes(dtype, is_torch)

    if psf is None:
        assert d1 is not None
        assert wv is not None
        assert dz is not None

        x1, y1 = sample_points(N=u_in.shape[:2], delta=d1)
        k = 2 * math.pi / wv
        curvature = np.sqrt(x1 ** 2 + y1 ** 2 + dz ** 2)
        psf = np.exp(1j * k * curvature).astype(ctype_np)
        # if intensity:
        #     psf = np.abs(psf) ** 2
        if is_torch:
            psf = torch.tensor(psf, dtype=ctype, device=u_in.device)

    if return_psf:
        return psf
    if is_torch:
        return fftconvolve_torch(u_in, psf)
    else:
        return fftconvolve(u_in, psf, mode="same")