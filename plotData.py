import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from readData import lire_donnees_tige, lire_monitor_sofa

base_length = 0.5  
nb_section = 10

donneesElastica = lire_donnees_tige("donnees_tige.txt")
donneesFrames2Strain = lire_monitor_sofa("monitor_frames2strain_x.txt", nb_section=nb_section, beam_length=base_length)
donneesStrain2Rigid = lire_monitor_sofa("monitor_strain2rigid_x.txt", nb_section=nb_section, beam_length=base_length)

times = [d['time'] for d in donneesFrames2Strain]



fig, ax = plt.subplots(figsize=(10, 6))
ax.set_xlim(-0.5, base_length + 0.5)
ax.set_ylim(-base_length -0.5, 1.0)
ax.set_xlabel('Position X (m)')
ax.set_ylabel('Position Y (m)')
ax.set_aspect('equal')
ax.grid(True)


# Lignes pour les tiges
line_pye, = ax.plot([], [], 'b-', linewidth=3, label='PyElastica (Référence)')
line_f2s, = ax.plot([], [], 'g--', linewidth=3, label='SOFA (Frames2Strain)')
line_s2r, = ax.plot([], [], 'r--', linewidth=3, label='SOFA (Strain2Rigid)')

time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

ax.legend()


def animate(frame_idx):
    # Ici on accède aux positions de la frame frame_idx

    if frame_idx >= len(donneesElastica) or frame_idx >= len(donneesFrames2Strain) or frame_idx >=len(donneesStrain2Rigid):
        return line_pye, line_f2s, line_s2r


    n_nodes_pye = len(donneesElastica[frame_idx]['nodes'])
    pos_pye = np.array([donneesElastica[frame_idx]['nodes'][i] for i in range(n_nodes_pye)])
    line_pye.set_data(pos_pye[:, 0], pos_pye[:, 1])

    # SOFA
    pos_f2s = donneesFrames2Strain[frame_idx]['pos']
    line_f2s.set_data(pos_f2s[:, 0], pos_f2s[:, 1])

    pos_s2r = donneesStrain2Rigid[frame_idx]['pos']
    line_s2r.set_data(pos_s2r[:, 0], pos_s2r[:, 1])

    time_text.set_text(f'Temps: {times[frame_idx]:.2f}s')
    return line_pye, line_f2s, line_s2r, time_text


anim = FuncAnimation(fig, animate, frames=len(times), interval=40, blit=True)

plt.show()

