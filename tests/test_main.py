"""Tests for QuantumAstro-Lab: degeneracy, Chandrasekhar, Gamow, Hawking, gates."""
import math
import subprocess
import sys
from pathlib import Path

import pytest

import main as m

ROOT = Path(__file__).resolve().parent.parent


# ---- constants
def test_hbar_derived():
    assert m.HBAR == m.H_PLANCK / (2.0 * math.pi)


def test_particle_mass_ordering():
    assert m.M_NEUTRON > m.M_PROTON > m.M_ELECTRON


# ---- white-dwarf polytrope
def test_wd_radius_1msun_band():
    assert 7000.0 < m.white_dwarf_radius(1.0) / 1000.0 < 10000.0


def test_wd_radius_scaling_exact():
    ratio = m.white_dwarf_radius(2.0) / m.white_dwarf_radius(1.0)
    assert ratio == pytest.approx(2.0 ** (-1.0 / 3.0), abs=1e-12)


def test_wd_heavier_is_smaller():
    radii = [m.white_dwarf_radius(x) for x in (0.4, 0.6, 0.8, 1.0, 1.2, 1.4)]
    assert radii == sorted(radii, reverse=True)


def test_wd_central_density_rises_with_mass():
    table = m.white_dwarf_table()
    dens = [row["central_density_kg_m3"] for row in table]
    assert dens == sorted(dens)


def test_wd_K_positive():
    assert m.K_WHITE_DWARF > 0
    assert m.degeneracy_K(m.M_ELECTRON, 2.0 * m.M_PROTON) == m.K_WHITE_DWARF


# ---- Chandrasekhar + energy minimum
def test_chandrasekhar_band():
    assert 1.40 < m.chandrasekhar_mass()["mass_msun"] < 1.48


def test_chandrasekhar_prefactor():
    assert 3.0 < m.chandrasekhar_mass()["dimensionless_prefactor"] < 3.2


def test_energy_minimum_exists_1msun():
    e = m.energy_minimum(m.M_SUN)
    assert e["has_minimum"] and e["energy_J"] < 0
    assert 3000.0 < e["radius_m"] / 1000.0 < 8000.0


def test_energy_no_minimum_3msun():
    assert not m.energy_minimum(3.0 * m.M_SUN)["has_minimum"]


def test_toy_critical_matches_analytic():
    assert abs(m.toy_critical_mass_msun()
               - m.toy_critical_mass_analytic_msun()) < 0.02


def test_toy_critical_band():
    assert 1.6 < m.toy_critical_mass_msun() < 1.85


def test_gravitational_energy_formula():
    assert m.gravitational_energy(m.M_SUN, 1.0e7) == (
        -3.0 * m.G_GRAV * m.M_SUN ** 2 / (5.0 * 1.0e7))


def test_kinetic_energy_rises_inward():
    assert m.kinetic_energy(m.M_SUN, 5.0e6) > m.kinetic_energy(m.M_SUN, 1.0e7) > 0


# ---- Gamow peak
def test_gamow_energy_band():
    assert 480.0 < m.E_GAMOW_PP_KEV < 505.0


def test_gamow_peak_analytic_band():
    assert 5.0 < m.gamow_peak_analytic_kev(1.5e7) < 7.0


def test_gamow_peak_numeric_matches_analytic():
    e0 = m.gamow_peak_analytic_kev(1.5e7)
    assert abs(m.gamow_peak_numeric_kev(1.5e7) - e0) / e0 < 0.02


def test_gamow_peak_temperature_scaling():
    ratio = m.gamow_peak_analytic_kev(3.0e7) / m.gamow_peak_analytic_kev(1.5e7)
    assert ratio == pytest.approx(2.0 ** (2.0 / 3.0), abs=1e-9)


def test_tunnelling_monotone_and_bounded():
    vals = [m.tunnelling_probability(e) for e in (1.0, 5.0, 20.0)]
    assert vals == sorted(vals)
    assert all(0.0 < v < 1.0 for v in vals)


def test_tunnelling_rejects_nonpositive():
    with pytest.raises(ValueError):
        m.tunnelling_probability(0.0)


def test_boltzmann_factor_falling():
    assert (m.boltzmann_factor(1.0, 1.5e7)
            > m.boltzmann_factor(10.0, 1.5e7))


def test_gamow_report_suppression():
    rep = m.gamow_report()
    assert 1e-7 < rep["suppression_exp_minus_3E0_over_kT"] < 1e-5


# ---- neutron-star toy
def test_ns_radius_band():
    assert 8.0 < m.neutron_star_radius(1.4) / 1000.0 < 25.0


def test_ns_far_smaller_than_wd():
    assert m.neutron_star_radius(1.4) < m.white_dwarf_radius(1.4) / 100.0


def test_ns_K_below_wd_K():
    assert 0 < m.K_NEUTRON_STAR < m.K_WHITE_DWARF


# ---- Hawking
def test_hawking_temperature_band():
    assert 5e-8 < m.hawking_temperature(m.M_SUN) < 7e-8


def test_hawking_temperature_inverse_mass():
    assert m.hawking_temperature(2.0 * m.M_SUN) == pytest.approx(
        m.hawking_temperature(m.M_SUN) / 2.0, rel=1e-12)


def test_schwarzschild_band_and_linear():
    assert 2.8 < m.schwarzschild_radius(m.M_SUN) / 1000.0 < 3.1
    assert (m.schwarzschild_radius(2.0 * m.M_SUN)
            == 2.0 * m.schwarzschild_radius(m.M_SUN))


def test_evaporation_band_and_cubic():
    assert 1e67 < m.evaporation_time_s(m.M_SUN) / m.YEAR_S < 3e67
    ratio = m.evaporation_time_s(2.0 * m.M_SUN) / m.evaporation_time_s(m.M_SUN)
    assert ratio == pytest.approx(8.0, abs=1e-9)


# ---- classifier
def test_classifier_scenarios():
    rep = m.classifier_report()
    assert rep["sun_like_1msun_695700km"] == "main-sequence-supported"
    assert rep["white_dwarf_1msun_lab_radius"] == "white-dwarf"
    assert rep["neutron_star_1.4msun_lab_radius"] == "neutron-star"
    assert rep["inside_schwarzschild_scale_10msun_20km"] == "black-hole"


def test_classifier_matches_policy():
    for features in [(1.0, 695700.0), (1.0, 8771.9), (1.4, 13.51), (10.0, 20.0)]:
        assert m.classify_remnant(*features) == m.remnant_policy(*features)


def test_policy_schwarzschild_boundary():
    rs_km = m.schwarzschild_radius(10.0 * m.M_SUN) / 1000.0
    assert m.remnant_policy(10.0, rs_km) == "black-hole"
    assert m.remnant_policy(10.0, 3.0 * rs_km) == "neutron-star"


# ---- gates + seats
def test_hold_gates_14():
    assert len(m.HOLD_GATES) == 14
    assert all(v.startswith("HOLD") for v in m.HOLD_GATES.values())


def test_gates_hold_and_proceed():
    assert m.gate("real_star_prediction_claim") == "HOLD"
    assert m.gate("weapons_claim") == "HOLD"
    assert m.gate("run_simulation") == "PROCEED"


def test_seats_never_override():
    brains = m.brains_report()
    assert brains["decider"]["can_override_hold"] is False
    assert brains["decider"]["seat"] == "Gemini Argon 4 Extended Thinking"
    assert brains["advisor"]["can_override_hold"] is False
    assert brains["flow"]["rendered"] is False and brains["flow"]["live"] == 0


def test_checks_all_pass():
    checks = m.run_checks()
    assert all(ok for _, ok in checks), [n for n, ok in checks if not ok]


# ---- CLI behaviour
def test_hold_demo_exits_2():
    proc = subprocess.run(
        [sys.executable, "main.py", "hold-demo"],
        cwd=ROOT, capture_output=True, text=True)
    assert proc.returncode == 2
    assert "HOLD" in proc.stdout


def test_demo_deterministic():
    runs = []
    for _ in range(2):
        proc = subprocess.run(
            [sys.executable, "main.py", "demo"],
            cwd=ROOT, capture_output=True, text=True)
        assert proc.returncode == 0
        runs.append(proc.stdout)
    assert runs[0] == runs[1]
