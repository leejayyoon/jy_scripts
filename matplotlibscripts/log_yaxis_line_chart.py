
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
xl = [1, 2, 4, 6, 8]
x = [1, 2, 4, 6]
xs = [1, 2, 4]

x = [12, 24, 36, 48]
y1 = ([268600, 546700, 820100, 1695210])
y2 = ([42697.6269, 70303.7755, 112231, 154159.4113])
y3 = ([12700, 25400, 38200, 48477])
y4 = ([3100, 6717, 9320, 13305])
# y2x = np.array(15640273.7048, 32010003.1260, 55351351.3514, 69189189.1892)
# y3x = np.array([10427486.2019, 20830790.5122, 38143485.0630, 65565373.2872])
# y2 = np.array([696694.1231, 2781131.335, 9905468.6984, 32230220.92])
fig, ax1 = pyplot.subplots(figsize=(4, 3.5))
ax1.semilogy(x, y1, color=my_color["blue"],
         label='Dimension 4', linewidth=3.0, marker="o")

ax1.semilogy(x, y2, color=my_color["orange"],
         label='Dimension 8', linewidth=3.0, marker="^")

ax1.semilogy(x, y3, color=my_color["green"],
         label='Dimension 12', linewidth=3.0, marker="s")

ax1.semilogy(x, y4, color=my_color["pink"],
         label='Dimension 16', linewidth=3.0, marker="o")

lines, labels = ax1.get_legend_handles_labels()
ax1.set_xlabel("# Client Nodes", fontsize=19)
ax1.set_ylabel("Query Rate (op/s)", fontsize=19)
#ax1.legend(lines, labels, loc="upper left", fontsize=12)
ax1.set_xlim([10, 50])
#ax1.set_ylim([5, 16])
#ax1.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
ax1.yaxis.grid(True)

pyplot.tight_layout()
#pyplot.savefig("ingestion.eps")
pyplot.savefig("../figures/dimension_query.pdf")
