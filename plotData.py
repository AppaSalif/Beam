import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button

from readData import lire_donnees_tige, lire_monitor_sofa

donneesElastica = lire_donnees_tige("donnees_tige.txt")
donneesFrames2Strain = lire_monitor_sofa("monitor_frames2strain_x.txt")
donneesStrain2Rigid = lire_monitor_sofa("monitor_strain2rigid_x.txt")

times = [d['time'] for d in donneesFrames2Strain]

fig, ax = plt.subplots(figsize=(10, 6))
fig.subplots_adjust(bottom=0.2) # On laisse de l'espace en bas pour le bouton
ax.set_aspect('equal')
ax.grid(True)

# Lignes pour les tiges
line_pye, = ax.plot([], [], 'b-', linewidth=3, label='PyElastica (Référence)')
line_f2s, = ax.plot([], [], 'g--', linewidth=3, label='SOFA (Frames2Strain)')
line_s2r, = ax.plot([], [], 'r--', linewidth=3, label='SOFA (Strain2Rigid)')

ax.legend()

# --- PLAY/PAUSE ---
class Callback:
    def __init__(self, anim):
        self.anim = anim
        self.running = True

    def pause(self, event):
        if self.running:
            self.anim.event_source.stop()
        else:
            self.anim.event_source.start()
        self.running = not self.running

# Placement du bouton
ax_button = plt.axes([0.8, 0.05, 0.1, 0.075])
btn = Button(ax_button, 'Play/Pause')


def animate(frame_idx):
    # Ici on accède aux positions de la frame frame_idx

    if frame_idx >= len(donneesElastica) or frame_idx >= len(donneesFrames2Strain) or frame_idx >=len(donneesStrain2Rigid):
        return line_pye, line_f2s, line_s2r

    # 1. Mise à jour des lignes
    n_nodes_pye = len(donneesElastica[frame_idx]['nodes'])
    pos_pye = np.array([donneesElastica[frame_idx]['nodes'][i] for i in range(n_nodes_pye)])
    line_pye.set_data(pos_pye[:, 0], pos_pye[:, 1])
    
    # SOFA
    pos_f2s = donneesFrames2Strain[frame_idx]['pos']
    line_f2s.set_data(pos_f2s[:, 0], pos_f2s[:, 1])

    pos_s2r = donneesStrain2Rigid[frame_idx]['pos']
    line_s2r.set_data(pos_s2r[:, 0], pos_s2r[:, 1])

    # 2. Cadrage dynamique basé sur la tige de référence (PyElastica)
    # Calcul des min/max avec une marge de 0.5 unité
    margin = 0.5
    x_min, x_max = np.min(pos_pye[:, 0]) - margin, np.max(pos_pye[:, 0]) + margin
    y_min, y_max = np.min(pos_pye[:, 1]) - margin, np.max(pos_pye[:, 1]) + margin
    
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    return line_pye, line_f2s, line_s2r

anim = FuncAnimation(fig, animate, frames=len(times), interval=40, blit=False)

callback = Callback(anim)
btn.on_clicked(callback.pause)
plt.show()