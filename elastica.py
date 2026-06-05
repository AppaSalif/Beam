import sys
import os

# Ajoutez le chemin absolu vers PyElastica
sys.path.insert(0, os.path.expanduser('~/PyElastica'))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from elastica import *
from elastica.timestepper import integrate

class HorizontalRodSimulator(BaseSystemCollection, Constraints, Forcing, Damping, CallBacks):
    pass


# Créer le simulateur
rod_sim = HorizontalRodSimulator()

# Vos paramètres spécifiques
n_elements = 20  # nombre de sections
base_length = 3.0  # longueur totale de 3 mètres
base_radius = 0.3  # rayon de 0.3 mètre
total_mass = 0.5  # masse totale de 0.5 kg
youngs_modulus = 1e4  # module d'Young de 10000 Pa
poisson_ratio = 0.38  # coefficient de Poisson

# Calcul de la densité volumique à partir de la masse et du volume
# Volume = π * r² * L (cylindre)
volume = np.pi * base_radius**2 * base_length
density = total_mass / volume  # masse volumique en kg/m³

# Calcul du module de cisaillement à partir du module d'Young et du coefficient de Poisson
shear_modulus = youngs_modulus / (2.0 * (1.0 + poisson_ratio))

print(f"Densité calculée: {density:.3f} kg/m³")
print(f"Volume de la tige: {volume:.3f} m³")
print(f"Module de cisaillement: {shear_modulus:.2f} Pa")

# Direction horizontale (axe x)
direction = np.array([1.0, 0.0, 0.0])
normal = np.array([0.0, 1.0, 0.0])

# Créer la tige avec vos paramètres
rod = CosseratRod.straight_rod(
    n_elements=n_elements,
    start=np.array([0.0, 0.0, 0.0]),
    direction=direction,
    normal=normal,
    base_length=base_length,
    base_radius=base_radius,
    density=density,
    youngs_modulus=youngs_modulus,
    shear_modulus=shear_modulus
)

# Ajouter la tige au simulateur
rod_sim.append(rod)
print(f"Tige créée avec {n_elements} éléments")


# Ajouter la gravité (vers le bas)
gravity_acc = np.array([0.0, -9.81, 0.0])
rod_sim.add_forcing_to(rod).using(
    GravityForces,
    acc_gravity=gravity_acc
)

# Conditions aux limites - tige encastrée à une extrémité (cantilever)
rod_sim.constrain(rod).using(
    OneEndFixedBC,
    constrained_position_idx=(0,),
    constrained_director_idx=(0,)
)

# Ajouter un amortissement pour la stabilité numérique
damping_constant = 0.3
rod_sim.dampen(rod).using(
    AnalyticalLinearDamper,
    uniform_damping_constant=damping_constant,
    time_step=1e-4
)

rod_sim.finalize()

# Configuration temporelle
final_time = 10.0  # secondes
time_step = 1e-4
total_steps = int(final_time / time_step)

# Créer le timestepper
timestepper = PositionVerlet()
do_step, stages_and_updates = extend_stepper_interface(timestepper, rod_sim)

# Sauvegarde des frames pour l'animation
save_interval = 200  # Sauvegarder tous les 200 pas de calcul

print(f"Simulation démarrée: {total_steps} pas de temps")
print(f"Durée: {final_time} secondes, dt: {time_step}")

# Stockage des positions de tous les nœuds à chaque frame
all_positions = []  # Liste de matrices de positions
times_saved = []

# Boucle de simulation
for step in range(total_steps):
    time = step * time_step
    
    if step % save_interval == 0:
        # Sauvegarder toutes les positions des nœuds
        # rod.position_collection a la forme (3, n_elements+1) ou (3, n_elements)
        positions = rod.position_collection.copy()
        all_positions.append(positions)
        times_saved.append(time)
        

    do_step(timestepper, stages_and_updates, rod_sim, time, time_step)

print(f"Simulation terminée! {len(all_positions)} frames sauvegardées")


# Conversion en array numpy
all_positions = np.array(all_positions)  # Shape: (n_frames, 3, n_nodes)
times_saved = np.array(times_saved)

print(f"Shape des positions: {all_positions.shape}")

# ============================================
# CRÉATION DE L'ANIMATION
# ============================================

# Configuration du plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Dynamique de la tige élastique', fontsize=14)

# RECADRAGE DE LA CAMÉRA (On cadre là où la tige va tomber !)
ax1.set_xlim(-0.5, base_length + 0.5)
ax1.set_ylim(-base_length - 0.5, 1) # la tige part de 0 et peut pendre verticalement jusqu' -base_length
ax1.set_xlabel('Position X (m)')
ax1.set_ylabel('Position Y (m)')
ax1.set_title('Mouvement de la tige')
ax1.grid(True, alpha=0.3)
ax1.set_aspect('equal')

# RECADRAGE DU GRAPH DE LA TRAJECTOIRE
ax2.set_xlim(0, final_time)
ax2.set_ylim(-base_length - 0.5, 1.0)
ax2.set_xlabel('Temps (s)')
ax2.set_ylabel('Position Y du centre (m)')
ax2.set_title('Évolution temporelle du centre de masse')
ax2.grid(True, alpha=0.3)

# Éléments graphiques
# Pour la tige (reliant les nœuds)
line_tige, = ax1.plot([], [], 'b-', linewidth=3, label='Tige')
points_tige, = ax1.plot([], [], 'ro', markersize=5, label='Nœuds')
time_text = ax1.text(0.02, 0.95, '', transform=ax1.transAxes, verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

trajectoire_centre, = ax2.plot([], [], 'g-', linewidth=2)
trace_temps, = ax2.plot([], [], 'go', markersize=8)

centres_y = np.array([np.mean(pos[1, :]) for pos in all_positions])

def init():
    line_tige.set_data([], [])
    points_tige.set_data([], [])
    time_text.set_text('')
    trajectoire_centre.set_data([], [])
    trace_temps.set_data([], [])
    return line_tige, points_tige, time_text, trajectoire_centre, trace_temps

def animate(frame):
    positions = all_positions[frame]
    time = times_saved[frame]
    
    x_nodes = positions[0, :]
    y_nodes = positions[1, :]
    
    line_tige.set_data(x_nodes, y_nodes)
    points_tige.set_data(x_nodes, y_nodes)
    
    time_text.set_text(f'Temps: {time:.2f}s')
    
    y_centre = np.mean(y_nodes)
    trajectoire_centre.set_data(times_saved[:frame+1], centres_y[:frame+1])
    trace_temps.set_data([time], [y_centre])
    
    return line_tige, points_tige, time_text, trajectoire_centre, trace_temps

print("Génération du GIF...")
anim = FuncAnimation(fig, animate, init_func=init, frames=len(times_saved), interval=40, blit=True)
anim.save('tige_elastique.gif', writer=PillowWriter(fps=25))
print("Terminé ! Fichier enregistré sous 'tige_elastique.gif'")
plt.show()

print("Terminé!")