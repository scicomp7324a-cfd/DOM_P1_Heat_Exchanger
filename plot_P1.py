#!/usr/bin/env python3
"""
Report-quality plotting script for the P1 radiation project.

Expected output folder structure from main.cpp:

Output/
├── ParallelPlateNoMediumVacuumClosed/
│   ├── heat_diagnostics.csv
│   ├── 300/centerlineG.csv
│   ├── 400/centerlineG.csv
│   └── ...
├── ParallelPlateParticipatingMediumClosed/
│   ├── heat_diagnostics.csv
│   ├── analytical_dimensionless_heat_flux.csv
│   ├── analytical_dimensionless_centerline_temperature.csv
│   ├── 0.1/dimensionlessCenterlineT.csv
│   ├── 1.0/dimensionlessCenterlineT.csv
│   └── ...
└── SquarePlateRadiationConduction/
    ├── analytical_dimensionless_centerline_temperature.csv
    ├── <conductivity_case>/dimensionlessCenterlineTInZ.csv
    └── ...

Usage:
    python plot_P1.py --output-root /path/to/Output
    python plot_P1.py --output-root /path/to/Output --fig-dir /path/to/Figures

The script saves both PNG and PDF versions of each plot.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator


# ---------------------------------------------------------------------
# User-adjustable defaults
# ---------------------------------------------------------------------

DEFAULT_OUTPUT_ROOT = Path("Output")
DEFAULT_FIG_DIR_NAME = "P1_report_figures"

CASE_CLOSED = "ParallelPlateNoMediumVacuumClosed"
CASE_PARTICIPATING = "ParallelPlateParticipatingMediumClosed"
CASE_CONDUCTION = "SquarePlateRadiationConductionClosed"

CLOSED_TEMPERATURE_CASES = ["300", "400", "500", "600", "700", "800", "900", "1000"]
PARTICIPATING_OPTICAL_LENGTHS = ["0.1", "0.5", "1.0", "1.5", "2.0", "2.5", "3.0", "3.5", "4.0", "5.0", "7.0", "9.0", "10.0"]
PARTICIPATING_ANALYTICAL_TAUS = ["0.1", "1.0", "2.0", "10.0"]

CONDUCTION_CASE_FOLDERS: list[str] = []


# ---------------------------------------------------------------------
# Plot styling
# ---------------------------------------------------------------------

def apply_report_style() -> None:
    """Set a readable, report-quality matplotlib style."""
    plt.rcParams.update({
        "figure.figsize": (10.5, 7.2),
        "figure.dpi": 150,
        "savefig.dpi": 400,
        "font.size": 17,
        "axes.titlesize": 21,
        "axes.labelsize": 19,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "legend.fontsize": 14,
        "lines.linewidth": 2.8,
        "lines.markersize": 7.5,
        "axes.grid": True,
        "grid.alpha": 0.30,
        "grid.linestyle": "--",
        "axes.linewidth": 1.25,
        "legend.frameon": True,
        "legend.framealpha": 0.95,
        "legend.edgecolor": "0.75",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def finish_axes(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    ax.set_title(title, pad=14, fontweight="bold")
    ax.set_xlabel(xlabel, labelpad=10)
    ax.set_ylabel(ylabel, labelpad=10)
    ax.tick_params(axis="both", which="major", length=7, width=1.15)
    ax.tick_params(axis="both", which="minor", length=4, width=0.9)
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    for spine in ax.spines.values():
        spine.set_linewidth(1.25)


def save_figure(fig: plt.Figure, fig_dir: Path, stem: str) -> None:
    fig_dir.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        out = fig_dir / f"{stem}.{ext}"
        fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------
# CSV readers
# ---------------------------------------------------------------------

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df


def read_standard_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return clean_columns(pd.read_csv(path))


def read_centerline_csv(path: Path) -> pd.DataFrame:
    """
    Reads centerline files produced by main.cpp.

    These files look like:
        west_wall_temperature,1000
        east_wall_temperature,500
        absorption_coefficient,1.0

        x_over_L, dimensionless_T
        0.0, ...
        ...

    This function searches for the real header line.
    """
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    lines = path.read_text().splitlines()
    header_idx = None
    header_tokens = (
        "x_over_L", "x_centerline_coordinate", "z_over_L",
        "y/l", "x/l"
    )

    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(stripped.startswith(tok) for tok in header_tokens):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(f"Could not find centerline header in: {path}")

    df = pd.read_csv(path, skiprows=header_idx)
    df = clean_columns(df)
    df = df.dropna(how="all")
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(how="any")
    return df


def first_existing_column(df: pd.DataFrame, candidates: Sequence[str]) -> str:
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"None of these columns found: {candidates}. Available columns: {list(df.columns)}")


def sorted_case_folders(case_dir: Path) -> list[str]:
    folders = [p.name for p in case_dir.iterdir() if p.is_dir()]
    return sorted(folders, key=lambda s: float(s))


# ---------------------------------------------------------------------
# Plot 1
# ---------------------------------------------------------------------

def plot_closed_heat_flux_vs_east_temperature(output_root: Path, fig_dir: Path) -> None:
    case_dir = output_root / CASE_CLOSED
    df = read_standard_csv(case_dir / "heat_diagnostics.csv")

    x = df["east_wall_temperature"].astype(float)

    fig, ax = plt.subplots()

    # West-wall flux is usually the cleaner representative because Twest is fixed.
    ax.plot(
        x,
        np.abs(df["west_wall_heat_flux"].astype(float)),
        marker="None",
        linestyle = "-",
        label="P1 simulated |west-wall heat flux|",
    )
    ax.plot(
        x,
        np.abs(df["west_wall_analytical_heat_flux"].astype(float)),
        marker="s",
        markerfacecolor="tab:red",
        linestyle="None",
        label="Analytical |west-wall heat flux|",
    )

    finish_axes(
        ax,
        title="Closed Parallel Plates: Heat Flux vs East-Wall Temperature",
        xlabel="East-wall temperature, $T_E$ [K]",
        ylabel="Absolute heat flux, $|q|$ [W m$^{-2}$]",
    )
    ax.legend(loc="best")
    save_figure(fig, fig_dir, "P1_plot1_closed_heat_flux_vs_east_temperature")


# ---------------------------------------------------------------------
# Plot 2
# ---------------------------------------------------------------------

def plot_closed_centerline_G_profiles(output_root: Path, fig_dir: Path) -> None:
    case_dir = output_root / CASE_CLOSED

    fig, ax = plt.subplots()

    cmap = plt.get_cmap("viridis")
    cases = CLOSED_TEMPERATURE_CASES
    for i, temp_case in enumerate(cases):
        path = case_dir / temp_case / "centerlineG.csv"
        if not path.exists():
            continue

        df = read_centerline_csv(path)
        x_col = first_existing_column(df, ["x_over_L", "x_centerline_coordinate"])
        g_col = first_existing_column(df, ["G"])

        x = df[x_col].astype(float)
        if x_col == "x_centerline_coordinate":
            # The plate length is 1 m in this case, so x and x/L are numerically equal.
            x = x / 1.0

        ax.plot(
            x,
            df[g_col].astype(float),
            marker="o",
            markevery=max(1, len(df) // 12),
            color=cmap(i / max(1, len(cases) - 1)),
            label=f"$T_E$ = {temp_case} K",
        )

    finish_axes(
        ax,
        title="Closed Parallel Plates: Centerline Irradiation Profiles",
        xlabel="Normalised coordinate, $x/L$ [-]",
        ylabel="Incident radiation, $G$ [W m$^{-2}$]",
    )
    ax.legend(loc="best", ncols=2)
    save_figure(fig, fig_dir, "P1_plot2_closed_centerline_G_profiles")


# ---------------------------------------------------------------------
# Plot 3
# ---------------------------------------------------------------------

def plot_participating_dimensionless_heat_flux(output_root: Path, fig_dir: Path) -> None:
    case_dir = output_root / CASE_PARTICIPATING
    sim = read_standard_csv(case_dir / "heat_diagnostics.csv")
    analytical = read_standard_csv(case_dir / "analytical_dimensionless_heat_flux.csv")

    x_sim = sim["absorption_coefficient"].astype(float)
    y_sim = np.abs(sim["dimensionless_heat_flux_west"].astype(float))

    x_ana = analytical["absorption_coefficient"].astype(float)
    y_ana = np.abs(analytical["dimension_heat_flux_east"].astype(float))

    fig, ax = plt.subplots()

    ax.plot(
        x_ana,
        y_ana,
        linestyle="None",
        marker="s",
        markerfacecolor="tab:red",
        markeredgecolor="tab:red",
        markeredgewidth = 4,
        label="Analytical dimensionless heat flux",
    )
    ax.plot(
        x_sim,
        y_sim,
        linestyle="--",
        marker="o",
        markerfacecolor="tab:purple",
        label="P1 simulated dimensionless heat flux",
    )

    finish_axes(
        ax,
        title="Participating Medium: Dimensionless Heat Flux vs Optical Length",
        xlabel="Optical length, $\\tau_L = aL$ [-]",
        ylabel="Dimensionless heat flux, $|\\psi|$ [-]",
    )
    ax.legend(loc="best")
    save_figure(fig, fig_dir, "P1_plot3_participating_dimensionless_heat_flux")


# ---------------------------------------------------------------------
# Plot 4
# ---------------------------------------------------------------------

def plot_participating_dimensionless_centerline_temperature(output_root: Path, fig_dir: Path) -> None:
    case_dir = output_root / CASE_PARTICIPATING
    analytical = read_standard_csv(case_dir / "analytical_dimensionless_centerline_temperature.csv")

    x_ana_col = first_existing_column(analytical, ["x/l", "x_over_L"])
    x_ana = analytical[x_ana_col].astype(float)

    fig, ax = plt.subplots()

    taus = PARTICIPATING_ANALYTICAL_TAUS

    # Independent style control for each tau_L value.
    #
    # The keys here must match the entries in PARTICIPATING_ANALYTICAL_TAUS.
    # Example:
    # PARTICIPATING_ANALYTICAL_TAUS = ["0.1", "1.0", "2.0", "10.0"]
    tau_styles = {
        "0.1": {
            "color": "tab:blue",
            "sim_marker": "None",
            "ana_marker": "s",
            "sim_markersize": 4,
            "ana_markersize": 5,
            "sim_linestyle": "-",
            "ana_linestyle": "None",
        },
        "1.0": {
            "color": "tab:orange",
            "sim_marker": "None",
            "ana_marker": "D",
            "sim_markersize": 5,
            "ana_markersize": 5,
            "sim_linestyle": "-",
            "ana_linestyle": "None",
        },
        "2.0": {
            "color": "tab:green",
            "sim_marker": "None",
            "ana_marker": "x",
            "sim_markersize": 5,
            "ana_markersize": 5,
            "sim_linestyle": "-",
            "ana_linestyle": "None",
        },
        "10.0": {
            "color": "tab:red",
            "sim_marker": "None",
            "ana_marker": "*",
            "sim_markersize": 5,
            "ana_markersize": 6,
            "sim_linestyle": "-",
            "ana_linestyle": "None",
        },
    }

    default_style = {
        "color": "black",
        "sim_marker": "o",
        "ana_marker": "s",
        "sim_markersize": 4,
        "ana_markersize": 5,
        "sim_linestyle": "-",
        "ana_linestyle": "--",
    }

    for tau in taus:
        style = tau_styles.get(str(tau), default_style)

        sim_path = case_dir / tau / "dimensionlessCenterlineT.csv"

        if sim_path.exists():
            sim = read_centerline_csv(sim_path)
            x_sim_col = first_existing_column(sim, ["x_over_L", "x/l"])
            y_sim_col = first_existing_column(sim, ["dimensionless_T"])

            ax.plot(
                sim[x_sim_col].astype(float),
                sim[y_sim_col].astype(float),

                # P1 line style
                color=style["color"],
                linestyle=style["sim_linestyle"],
                linewidth=1.5,

                # P1 marker style
                marker=style["sim_marker"],
                markersize=style["sim_markersize"],
                markerfacecolor=style["color"],
                markeredgecolor=style["color"],
                markeredgewidth=1.0,

                markevery=max(1, len(sim) // 12),
                label=f"P1 $\\tau_L$ = {tau}",
            )

        if tau in analytical.columns:
            ax.plot(
                x_ana,
                analytical[tau].astype(float),

                # Analytical line style
                color=style["color"],
                linestyle=style["ana_linestyle"],
                linewidth=1.5,

                # Analytical marker style
                marker=style["ana_marker"],
                markersize=style["ana_markersize"],
                markerfacecolor="none",
                markeredgecolor=style["color"],
                markeredgewidth=1.2,

                markevery=max(1, len(analytical) // 12),
                label=f"Analytical $\\tau_L$ = {tau}",
            )

    finish_axes(
        ax,
        title="Participating Medium: Dimensionless Centerline Temperature",
        xlabel="Normalised coordinate, $x/L$ [-]",
        ylabel="Dimensionless temperature, $T/T_W$ [-]",
    )

    ax.legend(loc="best", ncols=2)
    save_figure(fig, fig_dir, "P1_plot4_participating_dimensionless_centerline_temperature")

# ---------------------------------------------------------------------
# Plot 5
# ---------------------------------------------------------------------

def plot_conduction_dimensionless_temperature_z(output_root: Path, fig_dir: Path) -> None:
    case_dir = output_root / CASE_CONDUCTION
    analytical = read_standard_csv(case_dir / "analytical_dimensionless_centerline_temperature.csv")

    x_ana_col = first_existing_column(analytical, ["y/l", "z_over_L"])
    x_ana = analytical[x_ana_col].astype(float)

    # Analytical CSV is assumed to be ordered as:
    # y/l, N0.05, N0.1, N1
    analytical_columns = [
        ("N0.05", "$N$ = 0.05 Rousse 2000"),
        ("N0.1", "$N$ = 0.1 Rousse 2000"),
        ("N1", "$N$ = 1 Rousse 2000"),
    ]

    case_folders = CONDUCTION_CASE_FOLDERS or sorted_case_folders(case_dir)

    # Exclude accidental non-case folders if present.
    case_folders = [
        c for c in case_folders
        if (case_dir / c / "dimensionlessCenterlineTInZ.csv").exists()
    ]

    # This order must match the order of case_folders.
    stark_labels = [
        "$N$ = 0.05 P1",
        "$N$ = 0.1 P1",
        "$N$ = 1 P1",
    ]

    # Change marker colour, shape, and size here.
    marker_styles = [
        {
            "color": "tab:blue",
            "marker": "s",      # square
            "markersize": 5,
        },
        {
            "color": "tab:red",
            "marker": "o",      # circle
            "markersize": 5,
        },
        {
            "color": "tab:green",
            "marker": "^",      # triangle
            "markersize": 6,
        },
    ]

    fig, ax = plt.subplots()

    for i, (col, label) in enumerate(analytical_columns):
        if col in analytical.columns:
            style = marker_styles[i]

            ax.plot(
                x_ana,
                analytical[col].astype(float),
                linestyle="None",

                # Marker controls
                marker=style["marker"],
                markersize=style["markersize"],
                markerfacecolor="none",          # hollow marker
                markeredgecolor=style["color"],
                markeredgewidth=1.2,

                markevery=max(1, len(analytical) // 12),
                label=label,
            )

    for i, folder in enumerate(case_folders[:3]):
        sim = read_centerline_csv(case_dir / folder / "dimensionlessCenterlineTInZ.csv")
        x_sim_col = first_existing_column(sim, ["z_over_L"])
        y_sim_col = first_existing_column(sim, ["dimensionless_T"])

        label = stark_labels[i] if i < len(stark_labels) else f"P1 case {folder}"
        style = marker_styles[i]

        ax.plot(
            sim[x_sim_col].astype(float),
            sim[y_sim_col].astype(float),
            linestyle="-",

            # P1 line controls
            color=style["color"],
            linewidth=1.5,

            # No markers on P1 curves
            marker="None",

            label=label,
        )

    finish_axes(
        ax,
        title="Radiation-Conduction Square Plate: Vertical Temperature Profile",
        xlabel="Normalised vertical coordinate, $z/L$ [-]",
        ylabel="Dimensionless temperature, $T/T_W$ [-]",
    )

    ax.legend(loc="best", ncols=2)
    save_figure(fig, fig_dir, "P1_plot5_conduction_dimensionless_temperature_z")
# ---------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------

def make_all_plots(output_root: Path, fig_dir: Path) -> None:
    apply_report_style()

    plot_closed_heat_flux_vs_east_temperature(output_root, fig_dir)
    plot_closed_centerline_G_profiles(output_root, fig_dir)
    plot_participating_dimensionless_heat_flux(output_root, fig_dir)
    plot_participating_dimensionless_centerline_temperature(output_root, fig_dir)
    plot_conduction_dimensionless_temperature_z(output_root, fig_dir)

    print(f"Saved P1 report figures to: {fig_dir.resolve()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate report-quality P1 plots from CSV output files.")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Path to the root Output directory that contains the P1 case folders.",
    )
    parser.add_argument(
        "--fig-dir",
        type=Path,
        default=None,
        help="Directory where figures should be saved. Default: <output-root>/P1_report_figures",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = args.output_root.expanduser().resolve()
    fig_dir = args.fig_dir.expanduser().resolve() if args.fig_dir else output_root / DEFAULT_FIG_DIR_NAME

    make_all_plots(output_root, fig_dir)


if __name__ == "__main__":
    main()
