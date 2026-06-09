import numpy as np
import matplotlib.pyplot as plt

from readData import lire_donnees_tige, lire_monitor_sofa

donneesElastica  = lire_donnees_tige("donnees_tige.txt")
donneesFrames2Strain = lire_monitor_sofa("monitor_frames2strain_x.txt")
donneesStrain2Rigid = lire_monitor_sofa("monitor_strain2rigid_x.txt")

base_length = 5.0  

times = [d['time'] for d in donneesFrames2Strain]

# def calculer_erreur_moyenne(donnees1, donnees2):
#     erreurs = []
#     for i in range(len(times)):
#         if i >= len(donneesElastica) or i >= len(donneesFrames2Strain) or i >=len(donneesStrain2Rigid):
#             return erreurs

#         pos1 = np.array([donnees1[i]['nodes'][n] for n in range(11)])
#         pos2 = donnees2[i]['pos']
#         # Calcul de la distance euclidienne moyenne entre les nœuds à l'instant t
#         mse = np.mean(np.linalg.norm(pos1 - pos2, axis=1))
#         erreurs.append(mse)
#     return erreurs

# erreurs = calculer_erreur_moyenne(donneesElastica, donneesFrames2Strain)
# plt.plot(times[:-1], erreurs)
# plt.title("Erreur de position Frames2Strain vs PyElastica")
# plt.ylabel("Erreur moyenne")
# plt.xlabel("Temps")
# plt.grid()
# plt.show()


# erreurs2 = calculer_erreur_moyenne(donneesElastica, donneesStrain2Rigid)
# plt.plot(times[:-1], erreurs2)
# plt.title("Erreur de position Strain2Rigid vs PyElastica")
# plt.ylabel("Erreur moyenne")
# plt.xlabel("Temps")
# plt.grid()
# plt.show()


# def calculer_erreur_moyenne_sofa(donnees1, donnees2):
#     erreurs = []
#     for i in range(len(times)):
#         if i >= len(donneesFrames2Strain) or i >=len(donneesStrain2Rigid):
#             return erreurs

#         pos1 = donnees1[i]['pos']
#         pos2 = donnees2[i]['pos']
#         # Calcul de la distance euclidienne moyenne entre les nœuds à l'instant t
#         mse = np.mean(np.linalg.norm(pos1 - pos2, axis=1))
#         erreurs.append(mse)
#     return erreurs


# erreurs3 = calculer_erreur_moyenne_sofa(donneesFrames2Strain, donneesStrain2Rigid)
# plt.plot(times, erreurs3)
# plt.title("Erreur de position Strain2Rigid vs Frames2Strain")
# plt.ylabel("Erreur moyenne")
# plt.xlabel("Temps")
# plt.grid()
# plt.show()    


def calculer_erreur_normalisee(donnees1, donnees2):
    erreurs = []
    for i in range(len(times)):
        if i >= len(donneesElastica) or i >= len(donneesFrames2Strain) or i >=len(donneesStrain2Rigid):
            return erreurs

        pos1 = np.array([donnees1[i]['nodes'][n] for n in range(11)])
        pos2 = donnees2[i]['pos']
        # Calcul de la distance euclidienne moyenne entre les nœuds à l'instant t
        mse = np.linalg.norm(pos1 - pos2, axis=1)/ base_length
        erreurs.append(np.max(mse))
    return erreurs

erreurs = calculer_erreur_normalisee(donneesElastica, donneesFrames2Strain)
    
plt.plot(times[:-1], erreurs)
plt.title("Erreur de position Frames2Strain vs PyElastica")
plt.ylabel("Erreur normalisée")
plt.xlabel("Temps")
plt.grid()
plt.show()    

print(f"A l'équilibre l'erreur normalisée entre PyElastica et Frames2Strain est de {erreurs[-1]:.5f}")

erreurs2 = calculer_erreur_normalisee(donneesElastica, donneesStrain2Rigid)
plt.plot(times[:-1], erreurs2)
plt.title("Erreur de position Strain2Rigid vs PyElastica")
plt.ylabel("Erreur normalisée")
plt.xlabel("Temps")
plt.grid()
plt.show()


print(f"A l'équilibre l'erreur normalisée entre PyElastica et Strain2Rigid est de {erreurs2[-1]:.5f}")


def calculer_erreur_normalisee_sofa(donnees1, donnees2):
    erreurs = []
    for i in range(len(times)):
        if i >= len(donneesFrames2Strain) or i >=len(donneesStrain2Rigid):
            return erreurs

        pos1 = donnees1[i]['pos']
        pos2 = donnees2[i]['pos']
        # Calcul de la distance euclidienne moyenne entre les nœuds à l'instant t
        err = np.linalg.norm(pos1 - pos2, axis=1)/base_length
        erreurs.append(np.max(err))
    return erreurs

erreurs3 = calculer_erreur_normalisee_sofa(donneesFrames2Strain, donneesStrain2Rigid)
plt.plot(times, erreurs3)
plt.title("Erreur de position Strain2Rigid vs Frames2Strain")
plt.ylabel("Erreur normalisée")
plt.xlabel("Temps")
plt.grid()
plt.show()    

print(f"A l'équilibre l'erreur normalisée entre Frames2Strain et Strain2Rigid est de {erreurs3[-1]:.5f}")
