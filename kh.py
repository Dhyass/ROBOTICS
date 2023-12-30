# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 20:55:41 2023

@author: magnn
"""

import numpy as np
import matplotlib.pyplot as plt

# Paramètres du modèle de Vasicek
r0 = 0.05
kappa = 0.1
theta = 0.03
sigma = 0.03

# Paramètres du modèle de Poisson
lambda_poisson = 0.1

# Paramètres de la distribution log-normale
mu_ln = -0.1
sigma_ln = 0.2

# Paramètres de simulation
num_simulations = 1000
T = 1  # Horizon de négociation en années

# Fonction de simulation Monte Carlo
def simulate_mc_vasicek(r0, kappa, theta, sigma, lambda_poisson, mu_ln, sigma_ln, num_simulations, T):
    dt = 1 / 252  # Discrétisation quotidienne
    num_steps = int(T / dt)
    
    bond_prices = np.zeros(num_simulations)
    
    for i in range(num_simulations):
        # Simulation du processus de Poisson
        pois_process = np.random.poisson(lambda_poisson * T)
        
        # Simulation du processus de Vasicek
        vasicek_process = np.zeros(num_steps + 1)
        vasicek_process[0] = r0
        
        for t in range(1, num_steps + 1):
            dW = np.random.normal(0, np.sqrt(dt))
            dZ = np.random.normal(0, np.sqrt(dt))
            
            vasicek_process[t] = (
                vasicek_process[t - 1] + kappa * (theta - vasicek_process[t - 1]) * dt +
                sigma * np.sqrt(dt) * dW + sigma_ln * np.sqrt(dt) * dZ
            )
        
        # Calcul du prix de l'obligation catastrophe
        loss_values = np.random.lognormal(mean=mu_ln, sigma=sigma_ln, size=pois_process)
        total_loss = np.sum(loss_values)
        discount_factor = np.exp(-np.trapz(vasicek_process, dx=dt))
        
        bond_prices[i] = np.exp(-total_loss) * discount_factor
    
    return bond_prices

# Simulation Monte Carlo
simulated_prices = simulate_mc_vasicek(r0, kappa, theta, sigma, lambda_poisson, mu_ln, sigma_ln, num_simulations, T)

# Affichage des résultats
plt.hist(simulated_prices, bins=30, edgecolor='black')
plt.title('Distribution des prix des obligations catastrophiques')
plt.xlabel('Prix de l\'obligation catastrophe')
plt.ylabel('Fréquence')
plt.show()

# Calcul des statistiques
mean_price = np.mean(simulated_prices)
std_dev_price = np.std(simulated_prices)
max_price = np.max(simulated_prices)
min_price = np.min(simulated_prices)

# Affichage des statistiques
print(f"Prix moyen : {mean_price:.4f}")
print(f"Écart type du prix : {std_dev_price:.4f}")
print(f"Prix maximum : {max_price:.4f}")
print(f"Prix minimum : {min_price:.4f}")
