import sys
import os
import csv
import numpy as np
import cv2

if len(sys.argv) != 3:
    print(f'\n{sys.argv[0]} ./book out.ply\n')
    sys.exit(0)

prefix = sys.argv[1]

calib = np.load(os.path.join(prefix, 'calib.npz'))
gt = np.load(os.path.join(prefix, 'gt.npz'))

# Calibration
K = calib['K']
R_W2L = calib['Rmat_W2L']
t_W2L = calib['Tvec_W2L']
R_W2R = calib['Rmat_W2R']
t_W2R = calib['Tvec_W2R']
P_L = K @ np.hstack([R_W2L, t_W2L.reshape((3, 1))])
P_R = K @ np.hstack([R_W2L, t_W2R.reshape((3, 1))])

# GT correspondences
x_R = gt['sl_correspondence_L2R']
x_L = np.dstack([ *np.meshgrid(np.arange(x_R.shape[1]), np.arange(x_R.shape[0])) ])
x_R = x_R[::2, ::2]
x_L = x_L[::2, ::2]

# Valid mask
mask_L = gt['mask_L']

# Triangulation
x_L = x_L[mask_L].T.astype(np.float32)
x_R = x_R[mask_L].T.astype(np.float32)
X = cv2.triangulatePoints(P_L, P_R, x_L, x_R)
X = X[:3, :] / X[3, :]

# GT normal
n_L = gt['ps_normal_L']
n_L = n_L[mask_L]
n_L = n_L / np.linalg.norm(n_L, axis=1)[:,None]
n = R_W2L.T @ n_L.T

# Save as PLY
with open(sys.argv[2], 'w') as fp:
    fp.write('ply\n')
    fp.write('format ascii 1.0\n')
    fp.write(f'element vertex {X.shape[1]}\n')
    fp.write('property float x\n')
    fp.write('property float y\n')
    fp.write('property float z\n')
    fp.write('property float nx\n')
    fp.write('property float ny\n')
    fp.write('property float nz\n')
    fp.write('end_header\n')

    csv.writer(fp, delimiter='\t', lineterminator='\n').writerows(np.hstack([X.T, n.T]))

