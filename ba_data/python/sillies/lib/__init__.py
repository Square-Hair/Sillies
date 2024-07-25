from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import bascenev1 as bs
from bascenev1lib.gameutils import SharedObjects

import math

if TYPE_CHECKING:
    from typing import Any, Sequence, Callable

def rotate_direction_vector(vector: Sequence[float], angle_degrees: float) -> Sequence[float]:
    """ Rotate a direction vector by an angle in degrees. """
    angle_radians = angle_degrees * math.pi / 180
    return (vector[0] * math.cos(angle_radians) - vector[2] * math.sin(angle_radians),
            vector[1],
            vector[0] * math.sin(angle_radians) + vector[2] * math.cos(angle_radians))