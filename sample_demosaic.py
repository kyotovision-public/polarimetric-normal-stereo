import numpy as np
import cv2
import sys

class PBayer:
    """
    Polarimetric bayer image. Each pixel has a Stokes vector.
    """

    def __init__(self, raw, demosaic_method=cv2.COLOR_BAYER_BG2BGR_EA):
        assert raw.dtype == np.float32
        assert np.max(raw) <= 1
        assert np.min(raw) >= 0

        self.raw = raw.copy()

        p090 = self.raw[0::2, 0::2] # | 
        p045 = self.raw[0::2, 1::2] # / 
        p135 = self.raw[1::2, 0::2] # \ 
        p000 = self.raw[1::2, 1::2] # - 

        s0 = (p000 + p090 + p045 + p135)/2
        s1 = p000 - p090
        s2 = p045 - p135

        # Stokes vector HxWx3
        self.svec = np.dstack([s0, s1, s2])
        # Filter angles 4
        self.filt = np.array([0, np.pi/4, np.pi/2, np.pi/4*3])
        # Polarized images HxWx4
        self.fimg = np.dstack([p000, p045, p090, p135])

        assert self.svec.shape == (self.raw.shape[0]//2, self.raw.shape[1]//2, 3)
        assert self.fimg.shape == (self.raw.shape[0]//2, self.raw.shape[1]//2, 4)

        self.I_dc = s0 / 2
        self.DoLP = np.clip(np.sqrt(s1**2 + s2**2) / (s0 + 1e-9), 0, 1)
        self.AoLP = np.arctan2(s2, s1) / 2

        self.I_max = self.I_dc + self.DoLP * self.I_dc
        self.I_min = self.I_dc - self.DoLP * self.I_dc

        self.I_min_bgr = cv2.cvtColor((self.I_min * 255).astype(np.uint8), demosaic_method)

        assert self.raw.shape[0] == self.I_min_bgr.shape[0] * 2
        assert self.raw.shape[1] == self.I_min_bgr.shape[1] * 2

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f'\n{sys.argv[0]} book/img_L1_L.png out.bmp\n')
        sys.exit(0)

    # load and normalize to [0:1]
    img = cv2.imread(sys.argv[1], cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0

    # decode
    p = PBayer(img)

    # to 8-bit
    out = np.clip(p.I_min_bgr, 0, 255).astype(np.uint8)

    # save
    cv2.imwrite(sys.argv[2], out)

