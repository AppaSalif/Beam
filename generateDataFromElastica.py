import sys
import os
sys.path.insert(0, os.path.expanduser('~/PyElastica'))


import numpy as np
from elastica import *
from elastica.timestepper import integrate
from scipy.spatial.transform import Rotation as R  # Pour la conversion en quaternions


class HorizontalRodSimulator(BaseSystemCollection, Constraints, Forcing, Damping, CallBacks):
    pass

# ============================================
# CONFIGURATION DU SIMULATEUR
# ============================================
rod_sim = HorizontalRodSimulator()

n_elements = 7 
base_length = 5.0  
base_radius = 0.3  
total_mass = 0.5  
youngs_modulus = 1e3
poisson_ratio = 0.38  

volume = np.pi * base_radius**2 * base_length
density = total_mass / volume  
shear_modulus = youngs_modulus / (2.0 * (1.0 + poisson_ratio))

# Créer la tige
rod = CosseratRod.straight_rod(
    n_elements=n_elements,
    start=np.array([0.0, 0.0, 0.0]),
    direction=np.array([1.0, 0.0, 0.0]),
    normal=np.array([0.0, 1.0, 0.0]),
    base_length=base_length,
    base_radius=base_radius,
    density=density,
    youngs_modulus=youngs_modulus,
    shear_modulus=shear_modulus
)
rod_sim.append(rod)

# Forces, limites et amortissement
rod_sim.add_forcing_to(rod).using(GravityForces, acc_gravity=np.array([0.0, -9.81, 0.0]))
rod_sim.constrain(rod).using(OneEndFixedBC, constrained_position_idx=(0,), constrained_director_idx=(0,))
rod_sim.dampen(rod).using(AnalyticalLinearDamper, uniform_damping_constant=10.0, time_step=1e-4)

rod_sim.finalize()

# Configuration temporelle
final_time = 20.0  
time_step = 1e-3
total_steps = int(final_time / time_step)

timestepper = PositionVerlet()
do_step, stages_and_updates = extend_stepper_interface(timestepper, rod_sim)

save_interval = 100  

# ============================================
# BOUCLE DE SIMULATION ET EXPORT TEXTE
# ============================================
nom_fichier = "donnees_tige.txt"
print(f"Simulation démarrée. Écriture dans : {nom_fichier}...")

with open(nom_fichier, "w") as f:
    # Écriture de l'en-tête pour s'y retrouver
    f.write("# Fichier de données PyElastica pour couplage/test SOFA\n")
    f.write(f"# n_elements = {n_elements} (n_nodes = {n_elements + 1})\n")
    f.write("# Format par frame :\n")
    f.write("# FRAME [num_frame] TIME [temps]\n")
    f.write("# NODE [idx] x y z\n")
    f.write("# ELEM [idx] qw qx qy qz\n")
    f.write("# --------------------------------------------------------\n")

    frame_count = 0

    for step in range(total_steps):
        time = step * time_step
        
        if step % save_interval == 0:
            f.write(f"FRAME {frame_count} TIME {time:.4f}\n")
            
            # 1. Sauvegarde des POSITIONS (définies aux Noeuds : n_elements + 1)
            positions = rod.position_collection # Shape (3, n_nodes)
            for i in range(positions.shape[1]):
                f.write(f"NODE {i} {positions[0, i]:.6f} {positions[1, i]:.6f} {positions[2, i]:.6f}\n")
            
            # 2. Sauvegarde des ORIENTATIONS (définies aux Éléments : n_elements)
            # PyElastica stocke des matrices de rotation 3x3 pour chaque élément
            directors = rod.director_collection # Shape (3, 3, n_elements)
            for e in range(directors.shape[2]):
                matrice_rotation = directors[:, :, e]
                
                # Conversion de la matrice 3x3 en Quaternion (Scipy utilise le format x, y, z, w)
                r = R.from_matrix(matrice_rotation)
                quat = r.as_quat() 
                
                # Réorganisation au format standard (w, x, y, z) souvent préféré en physique/SOFA
                qw, qx, qy, qz = quat[3], quat[0], quat[1], quat[2]
                
                f.write(f"ELEM {e} {qw:.6f} {qx:.6f} {qy:.6f} {qz:.6f}\n")
            
            frame_count += 1
            
            if frame_count % 100 == 0:
                print(f"Progression : {step / total_steps * 100:.1f}% ({frame_count} frames écrites)")

        # Pas de simulation
        do_step(timestepper, stages_and_updates, rod_sim, time, time_step)

print(f"\nTerminé ! {frame_count} frames ont été exportées avec succès.")