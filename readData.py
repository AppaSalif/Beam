import numpy as np

def lire_donnees_tige(chemin_fichier):
    donnees = {}
    
    with open(chemin_fichier, 'r') as f:
        frame_actuelle = None
        
        for ligne in f:
            # Ignorer les commentaires et lignes vides
            if ligne.startswith('#') or not ligne.strip():
                continue
            
            parts = ligne.split()
            
            # Détection d'une nouvelle frame
            if parts[0] == 'FRAME':
                frame_idx = int(parts[1])
                temps = float(parts[3])
                frame_actuelle = {'time': temps, 'nodes': {}}
                donnees[frame_idx] = frame_actuelle
                
            # Lecture des nœuds
            elif parts[0] == 'NODE' and frame_actuelle is not None:
                node_idx = int(parts[1])
                coords = np.array([float(parts[2]), float(parts[3]), float(parts[4])])
                frame_actuelle['nodes'][node_idx] = coords
                
    return donnees

# # Utilisation
# donneesElastica = lire_donnees_tige('donnees_tige.txt')
# print(donneesElastica[1]['time'])

# # Exemple d'accès : afficher la position du nœud 10 à la frame 0
# print(f"Position Nœud 10, Frame 0: {donneesElastica[0]['nodes'][10]}")

# # Exemple pour extraire tous les X de tous les nœuds pour une frame donnée
# frame_test = 0
# x_coords = [donneesElastica[frame_test]['nodes'][i][0] for i in range(len(donneesElastica[frame_test]['nodes']))]
# print(f"Positions X à la frame {frame_test}: {x_coords}")

########## OK super fonctionnel ##########


def lire_monitor_sofa(fichier_sofa, intervalle=100):
    """
    Lit le fichier SOFA et extrait les données en respectant le même intervalle
    que ton save_interval de PyElastica (50).
    """
    data = []
    data.append({'time': 0.0, 'pos': initialiser_position_t0(11)})

    compteur_data = 1
    with open(fichier_sofa, 'r') as f:
        for ligne in f:
            if ligne.startswith('#') or not ligne.strip(): 
                continue
            
            # Ici, on est sûr de traiter une ligne de données
            if compteur_data % intervalle == 0:
                parts = [float(x) for x in ligne.split()]
                temps = parts[0]
                
                # Calcul dynamique du nombre de nœuds
                # Chaque bloc = 7 colonnes (x,y,z,qx,qy,qz,qw)
                # Donc (len(parts) - 1) / 7 = nombre de nœuds
                num_nodes = (len(parts) - 1) // 7
                
                positions = []
                for node_idx in range(num_nodes):
                    base = 1 + node_idx * 7 # 1(temps) + 7 colonnes par bloc
                    positions.append(parts[base:base+3])
                
                data.append({'time': temps, 'pos': np.array(positions)})
            
            compteur_data += 1
            
    return data    

def initialiser_position_t0(nb_nodes):
    nodes = np.linspace(0, 5, nb_nodes)
    pos_t0 = np.array([[x, 0.0, 0.0] for x in nodes])
    return pos_t0    


# # Utilisation
# donneesFrames2Strain = lire_monitor_sofa('monitor_frames2strain_x.txt')
# print(donneesFrames2Strain[1]['time'])