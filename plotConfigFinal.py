import matplotlib.pyplot as plt
import numpy as np

from readData import lire_donnees_tige, lire_monitor_sofa

base_length = 0.5  
nb_section = 200

donneesElastica = lire_donnees_tige("donnees_tige.txt")
donneesFrames2Strain = lire_monitor_sofa("monitor_frames2strain_x.txt", nb_section=nb_section, beam_length=base_length)
donneesStrain2Rigid = lire_monitor_sofa("monitor_strain2rigid_x.txt", nb_section=nb_section, beam_length=base_length)


# Load data
data = np.loadtxt("beam_pos_matlab.txt")

X_az, Y_az, Z_az = data[:, 0], data[:, 1], data[:, 2]

X_elastica = [node[0] for node in donneesElastica[999]['nodes'].values()]
Y_elastica = [node[1] for node in donneesElastica[999]['nodes'].values()]
Z_elastica = [node[2] for node in donneesElastica[999]['nodes'].values()]

pos_s2r = donneesStrain2Rigid[(len(donneesStrain2Rigid)-1)]['pos']

X_s2r = pos_s2r[:, 0]
Y_s2r = pos_s2r[:, 1]
Z_s2r = pos_s2r[:, 2]

pos_f2s = donneesFrames2Strain[(len(donneesFrames2Strain)-1)]['pos']
X_f2s = pos_f2s[:, 0]
Y_f2s = pos_f2s[:, 1]
Z_f2s = pos_f2s[:, 2]


# Plot
# plt.plot(X_az, Z_az, 'g-', linewidth=1.5, label="Az. result (Ref.)")
# plt.plot(X_elastica, Y_elastica, 'b--', label="Elastica result")
plt.plot(X_s2r, Y_s2r, label="S2R result")
plt.plot(X_f2s, Y_f2s, label="F2S result")

plt.xlabel("X")
plt.ylabel("Y")
plt.title(f"Beam Final Configuration (nb_sections = {nb_section})")
plt.grid(True)
plt.legend()
plt.show()


err = (np.sqrt((X_s2r - X_f2s)**2 + (Y_s2r - Y_f2s)**2))/base_length
plt.plot(err)
plt.xlabel("Frames")
plt.ylabel("Error")
plt.title("Error between F2S and S2R -- nb_sections = {}".format(nb_section))
plt.grid(True)
plt.show()


# # calcul d'erreur relative
# err_elastica = (np.sqrt((X_elastica - X_az)**2 + (Y_elastica - Y_az)**2))/base_length
# err_s2r = (np.sqrt((X_s2r - X_az)**2 + (Y_s2r - Y_az)**2))/base_length
# err_f2s = (np.sqrt((X_f2s - X_az)**2 + (Y_f2s - Y_az)**2))/base_length

# print("Mean relative error Elastica:", np.mean(err_elastica))
# print("Mean relative error S2R:", np.mean(err_s2r))
# print("Mean relative error F2S:", np.mean(err_f2s))

# # plt.plot(err_elastica, label="Elastica")
# plt.plot(err_s2r, label="S2R")
# plt.plot(err_f2s, label="F2S")
# plt.xlabel("Frames")
# plt.ylabel("Relative error")
# plt.title("Relative error comparison -- nb_sections = {}".format(nb_section))
# plt.legend()
# plt.grid(True)
# plt.show()