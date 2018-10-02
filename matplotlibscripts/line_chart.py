#!/usr/bin/python
import matplotlib
from matplotlib import colors
from matplotlib import pyplot as plt
import numpy as np


my_color = {"grey": colors.colorConverter.to_rgb("#4D4D4D"),
            "blue": colors.colorConverter.to_rgb("#5DA5DA"),
            "orange": colors.colorConverter.to_rgb("#FAA43A"),
            "green": colors.colorConverter.to_rgb("#60BD68"),
            "pink": colors.colorConverter.to_rgb("#F17CB0"),
            "brown": colors.colorConverter.to_rgb("#B2912F"),
            "purple": colors.colorConverter.to_rgb("#B276B2"),
            "yellow": colors.colorConverter.to_rgb("#DECF3F"),
            "red": colors.colorConverter.to_rgb("#F15854")}

x = np.array([1,2,4,6])
y1 = 100* np.array([0.228836686644,0.419665948276,0.761744619205,0.875893967662])
y2 = 100* np.array([0.186493844697,0.408907312925,0.727200255102,0.876267997382])
y3 = 100* np.array([0.126460873984,0.23828125,0.533504614094,0.514849330357])
y4 = 100* np.array([0.123676394628,0.251453488372,0.473772321429,0.407894736842])

plt.plot(x, y1, label="GPU - CS", color=my_color["blue"], marker='o')
plt.plot(x, y3, label="GPU - Tetrisched", color=my_color["green"], marker='^')
plt.plot(x, y2, label="MPI - CS", color=my_color["pink"], marker='s')
plt.plot(x, y4, label="MPI - Tetrisched", color=my_color["red"], marker='p')


plt.legend(loc="lower right")
plt.xlim([0,7])
plt.xlabel("Job Arrival Rate (Containers/sec)")
plt.ylabel("Cluster Utilization (%)")

plt.savefig("utilization.pdf")