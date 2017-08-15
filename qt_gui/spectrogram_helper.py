from typing import List, Tuple
import numpy as np
from PyQt5.QtGui import QPolygonF


def get_sample_data(samples: List[Tuple[int, int]]):
    first_channel_ydata = map(lambda x: x[0], samples)
    second_channel_ydata = map(lambda x: x[1], samples)


def series_to_polyline(xdata, ydata):
    """Convert series data to QPolygon(F) polyline"""
    size = len(xdata)
    polyline = QPolygonF(size)
    pointer = polyline.data()
    dtype, tinfo = np.float, np.finfo  # integers: = np.int, np.iinfo
    pointer.setsize(2*polyline.size()*tinfo(dtype).dtype.itemsize)
    memory = np.frombuffer(pointer, dtype)
    memory[:(size-1)*2+1:2] = xdata
    memory[1:(size-1)*2+2:2] = ydata
    return polyline

