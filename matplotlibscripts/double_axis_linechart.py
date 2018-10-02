#!/usr/bin/python
import matplotlib
from matplotlib import colors
from matplotlib import pyplot
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

#pyplot.savefig("ingestion.eps")

fig, ax1 = pyplot.subplots(figsize=(8,4))
x = np.array([2, 3, 4, 5, 6, 8])
y1 = np.array([938.24, 692.08, 526.49, 430.41, 367.94, 276.21])
ax1.plot(x, y1, color=my_color["blue"], label="Average Memory", linewidth=2.0, marker="o")
ax1.set_xlabel("# Server Nodes", fontsize=20)
ax1.set_xlim(1, 9)
ax1.set_ylim([200, 1200])
# Make the y-axis label and tick labels match the line color.
ax1.set_ylabel("Average Memory (MB)", fontsize=20)
ax1.yaxis.grid(True)

ax2 = ax1.twinx()
y2 = np.array([1890.62, 2076.24, 2105.76, 2152.06, 2207.61, 2209.74])
ax2.plot(x, y2, color=my_color["green"], label="Aggregate Memory", linewidth=2.0, marker="^")
ax2.set_ylabel("Aggregate Memory (MB)", fontsize=20)
ax2.set_xlim(1, 9)
ax2.set_ylim([1800, 2400])
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
fig.legend(lines+lines2, labels + labels2, loc="upper center")


#pyplot.show()

pyplot.tight_layout()
pyplot.savefig("../figures/memory.pdf")
#pyplot.show()