#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import time
import psutil

def fallback_package_power_w(cpu_util_percent: float, tdp_watts: float) -> float:
    # Estime la puissance (W) d'après la charge CPU et le TDP
    return max(0.0, min(1.0, cpu_util_percent / 100.0)) * tdp_watts

def cpu_times_active_total() -> float:
    # Retourne le temps CPU actif total du système
    t = psutil.cpu_times()
    active = 0.0
    for name in ("user", "system", "nice", "irq", "softirq", "guest"):
        active += getattr(t, name, 0.0)
    return active

def proc_cpu_times_active(proc: psutil.Process) -> float:
    # Retourne le temps CPU actif du processus
    with proc.oneshot():
        t = proc.cpu_times()
        return (getattr(t, "user", 0.0) + getattr(t, "system", 0.0))

def monitor(pid: int, duration: int = 60, interval: float = 1.0, tdp_watts: float = 28.0):
    # Mesure la consommation énergétique estimée d'un processus donné
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print("Erreur : PID introuvable.")
        return

    # Codes couleur ANSI
    JAUNE = "\033[93m"
    RESET = "\033[0m"

    # Affichage avec retours à la ligne supplémentaires
    print("\n\n\n")
    print(f"{JAUNE}Cible : {proc.name()} (PID={pid}) | durée={duration}s, pas={interval}s{RESET}\n")
    print("-" * 90)
    print(f"{'temps_s':>7} | {'P(W)':>7} | {'deltaE_tot(J)':>14} | {'part PID':>10} | {'deltaE_pid(J)':>14} | {'CPU_proc(%)':>11}")
    print("-" * 90)

    # État initial
    total_active_prev = cpu_times_active_total()
    try:
        proc_active_prev = proc_cpu_times_active(proc)
    except psutil.Error:
        print("Erreur : impossible de lire les temps CPU du processus.")
        return

    energy_pid_j = 0.0
    energy_total_j = 0.0
    start_time = time.time()

    t_end = start_time + duration
    while time.time() < t_end:
        time.sleep(interval)
        elapsed = int(time.time() - start_time)

        # Mesure CPU globale et estimation de la puissance
        cpu_util_total = psutil.cpu_percent(interval=None)
        p_w = fallback_package_power_w(cpu_util_total, tdp_watts)

        # Énergie totale sur l'intervalle
        e_interval_j = float(p_w) * float(interval)
        energy_total_j += e_interval_j

        # Calcul des parts CPU du processus
        total_active_cur = cpu_times_active_total()
        try:
            proc_active_cur = proc_cpu_times_active(proc)
        except psutil.NoSuchProcess:
            print("Le processus s'est terminé pendant la mesure.")
            break

        d_total = max(0.0, total_active_cur - total_active_prev)
        d_proc = max(0.0, proc_active_cur - proc_active_prev)
        share = (d_proc / d_total) if d_total > 1e-6 else 0.0

        e_pid_j = e_interval_j * share
        energy_pid_j += e_pid_j

        try:
            cpu_proc_pct = proc.cpu_percent(interval=None)
        except psutil.Error:
            cpu_proc_pct = 0.0

        # Affichage formaté avec temps (4 chiffres alignés)
        print(f"{elapsed:7d} | {p_w:7.2f} | {e_interval_j:14.3f} | {share:10.1%} | {e_pid_j:14.3f} | {cpu_proc_pct:11.1f}")

        # Mise à jour des références
        total_active_prev = total_active_cur
        proc_active_prev = proc_active_cur

    print("-" * 90)
    print(f"\n{JAUNE}Énergie totale estimée (CPU) : {energy_total_j/3600:.6f} Wh{RESET}")
    print(f"{JAUNE}Énergie attribuée au PID {pid} : {energy_pid_j/3600:.6f} Wh{RESET}\n\n\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pid", type=int, required=True, help="PID de l'application à mesurer")
    parser.add_argument("--duration", type=int, default=60, help="Durée de la mesure en secondes")
    parser.add_argument("--interval", type=float, default=1.0, help="Pas d'échantillonnage en secondes")
    parser.add_argument("--tdp", type=float, default=28.0, help="TDP CPU estimé en watts")
    args = parser.parse_args()
    monitor(args.pid, args.duration, args.interval, args.tdp)
