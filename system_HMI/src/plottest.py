import matplotlib.pyplot as plt
from math import exp
import matplotlib.dates as mdates

x = [ii/100 for ii in range(1000)]
y = [exp(-ii) for ii in x]

fig = plt.figure(facecolor='black', figsize=[15, 10], dpi=200)
plt.rcParams.update({'font.size': 22, 'axes.linewidth': 2})
ax = fig.gca()

ax.set_xlabel("Time", loc='right')
ax.set_ylabel("Temp (k)", loc='top')

ax.xaxis.label.set_color("white")
ax.yaxis.label.set_color("white")

ax.tick_params(axis='x', which='both', colors="white")
ax.tick_params(axis='y', which='both', colors='white')


ax.minorticks_on()

ax.spines['left'].set_color('white')
ax.spines['top'].set_color('white')
ax.spines['bottom'].set_color('white')
ax.spines['right'].set_color('white')

ax.set_facecolor('black')

plt.plot(x, y, color='red', linewidth=5, label="PRP")
legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                    fancybox=False, shadow=False, ncol=5, framealpha=0, prop={'size': 32})
for label in legend.get_texts():
    label.set_color("white")
plt.savefig("test.png", transparent=True)
plt.show()
