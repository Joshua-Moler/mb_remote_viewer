import matplotlib.pyplot as plt
import sqlite3


def newPlot():

    dbConnection = sqlite3.connect("logs.db")
    dbCursor = dbConnection.cursor()
    try:
        plotTimes = [time[0]
                     for time in dbCursor.execute("SELECT timestamp FROM datalog1")]
        temperatureData = {}
        temperatureData['PRP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT PRP FROM datalog1")]
        temperatureData['RGP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT RGP FROM datalog1")]
        temperatureData['CFP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT CFP FROM datalog1")]
        temperatureData['STP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT STP FROM datalog1")]
        temperatureData['ICP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT ICP FROM datalog1")]
        temperatureData['MXP'] = [temp[0]
                                  for temp in dbCursor.execute("SELECT MXP FROM datalog1")]
    except:
        return

    fig = plt.figure(facecolor='black', figsize=[15, 10], dpi=200)
    plt.rcParams.update({'font.size': 22, 'axes.linewidth': 2})
    ax = fig.gca()

    ax.set_xlabel("Time", loc='left')
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

    for plate in temperatureData:
        plt.plot(plotTimes, temperatureData[plate], label=plate)
    legend = plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
                        fancybox=False, shadow=False, ncol=5, framealpha=0, prop={'size': 32})
    for label in legend.get_texts():
        label.set_color("white")
    plt.savefig("test.png", transparent=True, bbox_inches='tight')


if __name__ == '__main__':
    newPlot()
