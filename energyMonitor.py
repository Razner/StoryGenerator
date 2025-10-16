#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

def monitor_two(pid1: int, pid2: int, name1: str, name2: str, duration: int = 60, interval: float = 1.0, tdp_watts: float = 28.0):
    # Mesure la consommation énergétique estimée de deux processus donnés
    try:
        proc1 = psutil.Process(pid1)
    except psutil.NoSuchProcess:
        print(f"Erreur : PID de {name1} introuvable.")
        return
    try:
        proc2 = psutil.Process(pid2)
    except psutil.NoSuchProcess:
        print(f"Erreur : PID de {name2} introuvable.")
        return

    # Codes couleur ANSI
    VERT = "\033[92m"
    BLEU = "\033[94m"
    JAUNE = "\033[93m"
    BLANC = "\033[97m"
    RESET = "\033[0m"

    print("\n\n\n")
    print(
        f"{BLEU}Cible 1 : {name1} (PID={pid1}){RESET} | "
        f"{JAUNE}Cible 2 : {name2} (PID={pid2}){RESET} | "
        f"{BLANC}durée={duration}s, pas={interval}s{RESET}\n"
    )

    sep_len = 140
    print("-" * sep_len)
    # En-tête du tableau coloré par cible
    print(
        f"{'temps_s':>7} | {'P(W)':>7} | {'deltaE_tot(J)':>14} | "
        f"{BLEU}{'part1':>7} | {'deltaE1(J)':>12} | {'CPU1(%)':>9}{RESET} | "
        f"{JAUNE}{'part2':>7} | {'deltaE2(J)':>12} | {'CPU2(%)':>9}{RESET}"
    )
    print("-" * sep_len)

    # État initial
    total_active_prev = cpu_times_active_total()
    try:
        proc1_active_prev = proc_cpu_times_active(proc1)
    except psutil.Error:
        print("Erreur : impossible de lire les temps CPU du processus 1.")
        return
    try:
        proc2_active_prev = proc_cpu_times_active(proc2)
    except psutil.Error:
        print("Erreur : impossible de lire les temps CPU du processus 2.")
        return

    energy1_j = 0.0
    energy2_j = 0.0
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

        # Calcul des parts CPU des processus
        total_active_cur = cpu_times_active_total()

        try:
            proc1_active_cur = proc_cpu_times_active(proc1)
            alive1 = True
        except psutil.NoSuchProcess:
            proc1_active_cur = proc1_active_prev
            alive1 = False

        try:
            proc2_active_cur = proc_cpu_times_active(proc2)
            alive2 = True
        except psutil.NoSuchProcess:
            proc2_active_cur = proc2_active_prev
            alive2 = False

        d_total = max(0.0, total_active_cur - total_active_prev)
        d1 = max(0.0, proc1_active_cur - proc1_active_prev) if alive1 else 0.0
        d2 = max(0.0, proc2_active_cur - proc2_active_prev) if alive2 else 0.0

        share1 = (d1 / d_total) if d_total > 1e-6 else 0.0
        share2 = (d2 / d_total) if d_total > 1e-6 else 0.0

        e1 = e_interval_j * share1
        e2 = e_interval_j * share2
        energy1_j += e1
        energy2_j += e2

        try:
            cpu1_pct = proc1.cpu_percent(interval=None) if alive1 else 0.0
        except psutil.Error:
            cpu1_pct = 0.0
        try:
            cpu2_pct = proc2.cpu_percent(interval=None) if alive2 else 0.0
        except psutil.Error:
            cpu2_pct = 0.0

        print(
            f"{elapsed:7d} | {p_w:7.2f} | {e_interval_j:14.3f} | "
            f"{BLEU}{share1:7.1%} | {e1:12.3f} | {cpu1_pct:9.1f}{RESET} | "
            f"{JAUNE}{share2:7.1%} | {e2:12.3f} | {cpu2_pct:9.1f}{RESET}"
        )

        total_active_prev = total_active_cur
        proc1_active_prev = proc1_active_cur
        proc2_active_prev = proc2_active_cur

    print("-" * sep_len)
    print(f"\n{VERT}Énergie totale estimée (CPU) : {energy_total_j/3600:.6f} Wh{RESET}")
    print(f"{BLEU}Énergie attribuée à {name1} : {energy1_j/3600:.6f} Wh{RESET}")
    print(f"{JAUNE}Énergie attribuée à {name2} : {energy2_j/3600:.6f} Wh{RESET}\n\n\n")

if __name__ == "__main__":
    print("\n=== Mesure de consommation énergétique sur deux processus ===")
    print("Saisis les informations demandées ci-dessous.\n")

    # Ligne 1 : HistoRik
    pid1 = int(input("PID de HistoRik : ").strip())
    name1 = "HistoRik"

    # Ligne 2 : autre process (nom + PID)
    raw = input("Nom et PID du processus de comparaison (ex: Notepad 25004) : ").strip().split()
    if len(raw) < 2:
        print("Erreur : tu dois saisir le nom et le PID séparés par un espace.")
        exit(1)
    name2 = raw[0]
    pid2 = int(raw[1])

    # Durée et intervalle (facultatif)
    duration = input("Durée de la mesure (s, défaut 60) : ").strip()
    interval = input("Pas d'échantillonnage (s, défaut 1.0) : ").strip()
    tdp = input("TDP CPU estimé (W, défaut 28.0) : ").strip()

    duration = int(duration) if duration else 60
    interval = float(interval) if interval else 1.0
    tdp = float(tdp) if tdp else 28.0

    monitor_two(pid1, pid2, name1, name2, duration, interval, tdp)
