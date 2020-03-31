import numpy as np
from PIL import Image
import sys

from fluid import Fluid

FRAME_PATH = 'placeholder'

RESOLUTION = 700, 700
VISCOSITY = 10 ** -3
DURATION = 200

INFLOW_PADDING = 50
INFLOW_DURATION = 60
INFLOW_RADIUS = 8
INFLOW_VELOCITY = 12


def circle(theta):
    return np.asarray((np.cos(theta), np.sin(theta)))


center = np.floor_divide(RESOLUTION, 2)
r = np.min(center) - INFLOW_PADDING
directions = tuple(-circle(p * np.pi * 2 / 3) for p in range(3))
points = tuple(r * circle(p * np.pi * 2 / 3) + center for p in range(3))

channels = 'r', 'g', 'b'
fluid = Fluid(RESOLUTION, VISCOSITY, channels)

inflow_dye_field = np.zeros((fluid.size, len(channels)))
inflow_velocity_field = np.zeros_like(fluid.velocity_field)
for i, p in enumerate(points):
    distance = np.linalg.norm(fluid.indices - p, axis=1)
    mask = distance <= INFLOW_RADIUS

    for d in range(2):
        inflow_velocity_field[..., d][mask] = directions[i][d] * INFLOW_VELOCITY

    inflow_dye_field[..., i][mask] = 1

for frame in range(DURATION):
    sys.stderr.write(f'Computing frame {frame+1}.\n')
    fluid.advect_diffuse()

    if frame <= INFLOW_DURATION:
        fluid.velocity_field += inflow_velocity_field

        for i, k in enumerate(channels):
            fluid.quantities[k] += inflow_dye_field[..., i]

    fluid.project()

    rgb = np.dstack(tuple(fluid.quantities[c] for c in channels))

    rgb = rgb.reshape((*RESOLUTION, 3))
    rgb = (np.clip(rgb, 0, 1) * 255).astype('uint8')
    frame_as_three_digits = f"{frame+1}".zfill(3)
    Image.fromarray(rgb).save(f'{FRAME_PATH}frame{frame}.png')

