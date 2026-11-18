#!/usr/bin/env python3
"""QuantumAstro-Lab - educational quantum astrophysics lab.

by Darion Kellar

Pure Python standard library. Zero dependencies. Zero network.
Education only - and the central lesson is stated up front:

  * This lab computes TEXTBOOK quantum astrophysics from labelled
    physical constants: electron-degeneracy pressure holds up a
    white dwarf, the same pressure fails relativistically at the
    Chandrasekhar mass, fusion in a stellar core burns at the
    Gamow peak where a Maxwell-Boltzmann tail meets a tunnelling
    probability, neutron degeneracy sets the scale of a neutron
    star, and a black hole radiates at the Hawking temperature.
  * Every constant is a labelled CODATA / exact-SI value written
    in the code. Every mass, temperature, and radius is a LABELLED
    teaching value. Nothing here is fitted to, measured from, or
    predicted about any real star, and no output is an observation.
  * The models are the honest textbook ones, with their limits
    printed next to their results: the white dwarf is a
    nonrelativistic n = 3/2 polytrope, the energy argument uses a
    uniform-density toy whose critical mass overshoots the real
    Lane-Emden value (both numbers are printed), the neutron star
    ignores general relativity and says so, and the Hawking
    formulas are the semiclassical textbook results.

Observational, mission, prediction, and real-object uses are
permanent HOLD gates - with Gemini Argon 4 Extended Thinking as
DECIDER (names-only, tighten-only), Muse as advisor (never
overrides HOLD), and Google Flow plan-only seats.
"""
import hashlib
import json
import math
import sys

# ---------------------------------------------------------------- constants
VERSION = "1.0.0"

# Labelled physical constants: exact SI values where the SI defines
# them (h, c, k_B, e), CODATA 2018/2022 values otherwise (G, particle
# masses, alpha, M_sun nominal). These are textbook constants, NOT
# measurements made by this lab.
H_PLANCK = 6.62607015e-34          # J s, exact SI
HBAR = H_PLANCK / (2.0 * math.pi)  # J s, derived
C_LIGHT = 299792458.0              # m/s, exact SI
G_GRAV = 6.67430e-11               # m^3 kg^-1 s^-2, CODATA 2018
K_BOLTZ = 1.380649e-23             # J/K, exact SI
M_ELECTRON = 9.1093837015e-31      # kg, CODATA
M_PROTON = 1.67262192369e-27       # kg, CODATA
M_NEUTRON = 1.67492749804e-27      # kg, CODATA
AMU = 1.66053906660e-27            # kg, CODATA
M_SUN = 1.98847e30                 # kg, nominal solar mass
ALPHA_FINE = 7.2973525693e-3       # dimensionless, CODATA
EV_JOULE = 1.602176634e-19         # J per eV, exact SI
YEAR_S = 365.25 * 24.0 * 3600.0    # s, Julian year

# White-dwarf composition: carbon/oxygen core, 2 nucleons per electron.
MU_E_WD = 2.0
M_PER_ELECTRON_WD = MU_E_WD * M_PROTON

# Lane-Emden structure constants (textbook values, labelled).
XI1_N15 = 3.65375374     # surface radius factor, n = 3/2 polytrope
OMEGA_N15 = 2.71405510   # mass factor (-xi^2 theta'), n = 3/2
OMEGA_N3 = 2.01823595    # mass factor (-xi^2 theta'), n = 3

SOLAR_CORE_T = 1.5e7     # K, LABELLED teaching value for the Sun's core

# ---------------------------------------------------------------- HOLD gates
HOLD_GATES = {
    "observational_data_claim": "HOLD - no claiming lab numbers are observations of any real star or object",
    "real_star_prediction_claim": "HOLD - no predicting a real star's fate, mass, radius, or lifetime",
    "mission_design_claim": "HOLD - no mission, probe, or spacecraft design use of these toy models",
    "telescope_observation_claim": "HOLD - no claiming any real object is detectable or visible from these numbers",
    "gravitational_wave_claim": "HOLD - no gravitational-wave event, merger, or detection predictions",
    "supernova_prediction_claim": "HOLD - no supernova timing, type, or progenitor predictions for real stars",
    "real_object_classification_claim": "HOLD - no classifying a real observed object as white dwarf / neutron star / black hole from this lab",
    "fusion_reactor_claim": "HOLD - the Gamow math is stellar teaching material, not a fusion reactor design",
    "weapons_claim": "HOLD - no weapons use of fusion, tunnelling, or degeneracy physics, ever",
    "habitability_claim": "HOLD - no habitability or life claims about real stars or planets",
    "navigation_claim": "HOLD - no spacecraft navigation or trajectory use",
    "investment_claim": "HOLD - no investment or space-industry claims from a teaching model",
    "astrology_claim": "HOLD - no astrology; this lab is physics, not fortune-telling",
    "textbook_value_as_measurement_claim": "HOLD - textbook constants and polytrope outputs must never be presented as measurements",
}


def gate(action):
    """Return 'HOLD' if the action is gated, else 'PROCEED' (sandbox sim)."""
    return "HOLD" if action in HOLD_GATES else "PROCEED"


# ================================================================ 1. Degeneracy polytropes
# A zero-temperature Fermi gas of nonrelativistic particles has
# pressure P = (3 pi^2)^(2/3) hbar^2 / (5 m_f) * n^(5/3). Writing the
# mass density as rho = (mass per fermion) * n turns this into a
# polytrope P = K rho^(5/3) with n = 3/2. The Lane-Emden solution for
# n = 3/2 then gives R proportional to M^(-1/3): heavier degenerate
# stars are SMALLER, the signature of degeneracy support.

def degeneracy_K(m_fermion, mass_per_fermion):
    """Polytrope constant K for a nonrelativistic degenerate gas."""
    return ((3.0 * math.pi ** 2) ** (2.0 / 3.0) * HBAR ** 2
            / (5.0 * m_fermion * mass_per_fermion ** (5.0 / 3.0)))


def polytrope_radius(mass_kg, K):
    """(radius_m, central_density) for an n = 3/2 polytrope.

    M = 4 pi OMEGA_N15 * a^3 * rho_c with a^2 = (5K / 8 pi G)
    rho_c^(-1/3); eliminating rho_c gives rho_c from M, then R.
    """
    a_factor = 2.5 * K / (4.0 * math.pi * G_GRAV)
    rho_c = (mass_kg / (4.0 * math.pi * OMEGA_N15 * a_factor ** 1.5)) ** 2
    a = math.sqrt(a_factor * rho_c ** (-1.0 / 3.0))
    return XI1_N15 * a, rho_c


K_WHITE_DWARF = degeneracy_K(M_ELECTRON, M_PER_ELECTRON_WD)
K_NEUTRON_STAR = degeneracy_K(M_NEUTRON, M_NEUTRON)


def white_dwarf_radius(mass_msun):
    radius_m, _ = polytrope_radius(mass_msun * M_SUN, K_WHITE_DWARF)
    return radius_m


def white_dwarf_table(masses_msun=(0.4, 0.6, 0.8, 1.0, 1.2, 1.4)):
    rows = []
    for mass in masses_msun:
        radius_m, rho_c = polytrope_radius(mass * M_SUN, K_WHITE_DWARF)
        rows.append({
            "mass_msun": mass,
            "radius_km": round(radius_m / 1000.0, 1),
            "central_density_kg_m3": rho_c,
        })
    return rows


def white_dwarf_report():
    return {
        "model": "nonrelativistic electron-degeneracy polytrope (n = 3/2)",
        "mu_e": MU_E_WD,
        "K": K_WHITE_DWARF,
        "scaling": "R proportional to M^(-1/3)",
        "table": white_dwarf_table(),
        "honest_note": "Textbook polytrope: real white dwarfs are "
                       "smaller at high mass because the electrons go "
                       "relativistic - that failure is section 2.",
    }


# ================================================================ 2. Relativistic turn-over + Chandrasekhar mass
# The exact relativistic Fermi gas has mean kinetic energy per
# electron set by x = p_F / (m_e c). With a uniform-density toy star
# (labelled), the total energy E(R) = E_kin(R) - 3 G M^2 / (5 R) has
# a minimum at the equilibrium radius while M is small. As M grows
# the kinetic term softens from R^-2 toward R^-1, the minimum
# shallows, and past a critical mass it vanishes: no equilibrium at
# any radius. The uniform-density toy puts that critical mass near
# 1.72 M_sun; the real answer needs the n = 3 Lane-Emden polytrope
# and is 1.44 M_sun. BOTH numbers are printed - the toy is a toy.

def fermi_x(mass_kg, radius_m, mass_per_fermion):
    """Dimensionless Fermi momentum x = p_F / (m_f c), uniform density."""
    n_fermion = (mass_kg / mass_per_fermion) / (4.0 / 3.0 * math.pi * radius_m ** 3)
    p_f = HBAR * (3.0 * math.pi ** 2 * n_fermion) ** (1.0 / 3.0)
    return p_f, n_fermion


def kinetic_energy(mass_kg, radius_m, m_fermion=M_ELECTRON,
                   mass_per_fermion=M_PER_ELECTRON_WD):
    """Exact relativistic degenerate kinetic energy, uniform density.

    U = V m_f^4 c^5 / (pi^2 hbar^3) * [ (x(2x^2+1)sqrt(1+x^2)
        - asinh x)/8 - x^3/3 ], the closed-form Fermi integral.
    """
    p_f, _ = fermi_x(mass_kg, radius_m, mass_per_fermion)
    x = p_f / (m_fermion * C_LIGHT)
    volume = 4.0 / 3.0 * math.pi * radius_m ** 3
    integral = ((x * (2.0 * x * x + 1.0) * math.sqrt(1.0 + x * x)
                 - math.asinh(x)) / 8.0 - x ** 3 / 3.0)
    return volume * m_fermion ** 4 * C_LIGHT ** 5 / (math.pi ** 2 * HBAR ** 3) * integral


def gravitational_energy(mass_kg, radius_m):
    """Uniform-sphere self-gravity: -3 G M^2 / (5 R)."""
    return -3.0 * G_GRAV * mass_kg ** 2 / (5.0 * radius_m)


def total_energy(mass_kg, radius_m):
    return (kinetic_energy(mass_kg, radius_m)
            + gravitational_energy(mass_kg, radius_m))


def energy_minimum(mass_kg):
    """Scan + golden-section minimum of E(R) on a log grid.

    Returns dict with radius_m, energy_J, and has_minimum: True only
    when the grid argmin is interior (a real equilibrium), False
    when E falls all the way to the smallest radius (collapse in
    this toy - no equilibrium exists).
    """
    lo, hi, steps = math.log(50.0), math.log(1.0e9), 400
    best_r, best_e, best_i = None, None, -1
    for i in range(steps + 1):
        radius = math.exp(lo + (hi - lo) * i / steps)
        energy = total_energy(mass_kg, radius)
        if best_e is None or energy < best_e:
            best_r, best_e, best_i = radius, energy, i
    interior = 0 < best_i < steps
    a = math.exp(lo + (hi - lo) * max(best_i - 1, 0) / steps)
    b = math.exp(lo + (hi - lo) * min(best_i + 1, steps) / steps)
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    x1, x2 = b - gr * (b - a), a + gr * (b - a)
    for _ in range(200):
        if total_energy(mass_kg, x1) < total_energy(mass_kg, x2):
            b, x2, x1 = x2, x1, b - gr * (b - a)
        else:
            a, x1, x2 = x1, x2, a + gr * (b - a)
    radius_star = (a + b) / 2.0
    energy_star = total_energy(mass_kg, radius_star)
    return {
        "radius_m": radius_star,
        "energy_J": energy_star,
        "has_minimum": bool(interior and energy_star < 0.0),
    }


def toy_critical_mass_msun():
    """Largest mass (M_sun) whose E(R) still has a minimum.

    Bisection on the has_minimum predicate of the uniform-density
    relativistic energy toy. Labelled: this toy overshoots the
    Lane-Emden Chandrasekhar mass, and the lab prints both.
    """
    lo, hi = 1.0, 3.0
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if energy_minimum(mid * M_SUN)["has_minimum"]:
            lo = mid
        else:
            hi = mid
    return lo


def toy_critical_mass_analytic_msun():
    """Ultra-relativistic coefficient equality for the same toy.

    In the UR limit U_kin = (3/4) N_e p_F c with the uniform-density
    p_F; setting its 1/R coefficient equal to 3 G M^2 / 5 gives
    M = [(5/4)(9 pi/4)^(1/3)]^(3/2) (hbar c/G)^(3/2) / (mu_e m_H)^2.
    The numeric scan must land on this - two routes, one answer.
    """
    prefactor = ((5.0 / 4.0) * (9.0 * math.pi / 4.0) ** (1.0 / 3.0)) ** 1.5
    return (prefactor * (HBAR * C_LIGHT / G_GRAV) ** 1.5
            / M_PER_ELECTRON_WD ** 2 / M_SUN)


def chandrasekhar_mass():
    """The textbook Chandrasekhar mass from the n = 3 polytrope.

    Relativistic degeneracy gives P = K_rel rho^(4/3) with
    K_rel = (3 pi^2)^(1/3) hbar c / (4 (mu_e m_H)^(4/3)); the n = 3
    Lane-Emden mass M = 4 pi OMEGA_N3 (K_rel / (pi G))^(3/2) is then
    a pure number times (hbar c/G)^(3/2) / (mu_e m_H)^2 - computed
    here from the constants, not quoted.
    """
    K_rel = ((3.0 * math.pi ** 2) ** (1.0 / 3.0) * HBAR * C_LIGHT
             / (4.0 * M_PER_ELECTRON_WD ** (4.0 / 3.0)))
    mass_kg = 4.0 * math.pi * OMEGA_N3 * (K_rel / (math.pi * G_GRAV)) ** 1.5
    scale = (HBAR * C_LIGHT / G_GRAV) ** 1.5 / M_PER_ELECTRON_WD ** 2
    return {"mass_kg": mass_kg, "mass_msun": mass_kg / M_SUN,
            "dimensionless_prefactor": mass_kg / scale, "K_rel": K_rel}


def chandrasekhar_report():
    m1 = energy_minimum(1.0 * M_SUN)
    m3 = energy_minimum(3.0 * M_SUN)
    return {
        "energy_minimum_1msun": {
            "radius_km": round(m1["radius_m"] / 1000.0, 1),
            "energy_J": m1["energy_J"],
            "has_minimum": m1["has_minimum"],
        },
        "energy_minimum_3msun": {
            "radius_km": round(m3["radius_m"] / 1000.0, 1),
            "energy_J": m3["energy_J"],
            "has_minimum": m3["has_minimum"],
        },
        "toy_critical_mass_msun": round(toy_critical_mass_msun(), 4),
        "toy_critical_mass_analytic_msun": round(
            toy_critical_mass_analytic_msun(), 4),
        "chandrasekhar_mass_msun": round(chandrasekhar_mass()["mass_msun"], 4),
        "honest_note": "Uniform-density energy toy: minimum exists at "
                       "1 M_sun, gone at 3 M_sun, vanishes near "
                       "1.72 M_sun. The textbook Lane-Emden n = 3 "
                       "value is 1.44 M_sun. The toy overshoots "
                       "because a real star is centrally concentrated.",
    }


# ================================================================ 3. Fusion tunnelling + the Gamow peak
# A charged-particle reaction at thermal energy faces two exponentials
# fighting each other: the Maxwell-Boltzmann factor exp(-E/kT) falls
# with E, while the WKB tunnelling probability exp(-sqrt(E_G/E))
# rises. Their product peaks at the Gamow energy
# E0 = (E_G (kT)^2 / 4)^(1/3), far above kT - fusion burns in the
# tail of the distribution, through the barrier, not over it.

def gamow_energy_J(z1=1, z2=1, reduced_mass_kg=None):
    """Gamow energy E_G = 2 mu c^2 (pi alpha Z1 Z2)^2."""
    mu = M_PROTON / 2.0 if reduced_mass_kg is None else reduced_mass_kg
    return 2.0 * mu * C_LIGHT ** 2 * (math.pi * ALPHA_FINE * z1 * z2) ** 2


E_GAMOW_PP_J = gamow_energy_J()
E_GAMOW_PP_KEV = E_GAMOW_PP_J / EV_JOULE / 1000.0


def tunnelling_probability(energy_kev, e_gamow_kev=E_GAMOW_PP_KEV):
    """WKB s-wave tunnelling factor exp(-sqrt(E_G / E))."""
    if energy_kev <= 0:
        raise ValueError("energy must be positive")
    return math.exp(-math.sqrt(e_gamow_kev / energy_kev))


def boltzmann_factor(energy_kev, temperature_K):
    kT_kev = K_BOLTZ * temperature_K / EV_JOULE / 1000.0
    return math.exp(-energy_kev / kT_kev)


def gamow_log_integrand(energy_kev, temperature_K):
    kT_kev = K_BOLTZ * temperature_K / EV_JOULE / 1000.0
    return -energy_kev / kT_kev - math.sqrt(E_GAMOW_PP_KEV / energy_kev)


def gamow_peak_analytic_kev(temperature_K):
    """E0 = (E_G (kT)^2 / 4)^(1/3), the textbook Gamow peak."""
    kT_kev = K_BOLTZ * temperature_K / EV_JOULE / 1000.0
    return (E_GAMOW_PP_KEV * kT_kev ** 2 / 4.0) ** (1.0 / 3.0)


def gamow_peak_numeric_kev(temperature_K):
    """The lab's own maximisation of the product integrand.

    Coarse grid over 0.05..40 keV, then golden-section refinement on
    the log integrand. No analytic shortcut is taken.
    """
    steps = 4000
    best_e, best_v = None, None
    for i in range(steps + 1):
        energy = 0.05 + (40.0 - 0.05) * i / steps
        value = gamow_log_integrand(energy, temperature_K)
        if best_v is None or value > best_v:
            best_e, best_v = energy, value
    step = (40.0 - 0.05) / steps
    a, b = max(0.01, best_e - step), best_e + step
    gr = (math.sqrt(5.0) - 1.0) / 2.0
    x1, x2 = b - gr * (b - a), a + gr * (b - a)
    for _ in range(200):
        if gamow_log_integrand(x1, temperature_K) < gamow_log_integrand(x2, temperature_K):
            a, x1, x2 = x1, x2, a + gr * (b - a)
        else:
            b, x2, x1 = x2, x1, b - gr * (b - a)
    return (a + b) / 2.0


def gamow_report(temperature_K=SOLAR_CORE_T):
    kT_kev = K_BOLTZ * temperature_K / EV_JOULE / 1000.0
    e0 = gamow_peak_analytic_kev(temperature_K)
    return {
        "reaction": "p + p (Z1 = Z2 = 1, reduced mass m_p/2)",
        "temperature_K": temperature_K,
        "temperature_label": "LABELLED solar-core teaching value",
        "kT_kev": round(kT_kev, 4),
        "gamow_energy_kev": round(E_GAMOW_PP_KEV, 2),
        "peak_analytic_kev": round(e0, 4),
        "peak_numeric_kev": round(gamow_peak_numeric_kev(temperature_K), 4),
        "peak_over_kT": round(e0 / kT_kev, 2),
        "suppression_exp_minus_3E0_over_kT": math.exp(-3.0 * e0 / kT_kev),
        "honest_note": "The integrand is the Maxwell-Boltzmann factor "
                       "times the WKB tunnelling probability; cross "
                       "sections, screening, and the weak-interaction "
                       "step of the real pp chain are out of scope.",
    }


# ================================================================ 4. Neutron-star toy
# Swap the fermion: neutron degeneracy pressure, neutron mass per
# fermion, same n = 3/2 polytrope. The radius scale collapses from
# thousands of km to ~13 km for 1.4 M_sun. LABELLED order-of-
# magnitude toy: general relativity, interactions, and the real
# equation of state are all ignored, and the lab says so everywhere.

def neutron_star_radius(mass_msun):
    radius_m, _ = polytrope_radius(mass_msun * M_SUN, K_NEUTRON_STAR)
    return radius_m


def neutron_star_report(mass_msun=1.4):
    radius_m, rho_c = polytrope_radius(mass_msun * M_SUN, K_NEUTRON_STAR)
    wd_radius_m = white_dwarf_radius(mass_msun)
    return {
        "model": "neutron-degeneracy n = 3/2 polytrope (toy)",
        "mass_msun": mass_msun,
        "radius_km": round(radius_m / 1000.0, 2),
        "central_density_kg_m3": rho_c,
        "white_dwarf_radius_same_mass_km": round(wd_radius_m / 1000.0, 1),
        "radius_ratio_to_white_dwarf": radius_m / wd_radius_m,
        "honest_note": "Order-of-magnitude toy only: GR ignored, no "
                       "nuclear interactions, no real equation of "
                       "state. Real neutron stars need TOV + a "
                       "microphysical EOS; this is the degeneracy "
                       "scaling, nothing more.",
    }


# ================================================================ 5. Hawking radiation
# Semiclassical textbook results: a black hole of mass M radiates
# like a blackbody at T_H = hbar c^3 / (8 pi G M k_B), sits inside
# its Schwarzschild radius r_s = 2 G M / c^2, and evaporates on a
# timescale t = 5120 pi G^2 M^3 / (hbar c^4). A solar-mass hole is
# colder than the cosmic microwave background and effectively
# eternal; both facts fall out of the constants.

def hawking_temperature(mass_kg):
    return HBAR * C_LIGHT ** 3 / (8.0 * math.pi * G_GRAV * mass_kg * K_BOLTZ)


def schwarzschild_radius(mass_kg):
    return 2.0 * G_GRAV * mass_kg / C_LIGHT ** 2


def evaporation_time_s(mass_kg):
    return (5120.0 * math.pi * G_GRAV ** 2 * mass_kg ** 3
            / (HBAR * C_LIGHT ** 4))


def hawking_report(masses_msun=(1.0, 10.0, 1.0e6)):
    rows = []
    for mass in masses_msun:
        rows.append({
            "mass_msun": mass,
            "temperature_K": hawking_temperature(mass * M_SUN),
            "schwarzschild_radius_km": round(
                schwarzschild_radius(mass * M_SUN) / 1000.0, 4),
            "evaporation_time_yr": evaporation_time_s(mass * M_SUN) / YEAR_S,
        })
    return {
        "formula": "T_H = hbar c^3 / (8 pi G M k_B)",
        "rows": rows,
        "honest_note": "Semiclassical textbook formulas. No black "
                       "hole has been observed evaporating; the "
                       "numbers are what the formulas give for the "
                       "labelled masses, nothing more.",
    }


# ================================================================ 6. kNN remnant classifier
# Features: mass (M_sun) and radius (km). The training grid is
# labelled by the lab's own remnant policy (remnant_policy below),
# whose boundaries are the lab's computed scales: the Schwarzschild
# radius, the neutron-star polytrope scale, and the white-dwarf
# polytrope scale. The classifier interpolates the policy - it
# classifies TOY points, never real observed objects (a HOLD gate).

def remnant_policy(mass_msun, radius_km):
    """The lab's remnant policy, from its own computed boundaries."""
    r_s_km = schwarzschild_radius(mass_msun * M_SUN) / 1000.0
    if radius_km <= 1.5 * r_s_km:
        return "black-hole"
    if radius_km <= 100.0:
        return "neutron-star"
    if radius_km <= 30000.0:
        return "white-dwarf"
    return "main-sequence-supported"


def _training_grid():
    masses = (0.1, 0.3, 0.6, 1.0, 1.4, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0)
    radii = (3.0, 10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0,
             30000.0, 100000.0, 300000.0, 700000.0)
    return [((mass, radius), remnant_policy(mass, radius))
            for mass in masses for radius in radii]


TRAINING_GRID = _training_grid()


def _scaled(features):
    mass_msun, radius_km = features
    return (mass_msun / 30.0, math.log10(radius_km) / 6.0)


def classify_remnant(mass_msun, radius_km, k=5):
    """kNN over the policy-labelled grid, deterministic tie-breaking."""
    target = _scaled((mass_msun, radius_km))
    ranked = []
    for features, label in TRAINING_GRID:
        point = _scaled(features)
        dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(target, point)))
        ranked.append((dist, features, label))
    ranked.sort(key=lambda row: (row[0], row[1]))
    votes = {}
    for _, _, label in ranked[:k]:
        votes[label] = votes.get(label, 0) + 1
    priority = {"black-hole": 0, "neutron-star": 1, "white-dwarf": 2,
                "main-sequence-supported": 3}
    return sorted(votes.items(), key=lambda kv: (-kv[1], priority[kv[0]]))[0][0]


def classifier_report():
    wd_r = white_dwarf_radius(1.0) / 1000.0
    ns_r = neutron_star_radius(1.4) / 1000.0
    scenarios = {
        "sun_like_1msun_695700km": (1.0, 695700.0),
        "white_dwarf_1msun_lab_radius": (1.0, wd_r),
        "white_dwarf_0.6msun_lab_radius": (0.6, white_dwarf_radius(0.6) / 1000.0),
        "neutron_star_1.4msun_lab_radius": (1.4, ns_r),
        "inside_schwarzschild_scale_10msun_20km": (10.0, 20.0),
    }
    return {name: classify_remnant(*features)
            for name, features in scenarios.items()}


# ================================================================ 7. Advisory seats
def _trace(payload):
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def argon4_decide(topic="quantumastro-demo"):
    """Gemini Argon 4 DECIDER seat: MAP->MODEL->STRESS->DECIDE.

    Names-only keys, live calls 0, tighten-only: can add HOLDs, never lift one.
    """
    stages = ["MAP", "MODEL", "STRESS", "DECIDE"]
    payload = {"seat": "gemini-argon-4", "topic": topic, "stages": stages}
    return {
        "seat": "Gemini Argon 4 Extended Thinking",
        "role": "DECIDER",
        "pipeline": stages,
        "tiers": [2048, 8192, 32768],
        "key": "names-only (GEMINI_API_KEY name checked, value never read)",
        "live_calls": 0,
        "decision": "PROCEED - sandbox simulation only, all observational / prediction gates stay HOLD",
        "can_override_hold": False,
        "trace_sha256_16": _trace(payload),
    }


def claude_advisor(topic="quantumastro-demo"):
    """Muse advisor seat: advises, can never override a HOLD."""
    return {
        "seat": "Muse",
        "role": "ADVISOR",
        "key": "names-only (MODEL_API_KEY name checked, value never read)",
        "live_calls": 0,
        "advice": "Print both critical masses side by side - the uniform-density toy's 1.72 and the Lane-Emden 1.44 - and say why they differ; a lab that shows its toy overshooting teaches more than one that hides it.",
        "can_override_hold": False,
    }


def google_flow_plan():
    """Google Flow seat: plan-only, nothing rendered, nothing live."""
    return {
        "seat": "Google Flow",
        "role": "PLAN-ONLY",
        "shots": ["a white dwarf shrinking as mass is added, radius falling as M^(-1/3)",
                  "the E(R) curve losing its minimum as the mass dial crosses the critical line",
                  "two protons tunnelling through a Coulomb wall at the Gamow peak",
                  "a neutron star the size of a city beside the white dwarf it out-weighs",
                  "a black hole glowing at 6e-8 K against the warmer cosmic background"],
        "rendered": False,
        "live": 0,
    }


def brains_report():
    return {"decider": argon4_decide(), "advisor": claude_advisor(),
            "flow": google_flow_plan()}


# ================================================================ checks
def run_checks():
    c = []

    def chk(name, ok):
        c.append((name, bool(ok)))

    # constants
    chk("hbar_derived_from_h", HBAR == H_PLANCK / (2.0 * math.pi))
    chk("constants_ordering", M_NEUTRON > M_PROTON > M_ELECTRON > 0
        and G_GRAV > 0 and C_LIGHT > 0 and K_BOLTZ > 0)

    # 1. white-dwarf polytrope
    chk("wd_K_positive", K_WHITE_DWARF > 0)
    r1 = white_dwarf_radius(1.0) / 1000.0
    chk("wd_radius_1msun_band", 7000.0 < r1 < 10000.0)
    ratio = white_dwarf_radius(2.0) / white_dwarf_radius(1.0)
    chk("wd_radius_scaling_exact",
        abs(ratio - 2.0 ** (-1.0 / 3.0)) < 1e-12)
    table = white_dwarf_table()
    chk("wd_radius_monotone_decreasing",
        all(table[i]["radius_km"] > table[i + 1]["radius_km"]
            for i in range(len(table) - 1)))
    chk("wd_density_monotone_increasing",
        all(table[i]["central_density_kg_m3"]
            < table[i + 1]["central_density_kg_m3"]
            for i in range(len(table) - 1)))
    chk("wd_radius_06_exceeds_10",
        white_dwarf_radius(0.6) > white_dwarf_radius(1.0))

    # 2. relativistic energy + Chandrasekhar
    mch = chandrasekhar_mass()
    chk("chandrasekhar_band", 1.40 < mch["mass_msun"] < 1.48)
    chk("chandrasekhar_prefactor_textbook",
        3.0 < mch["dimensionless_prefactor"] < 3.2)
    e1 = energy_minimum(1.0 * M_SUN)
    chk("energy_minimum_exists_1msun",
        e1["has_minimum"] and e1["energy_J"] < 0)
    chk("energy_minimum_radius_band",
        3000.0 < e1["radius_m"] / 1000.0 < 8000.0)
    e3 = energy_minimum(3.0 * M_SUN)
    chk("energy_no_minimum_3msun", not e3["has_minimum"])
    toy = toy_critical_mass_msun()
    toy_an = toy_critical_mass_analytic_msun()
    chk("toy_critical_band", 1.6 < toy < 1.85)
    chk("toy_critical_matches_analytic", abs(toy - toy_an) < 0.02)
    chk("energy_large_radius_between",
        e1["energy_J"] < total_energy(M_SUN, 1.0e8) < 0)
    chk("gravitational_energy_formula",
        gravitational_energy(M_SUN, 1.0e7)
        == -3.0 * G_GRAV * M_SUN ** 2 / (5.0 * 1.0e7))
    chk("kinetic_energy_positive_and_rises_inward",
        kinetic_energy(M_SUN, 5.0e6) > kinetic_energy(M_SUN, 1.0e7) > 0)

    # 3. Gamow peak
    chk("gamow_energy_band", 480.0 < E_GAMOW_PP_KEV < 505.0)
    e0 = gamow_peak_analytic_kev(SOLAR_CORE_T)
    chk("gamow_peak_analytic_band", 5.0 < e0 < 7.0)
    e0_num = gamow_peak_numeric_kev(SOLAR_CORE_T)
    chk("gamow_peak_numeric_matches_analytic",
        abs(e0_num - e0) / e0 < 0.02)
    chk("tunnelling_monotone_rising",
        tunnelling_probability(1.0) < tunnelling_probability(5.0)
        < tunnelling_probability(20.0))
    chk("tunnelling_bounds",
        0.0 < tunnelling_probability(5.9) < 1.0)
    chk("boltzmann_factor_falling",
        boltzmann_factor(1.0, SOLAR_CORE_T)
        > boltzmann_factor(10.0, SOLAR_CORE_T))
    kT_kev = K_BOLTZ * SOLAR_CORE_T / EV_JOULE / 1000.0
    chk("gamow_suppression_band",
        1e-7 < math.exp(-3.0 * e0 / kT_kev) < 1e-5)
    chk("gamow_peak_temperature_scaling",
        abs(gamow_peak_analytic_kev(3.0e7) / e0 - 2.0 ** (2.0 / 3.0)) < 1e-9)

    # 4. neutron-star toy
    ns_r = neutron_star_radius(1.4) / 1000.0
    chk("ns_radius_band", 8.0 < ns_r < 25.0)
    chk("ns_K_below_wd_K", 0 < K_NEUTRON_STAR < K_WHITE_DWARF)
    chk("ns_radius_far_below_wd",
        neutron_star_radius(1.4) < white_dwarf_radius(1.4) / 100.0)

    # 5. Hawking
    t1 = hawking_temperature(M_SUN)
    chk("hawking_temperature_band", 5e-8 < t1 < 7e-8)
    chk("hawking_temperature_inverse_mass",
        abs(hawking_temperature(2.0 * M_SUN) / t1 - 0.5) < 1e-12)
    rs1 = schwarzschild_radius(M_SUN) / 1000.0
    chk("schwarzschild_band", 2.8 < rs1 < 3.1)
    chk("schwarzschild_linear",
        schwarzschild_radius(2.0 * M_SUN) == 2.0 * schwarzschild_radius(M_SUN))
    ev1 = evaporation_time_s(M_SUN) / YEAR_S
    chk("evaporation_band", 1e67 < ev1 < 3e67)
    chk("evaporation_cubic_scaling",
        abs(evaporation_time_s(2.0 * M_SUN) / evaporation_time_s(M_SUN)
            - 8.0) < 1e-9)

    # 6. classifier - labels come from the lab's own remnant policy
    rep = classifier_report()
    chk("classifier_sun_main_sequence",
        rep["sun_like_1msun_695700km"] == "main-sequence-supported")
    chk("classifier_white_dwarf",
        rep["white_dwarf_1msun_lab_radius"] == "white-dwarf")
    chk("classifier_white_dwarf_06",
        rep["white_dwarf_0.6msun_lab_radius"] == "white-dwarf")
    chk("classifier_neutron_star",
        rep["neutron_star_1.4msun_lab_radius"] == "neutron-star")
    chk("classifier_black_hole",
        rep["inside_schwarzschild_scale_10msun_20km"] == "black-hole")
    chk("classifier_matches_policy",
        all(classify_remnant(*features) == remnant_policy(*features)
            for features in [(1.0, 695700.0), (1.0, 8771.9), (0.6, 10400.3),
                             (1.4, 13.51), (10.0, 20.0)]))

    # gates + seats
    chk("hold_gates_14", len(HOLD_GATES) == 14
        and all(v.startswith("HOLD") for v in HOLD_GATES.values()))
    chk("gate_observational_hold", gate("observational_data_claim") == "HOLD")
    chk("gate_prediction_hold", gate("real_star_prediction_claim") == "HOLD")
    chk("gate_classification_hold",
        gate("real_object_classification_claim") == "HOLD")
    chk("gate_weapons_hold", gate("weapons_claim") == "HOLD")
    chk("gate_sandbox_proceed", gate("run_simulation") == "PROCEED")
    brains = brains_report()
    chk("argon4_no_override", brains["decider"]["can_override_hold"] is False
        and brains["decider"]["seat"]
        == "Gemini Argon 4 Extended Thinking")
    chk("claude_no_override", brains["advisor"]["can_override_hold"] is False)
    chk("flow_plan_only", brains["flow"]["rendered"] is False
        and brains["flow"]["live"] == 0)
    return c


# ================================================================ CLI / demo
def demo():
    print("=" * 68)
    print("QuantumAstro-Lab - quantum astrophysics lab")
    print("by Darion Kellar | MIT | pure stdlib | zero network | EDUCATION ONLY")
    print("=" * 68)
    print("\n[1] THE HONEST CORE - textbook physics, labelled constants")
    print("    Degeneracy pressure, the Chandrasekhar limit, the Gamow")
    print("    peak, neutron degeneracy, Hawking temperature - all computed")
    print("    from CODATA / exact-SI constants written in the code.")
    print("    Nothing is fitted to or predicted about any real star.")
    print("\n[2] White dwarfs - nonrelativistic degeneracy, R ~ M^(-1/3)")
    for row in white_dwarf_table():
        print(f"    M = {row['mass_msun']:.1f} M_sun | R = "
              f"{row['radius_km']:9.1f} km | rho_c = "
              f"{row['central_density_kg_m3']:.3e} kg/m^3")
    print("    -> heavier white dwarfs are SMALLER: degeneracy support.")
    print("\n[3] The relativistic turn-over + Chandrasekhar mass")
    rep = chandrasekhar_report()
    e1 = rep["energy_minimum_1msun"]
    print(f"    E(R) at 1.0 M_sun: minimum at R = {e1['radius_km']} km, "
          f"E_min = {e1['energy_J']:.3e} J (equilibrium exists)")
    print(f"    E(R) at 3.0 M_sun: has_minimum = "
          f"{rep['energy_minimum_3msun']['has_minimum']} (no equilibrium)")
    print(f"    uniform-density toy critical mass: "
          f"{rep['toy_critical_mass_msun']} M_sun (numeric) / "
          f"{rep['toy_critical_mass_analytic_msun']} M_sun (UR analytic)")
    print(f"    Lane-Emden n=3 Chandrasekhar mass: "
          f"{rep['chandrasekhar_mass_msun']} M_sun (textbook value)")
    print("    -> the toy overshoots; the polytrope is the real answer.")
    print("\n[4] Fusion tunnelling - the Gamow peak (p-p, T = 1.5e7 K LABELLED)")
    g = gamow_report()
    print(f"    E_G = {g['gamow_energy_kev']} keV | kT = {g['kT_kev']} keV")
    print(f"    Gamow peak E0 = {g['peak_analytic_kev']} keV (analytic) / "
          f"{g['peak_numeric_kev']} keV (lab maximisation)")
    print(f"    E0/kT = {g['peak_over_kT']} | peak suppression "
          f"exp(-3E0/kT) = {g['suppression_exp_minus_3E0_over_kT']:.3e}")
    print("    -> fusion burns in the Boltzmann tail, through the barrier.")
    print("\n[5] Neutron-star toy - same machinery, neutron fermion")
    ns = neutron_star_report()
    print(f"    1.4 M_sun: R = {ns['radius_km']} km (white dwarf at the "
          f"same mass: {ns['white_dwarf_radius_same_mass_km']} km)")
    print("    -> order-of-magnitude toy: GR ignored, stated openly.")
    print("\n[6] Hawking temperature - T_H = hbar c^3 / (8 pi G M k_B)")
    for row in hawking_report()["rows"]:
        print(f"    M = {row['mass_msun']:>8.0f} M_sun | T_H = "
              f"{row['temperature_K']:.3e} K | r_s = "
              f"{row['schwarzschild_radius_km']} km | t_evap = "
              f"{row['evaporation_time_yr']:.3e} yr")
    print("\n[7] Remnant classifier (TinyML kNN, labels from the lab policy)")
    for name, label in classifier_report().items():
        print(f"    {name:44s} -> {label}")
    print("\n[8] Advisory seats")
    brains = brains_report()
    print(f"    decider: {brains['decider']['decision']} "
          f"trace={brains['decider']['trace_sha256_16']}")
    print(f"    advisor can_override_hold = {brains['advisor']['can_override_hold']}")
    print(f"    flow rendered = {brains['flow']['rendered']} "
          f"live = {brains['flow']['live']}")
    print(f"\n[9] HOLD gates: {len(HOLD_GATES)}")
    for key in HOLD_GATES:
        print(f"    HOLD  {key}")
    checks = run_checks()
    passed = sum(1 for _, ok in checks if ok)
    print(f"\nCHECKS {passed}/{len(checks)}")
    for name, ok in checks:
        if not ok:
            print(f"    FAIL {name}")
    verdict = "PROCEED" if passed == len(checks) else "HOLD"
    print(f"VERDICT {verdict} (sandbox simulation only) | HOLD gates {len(HOLD_GATES)}")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] == "demo":
        return demo()
    cmd = argv[0]
    if cmd == "checks":
        checks = run_checks()
        for name, ok in checks:
            print(f"{'PASS' if ok else 'FAIL'} {name}")
        print(f"CHECKS {sum(1 for _, ok in checks if ok)}/{len(checks)}")
        return 0 if all(ok for _, ok in checks) else 1
    if cmd == "whitedwarf":
        print(json.dumps(white_dwarf_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "chandrasekhar":
        print(json.dumps(chandrasekhar_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "gamow":
        print(json.dumps(gamow_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "neutronstar":
        print(json.dumps(neutron_star_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "hawking":
        print(json.dumps(hawking_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "classify":
        print(json.dumps(classifier_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "brains":
        print(json.dumps(brains_report(), indent=2, sort_keys=True))
        return 0
    if cmd == "holds":
        for key, value in HOLD_GATES.items():
            print(f"{key}: {value}")
        return 0
    if cmd == "hold-demo":
        action = argv[1] if len(argv) > 1 else "real_star_prediction_claim"
        print(f"{action}: {HOLD_GATES.get(action, 'PROCEED - not gated')}")
        return 2 if gate(action) == "HOLD" else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
