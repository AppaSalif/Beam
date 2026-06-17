"""
Validation statique d'un modèle de tige de Cosserat
===================================================

Resolution du problème aux limites de l'elastica plane:
tige inextensible, sans shear, encastrée en s=0, libre en s=L,
soumise a une force et/ou un moment à l'extrémité libre (et eventuellement 
une charge repartie comme la gravite).

Equations (variables d'etat Y = [x, u, theta, Nx, Ny, M]):

    x'(s) = cos(theta)
    y'(s) = sin(theta)
    theta'(s) = M/EI
    Nx'(s) = -fx(s)
    Ny'(s) = -fy(s)
    M'(s) = sin(theta)*Nx - cos(theta)*Ny

Cdts aux limites:
    s = 0: x(0) = 0, y(0) = 0, theta(0) = 0         (encastrement)
    s = L: Nx(L) = Fx_tip, Ny(L) = Fy_tip, M(L) = M_tip         (force et moment appliqués à l'extrémité)

Cette formulation est la même que celle utilisee dans la plupart des modeles
de tige de Cosserat "Kirchoff" (sans cisallement, ni extension)
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_bvp

from readData import lire_donnees_tige, lire_monitor_sofa

nb_section = 10

L = 1.0                       # longueur [m]
radius = 0.01                 # rayon section circulaire [m]
E = 1.0e6                      # module de Young [Pa]
I = np.pi * radius**4 / 4.0    # moment d'inertie de section [m^4]
EI = E * I
 
# # print(f"EI = {EI:.6e} N.m^2")
 
 

# def solve_elastica(fx, fy, Fx_tip, Fy_tip, M_tip, n_init=100):
#     """Resout l'elastica plane avec charge repartie f=(fx,fy)(s)
#     et effort/moment de bout (Fx_tip, Fy_tip, M_tip)."""
 
#     def rhs(s, Y):
#         x, y, theta, Nx, Ny, M = Y
#         return np.vstack([
#             np.cos(theta),
#             np.sin(theta),
#             M / EI,
#             -fx(s) * np.ones_like(s),
#             -fy(s) * np.ones_like(s),
#             np.sin(theta) * Nx - np.cos(theta) * Ny,
#         ])
 
#     def bc(Ya, Yb):
#         return np.array([
#             Ya[0],
#             Ya[1],
#             Ya[2],
#             Yb[3] - Fx_tip,
#             Yb[4] - Fy_tip,
#             Yb[5] - M_tip,
#         ])
 
#     s = np.linspace(0.0, L, n_init)
#     Y0 = np.zeros((6, s.size))
#     sol = solve_bvp(rhs, bc, s, Y0, tol=1e-10, max_nodes=100000)
#     if not sol.success:
#         raise RuntimeError("BVP solver failed: " + sol.message)
#     return sol
 
  
# def sample(sol, s_values):
#     """Renvoie x(s), y(s), theta(s) aux abscisses curvilignes demandees."""
#     Y = sol.sol(np.asarray(s_values))
#     return Y[0], Y[1], Y[2]
 
 
# zero = lambda s: 0.0 * s
 
 
# # =================================================================
# # TEST A : PETITES DEFORMATIONS -- force transverse au bout
# #          comparaison avec la theorie d'Euler-Bernoulli (lineaire)
# # =================================================================
# print("\n=== TEST A : petites deformations (force au bout) ===")
 
# F_small = 1.0e-3   # N (force verticale, vers le bas)
 
# solA = solve_elastica(zero, zero, Fx_tip=0.0, Fy_tip=-F_small, M_tip=0.0)
 
# # Fleche et rotation au bout -- BVP non lineaire
# xA, yA, thA = sample(solA, [L])
# print(f"BVP        : y_tip = {yA[0]: .6e} m, theta_tip = {thA[0]: .6e} rad")
 
# # Solution Euler-Bernoulli (lineaire), pour comparaison
# y_tip_EB    = -F_small * L**3 / (3.0 * EI)
# theta_tip_EB = -F_small * L**2 / (2.0 * EI)
# print(f"EulerBern. : y_tip = {y_tip_EB: .6e} m, theta_tip = {theta_tip_EB: .6e} rad")
 
# err_y  = abs((yA[0]  - y_tip_EB)   / y_tip_EB)
# err_th = abs((thA[0] - theta_tip_EB) / theta_tip_EB)
# print(f"erreur relative : y -> {err_y:.3e}, theta -> {err_th:.3e}")
 

  
# # =================================================================
# # TEST B : GRANDES DEFORMATIONS -- moment pur au bout
# #          comparaison avec la solution EXACTE (arc de cercle)
# # =================================================================
# print("\n=== TEST B : grandes deformations (moment pur au bout) ===")
 
# # On choisit M0 pour que la tige s'enroule en un demi-cercle
# # (angle total = pi -> rayon R = L/pi)
# M0 = np.pi * EI / L
 
# solB = solve_elastica(zero, zero, Fx_tip=0.0, Fy_tip=0.0, M_tip=M0)
 
# s_eval = np.linspace(0, L, 11)
# xB, yB, thB = sample(solB, s_eval)
 
# # Solution exacte : sous moment pur, M(s)=M0 constant donc la courbure
# # kappa = M0/EI est constante -> arc de cercle de rayon R = EI/M0
# R = EI / M0
# theta_exact = s_eval * M0 / EI
# x_exact = R * np.sin(theta_exact)
# y_exact = R * (1.0 - np.cos(theta_exact))
 
# print(f"Rayon attendu R = EI/M0 = {R:.6f} m  (ici L/pi = {L/np.pi:.6f} m)")
# print("\n  s      x_BVP     x_exact     y_BVP     y_exact   theta_BVP  theta_exact")
# for i, s in enumerate(s_eval):
#     print(f"{s:5.2f}  {xB[i]: .6f}  {x_exact[i]: .6f}  "
#           f"{yB[i]: .6f}  {y_exact[i]: .6f}  "
#           f"{thB[i]: .6f}  {theta_exact[i]: .6f}")
 
# err_pos = np.max(np.abs(xB - x_exact)) + np.max(np.abs(yB - y_exact))
# print(f"\nerreur max position (BVP vs cercle exact) : {err_pos:.3e} m")
 

# # =================================================================
# # TEST C (bonus) : grandes deformations -- force au bout
# #         -> pas de forme close simple, mais utile comme reference
# #            directe pour SOFA (pas de comparaison "papier")
# # =================================================================
# print("\n=== TEST C (bonus) : grande force transverse au bout ===")
 
# # Force choisie pour avoir une fleche tip ~ L (grande deformation)
# F_large = 3.0 * EI / L**2
 
# solC = solve_elastica(zero, zero, Fx_tip=0.0, Fy_tip=-F_large, M_tip=0.0)
# xC, yC, thC = sample(solC, [L])
# print(f"F = {F_large:.6e} N  ->  x_tip = {xC[0]:.6f} m, "
#       f"y_tip = {yC[0]:.6f} m, theta_tip = {thC[0]:.6f} rad")
# print(f"(rappel L = {L} m -- la fleche est du meme ordre que L : "
#       f"comportement non-lineaire attendu)")
 
 
# # =================================================================
# # Export des profils (x,y,theta) le long de la tige
# # -> a comparer directement aux positions des noeuds/cadres SOFA
# # =================================================================
# def export_profile(sol, n_nodes, filename):
#     s_nodes = np.linspace(0, L, n_nodes)
#     x, y, th = sample(sol, s_nodes)
#     data = np.column_stack([s_nodes, x, y, th])
#     np.savetxt(filename, data, header="s x y theta", comments="# ")
#     print(f"-> profil exporte dans {filename} ({n_nodes} noeuds)")
 
# export_profile(solA, 11, "test_A_profile.txt")
# export_profile(solB, 11, "test_B_profile.txt")
# export_profile(solC, 11, "test_C_profile.txt")
 
 
# # =================================================================
# # (En commentaire) Etude de convergence : faire varier N (nombre de
# # sections) cote SOFA, et comparer la position du bout a la
# # reference BVP (qui est, elle, deja convergee -- tol=1e-10)
# # =================================================================


 
# # =================================================================
# # Visualisation rapide des 3 configurations
# # =================================================================
# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
 
# fig, axes = plt.subplots(1, 3, figsize=(13, 4))
 
# for ax, sol, title in zip(
#     axes, [solA, solB, solC],
#     ["A: petite force\n(comparaison Euler-Bernoulli)",
#      "B: moment pur\n(comparaison cercle exact)",
#      "C: grande force\n(reference BVP pour SOFA)"]):
 
#     s_plot = np.linspace(0, L, 200)
#     x_plot, y_plot, _ = sample(sol, s_plot)
#     ax.plot(x_plot, y_plot, lw=2)
#     ax.plot(0, 0, 'ks', ms=8, label="encastrement")
#     ax.plot(x_plot[-1], y_plot[-1], 'ro', ms=6, label="bout")
#     ax.set_title(title)
#     ax.set_xlabel("x [m]")
#     ax.set_ylabel("y [m]")
#     # ax.set_aspect("equal")
#     ax.grid(alpha=0.3)
#     ax.legend(fontsize=8)
 
# plt.tight_layout()
# plt.savefig("rod_shapes.png", dpi=120)
# print("\n-> figure sauvegardee dans rod_shapes.png")
 

# ############################
# ############################
# ### Comparaison avec SOFA ###
# ############################
# ############################

# ## Test A
# data_testA = np.loadtxt("test_A_profile.txt")

# x_testA = data_testA[0:, 1]
# y_testA = data_testA[0:, 2]

# data_sofa_testA = lire_monitor_sofa("f2s_test_A_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testA = data_sofa_testA[len(data_sofa_testA)-1]["pos"]
# x_sofa_testA = pos_testA[:, 0]
# y_sofa_testA = pos_testA[:, 1]

# plt.plot(x_sofa_testA, y_sofa_testA, 'o--', linewidth=2, label="F2S")
# plt.plot(x_testA, y_testA, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test A")
# plt.grid()
# plt.savefig("f2s_test_A_profile.png")
# plt.show()


# ## Test B

# data_testB = np.loadtxt("test_B_profile.txt")

# x_testB = data_testB[0:, 1]
# y_testB = data_testB[0:, 2]

# data_sofa_testB = lire_monitor_sofa("f2s_test_B_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testB = data_sofa_testB[len(data_sofa_testB)-1]["pos"]
# x_sofa_testB = pos_testB[:, 0]
# y_sofa_testB = pos_testB[:, 1]

# plt.plot(x_sofa_testB, y_sofa_testB, 'o--', linewidth=2, label="F2S")
# plt.plot(x_testB, y_testB, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test B")
# plt.grid()
# plt.savefig("f2s_test_B_profile.png")
# plt.show()


# ## Test C

# data_testC = np.loadtxt("test_C_profile.txt")

# x_testC = data_testC[0:, 1]
# y_testC = data_testC[0:, 2]

# data_sofa_testC = lire_monitor_sofa("f2s_test_C_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testC = data_sofa_testC[len(data_sofa_testC)-1]["pos"]
# x_sofa_testC = pos_testC[:, 0]
# y_sofa_testC = pos_testC[:, 1]

# plt.plot(x_sofa_testC, y_sofa_testC, 'o--', linewidth=2, label="F2S")
# plt.plot(x_testC, y_testC, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test C")
# plt.grid()
# plt.savefig("f2s_test_C_profile.png")
# plt.show()



####################
####################
## Pour le S2R
####################
####################


# ## Test A
# data_testA = np.loadtxt("test_A_profile.txt")

# x_testA = data_testA[0:, 1]
# y_testA = data_testA[0:, 2]

# data_sofa_testA = lire_monitor_sofa("s2r_test_A_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testA = data_sofa_testA[len(data_sofa_testA)-1]["pos"]
# x_sofa_testA = pos_testA[:, 0]
# y_sofa_testA = pos_testA[:, 1]

# plt.plot(x_sofa_testA, y_sofa_testA, 'o--', linewidth=2, label="S2R")
# plt.plot(x_testA, y_testA, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test A")
# plt.grid()
# plt.savefig("s2r_test_A_profile.png")
# plt.show()


# # Test B

# data_testB = np.loadtxt("test_B_profile.txt")

# x_testB = data_testB[0:, 1]
# y_testB = data_testB[0:, 2]

# data_sofa_testB = lire_monitor_sofa("s2r_test_B_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testB = data_sofa_testB[len(data_sofa_testB)-1]["pos"]
# x_sofa_testB = pos_testB[:, 0]
# y_sofa_testB = pos_testB[:, 1]

# plt.plot(x_sofa_testB, y_sofa_testB, 'o--', linewidth=2, label="S2R")
# plt.plot(x_testB, y_testB, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test B")
# plt.grid()
# plt.savefig("s2r_test_B_profile.png")
# plt.show()


## Test C

# data_testC = np.loadtxt("test_C_profile.txt")

# x_testC = data_testC[0:, 1]
# y_testC = data_testC[0:, 2]

# data_sofa_testC = lire_monitor_sofa("s2r_test_C_profile.txt", beam_length=L, nb_section=nb_section)

# pos_testC = data_sofa_testC[len(data_sofa_testC)-1]["pos"]
# x_sofa_testC = pos_testC[:, 0]
# y_sofa_testC = pos_testC[:, 1]

# plt.plot(x_sofa_testC, y_sofa_testC, 'o--', linewidth=2, label="S2R")
# plt.plot(x_testC, y_testC, 'x-', label="Analytique")
# plt.legend()
# plt.xlabel("x [m]")
# plt.ylabel("y [m]")
# plt.title("Profil de la poutre test C")
# plt.grid()
# plt.savefig("s2r_test_C_profile.png")
# plt.show()

