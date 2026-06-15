import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from readData import lire_donnees_tige, lire_monitor_sofa

nb_section = 10
beam_length = 1

donneesElastica = lire_donnees_tige("donnees_tige.txt")
donneesFrames2Strain = lire_monitor_sofa("monitor_frames2strain_x.txt", length=beam_length, nb_section=nb_section)
donneesStrain2Rigid = lire_monitor_sofa("monitor_strain2rigid_x.txt", length=beam_length, nb_section=nb_section)


donneesAz = np.loadtxt("beam_pos_matlab.txt", skiprows=0) 

X_az = donneesAz[:, 0]
Y_az = donneesAz[:, 1]
Z_az = donneesAz[:, 2]

n_nodes_elastica = len(donneesElastica[0]['nodes'])

X_elastica = []
Y_elastica = []
Z_elastica = []

for i in range(n_nodes_elastica):
    X_elastica.append(donneesElastica[1999]['nodes'][i][0])
    Y_elastica.append(donneesElastica[1999]['nodes'][i][1])
    Z_elastica.append(donneesElastica[1999]['nodes'][i][2])


X_s2r = []
Y_s2r = []
Z_s2r = []

for i in range(len(donneesStrain2Rigid[-1]['pos'])):
    X_s2r.append(donneesStrain2Rigid[-1]['pos'][i][0])
    Y_s2r.append(donneesStrain2Rigid[-1]['pos'][i][1])
    Z_s2r.append(donneesStrain2Rigid[-1]['pos'][i][2])


X_f2s = []
Y_f2s = []
Z_f2s = []

for i in range(len(donneesFrames2Strain[-1]['pos'])):
    X_f2s.append(donneesFrames2Strain[-1]['pos'][i][0])
    Y_f2s.append(donneesFrames2Strain[-1]['pos'][i][1])
    Z_f2s.append(donneesFrames2Strain[-1]['pos'][i][2])


plt.plot(X_f2s, Y_f2s, 'r--', label='Frames2Strain result')
plt.plot(X_s2r, Y_s2r, 'b--', label='Strain2Rigid result')
plt.plot(X_elastica, Y_elastica, 'g-', linewidth=0.75, label='Elastica result')
plt.plot(X_az, Z_az, 'm--', linewidth=0.75, label='Az. result')
plt.xlabel('X')
plt.ylabel('Z')
plt.legend()
plt.grid(True)
plt.show()


### Calcul d'erreur de tous les résultats comparé à la solution d'Azouaou

err_f2s = (np.sqrt((np.array(X_f2s) - np.array(X_az))**2 + (np.array(Y_f2s) - np.array(Y_az))**2 + (np.array(Z_f2s) - np.array(Z_az))**2))/beam_length
err_s2r = (np.sqrt((np.array(X_s2r) - np.array(X_az))**2 + (np.array(Y_s2r) - np.array(Y_az))**2 + (np.array(Z_s2r) - np.array(Z_az))**2))/beam_length
err_elastica = (np.sqrt((np.array(X_elastica) - np.array(X_az))**2 + (np.array(Y_elastica) - np.array(Y_az))**2 + (np.array(Z_elastica) - np.array(Z_az))**2))/beam_length

plt.plot(err_f2s, label='Frames2Strain')
plt.plot(err_s2r, label='Strain2Rigid')
plt.plot(err_elastica, label='Elastica')
plt.legend()
plt.xlabel('Node index')
plt.ylabel('Error (normalized by beam length)')
plt.grid(True)
plt.show()

err_rel_f2s = np.mean(err_f2s) *100
err_rel_s2r = np.mean(err_s2r) *100
err_rel_elastica = np.mean(err_elastica) *100

print("Erreur relative Frames2Strain: ", err_rel_f2s)
print("Erreur relative Strain2Rigid: ", err_rel_s2r)
print("Erreur relative Elastica: ", err_rel_elastica)