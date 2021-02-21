import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator


temps = [0, 10, 20, 30, 40, 50]
oat0_gr = [365, 390, 415, 440, 470, 505, 540, 580, 635, 695, 765]
oat10_gr = [385, 410, 440, 470, 500, 535, 585, 640, 700, 770, 850]
oat20_gr = [410, 435, 465, 500, 540, 585, 640, 700, 770, 850, 910]
oat30_gr = [430, 465, 500, 540, 590, 640, 700, 765, 845, 915, 995]

oat40_gr = [460, 500, 540, 580, 630, 685, 750, 820, 900, 990]
oat50_gr = [495, 535, 575, 625, 680]

oat40_gr.extend([np.nan] * (len(oat0_gr) - len(oat40_gr)))
oat50_gr.extend([np.nan] * (len(oat0_gr) - len(oat50_gr)))

ISA_gr = [397, 418, 439, 463, 490, 519, 549, 585, 628, 674, 729]
PA = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]


sns.set_style("whitegrid")

fig, ax = plt.subplots(1, 1, figsize=(15, 8))

sns.lineplot(x=ISA_gr, y=PA, label="ISA")
for t in temps:
    t_curve = f"oat{t}_gr"
    label = f"{t}° C"
    sns.lineplot(x=locals()[t_curve], y=PA, label=label)


ax.yaxis.set_major_locator(MultipleLocator(500))
ax.xaxis.set_major_locator(MultipleLocator(20))

plt.suptitle("DA40NG", y=1.02, size=20, fontweight="bold")
plt.title("Ground Roll\n1310 kg", size=16, y=1.03, x=0.485)
plt.ylabel("Pressure Altitude (ft)")
plt.xlabel("Distance (m)")

plt.show()
