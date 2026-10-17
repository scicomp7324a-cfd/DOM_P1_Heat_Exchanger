#!/usr/bin/env python3

from pathlib import Path
import sys
import csv
import warnings

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


OPTICAL_TEST_NAME = "DOMP1HeatExchangerOpticalThicknessTest"
SPATIAL_TEST_NAME = "DOMP1HeatExchangerSpatialDifferenceTest"

MATCHED_TAU = [0.05, 0.10, 0.15]
SPATIAL_CASE_TO_TAU = {
    "CloseSpacing": 0.05,
    "MediumSpacing": 0.10,
    "WideSpacing": 0.15,
}
OPTICAL_CASE_TO_TAU = {
    "opticalThickness0.050000": 0.05,
    "opticalThickness0.100000": 0.10,
    "opticalThickness0.150000": 0.15,
}

ARRANGEMENTS = {
    "AlternatingArrangement": "Alternating",
    "HotPipesSurroundedByColdPipes": "Surrounded",
}
MODELS = ["P1", "DOM"]

ARRANGEMENT_COLOURS = {
    "Alternating": "#E64A19",
    "Surrounded": "#1565C0",
}
MODEL_MARKERS = {
    "P1": "o",
    "DOM": "D",
}


CORRECTED_SUMMARY_COLUMNS = [
    "parameter_name",
    "parameter_value",
    "absorption_coefficient",
    "scattering_coefficient",
    "hot_pipe_temperature",
    "cold_pipe_temperature",
    "outer_wall_temperature",
    "initial_medium_temperature",
    "minimum_irradiation",
    "minimum_dimensionless_irradiation",
    "minimum_irradiation_x",
    "minimum_irradiation_y",
    "minimum_irradiation_z",
    "maximum_irradiation",
    "maximum_dimensionless_irradiation",
    "maximum_irradiation_x",
    "maximum_irradiation_y",
    "maximum_irradiation_z",
    "minimum_temperature",
    "minimum_dimensionless_temperature",
    "minimum_temperature_x",
    "minimum_temperature_y",
    "minimum_temperature_z",
    "maximum_temperature",
    "maximum_dimensionless_temperature",
    "maximum_temperature_x",
    "maximum_temperature_y",
    "maximum_temperature_z",
    "minimum_heat_flux_magnitude",
    "minimum_dimensionless_heat_flux_magnitude",
    "minimum_heat_flux_x",
    "minimum_heat_flux_y",
    "minimum_heat_flux_z",
    "maximum_heat_flux_magnitude",
    "maximum_dimensionless_heat_flux_magnitude",
    "maximum_heat_flux_x",
    "maximum_heat_flux_y",
    "maximum_heat_flux_z",
    "total_hot_pipe_heat_release",
    "total_cold_pipe_heat_absorption",
    "total_outer_wall_heat_loss",
    "heat_recovery_ratio",
    "wall_loss_ratio",
    "mean_cold_pipe_heat_load",
    "standard_deviation_cold_pipe_heat_load",
    "coefficient_of_variation_cold_pipe_heat_load",
    "minimum_cold_pipe_heat_load",
    "maximum_cold_pipe_heat_load",
    "average_temperature",
    "average_irradiation",
    "total_radiative_source_term",
    "energy_balance_residual",
    "energy_balance_error",
    "runtime",
    "total_iteration_count",
]


plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 12,
    "ytick.labelsize": 13,
    "legend.fontsize": 11,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def resolve_project_root(root: Path) -> Path:
    root = root.expanduser().resolve()

    if root.name in {OPTICAL_TEST_NAME, SPATIAL_TEST_NAME}:
        if root.parent.name in {"ValidationTests", "Output"}:
            root = root.parent.parent

    if root.name in {"ValidationTests", "Output"}:
        root = root.parent

    if not (root / "Output").is_dir():
        raise FileNotFoundError(f"Could not find Output directory under:\n{root}")

    return root


def read_summary_csv(file_path: Path) -> pd.DataFrame:
    with file_path.open(newline="") as handle:
        rows = list(csv.reader(handle))

    if len(rows) < 2:
        raise ValueError(f"Summary CSV contains no data rows: {file_path}")

    header = rows[0]
    data_rows = rows[1:]
    row_lengths = {len(row) for row in data_rows}

    if len(row_lengths) != 1:
        raise ValueError(
            f"Inconsistent summary row lengths in {file_path}: {sorted(row_lengths)}"
        )

    row_length = next(iter(row_lengths))

    if len(header) == row_length:
        return pd.DataFrame(data_rows, columns=header)

    if row_length == len(CORRECTED_SUMMARY_COLUMNS):
        return pd.DataFrame(data_rows, columns=CORRECTED_SUMMARY_COLUMNS)

    raise ValueError(
        f"Summary header/data mismatch in {file_path}: header has {len(header)} "
        f"columns, data rows have {row_length}."
    )


def require_columns(df: pd.DataFrame, columns, file_path: Path) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in {file_path}: {missing}")


def find_summary_file(arrangement_dir: Path, model: str) -> Path:
    preferred = arrangement_dir / f"{model}_summary.csv"
    if preferred.is_file():
        return preferred

    matches = sorted(arrangement_dir.glob("*_summary.csv"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"No summary CSV found in {arrangement_dir}")
    raise RuntimeError(f"Multiple summary CSV files found in {arrangement_dir}: {matches}")


def read_summary_metric(output_root: Path, study: str) -> pd.DataFrame:
    required = [
        "parameter_value",
        "heat_recovery_ratio",
        "maximum_heat_flux_magnitude",
    ]

    records = []

    for model in MODELS:
        for arrangement_folder, arrangement_label in ARRANGEMENTS.items():
            arrangement_dir = output_root / model / arrangement_folder
            summary_file = find_summary_file(arrangement_dir, model)
            df = read_summary_csv(summary_file)
            require_columns(df, required, summary_file)

            for column in required:
                df[column] = pd.to_numeric(df[column], errors="raise")

            for _, row in df.iterrows():
                parameter_value = float(row["parameter_value"])

                if study == "Optical":
                    tau = parameter_value
                elif study == "Geometry":
                    tau_map = {1.5: 0.05, 2.0: 0.10, 2.5: 0.15}
                    if parameter_value not in tau_map:
                        continue
                    tau = tau_map[parameter_value]
                else:
                    raise ValueError(f"Unknown study type: {study}")

                if tau not in MATCHED_TAU:
                    continue

                records.append({
                    "study": study,
                    "model": model,
                    "arrangement": arrangement_label,
                    "tau": tau,
                    "heat_recovery_ratio": float(row["heat_recovery_ratio"]),
                    "maximum_heat_flux_magnitude": float(row["maximum_heat_flux_magnitude"]),
                })

    result = pd.DataFrame(records)
    expected = len(MODELS) * len(ARRANGEMENTS) * len(MATCHED_TAU)
    if len(result) != expected:
        raise ValueError(
            f"Expected {expected} summary records for {study}, found {len(result)}."
        )
    return result


def read_midpoint_metric(output_root: Path, study: str) -> pd.DataFrame:
    records = []

    if study == "Geometry":
        case_to_tau = SPATIAL_CASE_TO_TAU
    elif study == "Optical":
        case_to_tau = OPTICAL_CASE_TO_TAU
    else:
        raise ValueError(f"Unknown study type: {study}")

    for model in MODELS:
        for arrangement_folder, arrangement_label in ARRANGEMENTS.items():
            extended_dir = output_root / model / arrangement_folder / "ExtendedDiagnostics"
            if not extended_dir.is_dir():
                raise FileNotFoundError(f"ExtendedDiagnostics not found: {extended_dir}")

            seen = set()
            for case_name, tau in case_to_tau.items():
                midpoint_file = extended_dir / case_name / "midpoint_diagnostics.csv"
                if not midpoint_file.is_file():
                    raise FileNotFoundError(f"Midpoint diagnostics not found: {midpoint_file}")

                df = pd.read_csv(midpoint_file)
                require_columns(df, ["temperature"], midpoint_file)
                temperature = pd.to_numeric(df["temperature"], errors="raise")

                records.append({
                    "study": study,
                    "model": model,
                    "arrangement": arrangement_label,
                    "tau": tau,
                    "average_midpoint_temperature": float(temperature.mean()),
                })
                seen.add(tau)

            if seen != set(MATCHED_TAU):
                raise ValueError(
                    f"Expected midpoint cases {MATCHED_TAU} under {extended_dir}, "
                    f"found {sorted(seen)}."
                )

    result = pd.DataFrame(records)
    expected = len(MODELS) * len(ARRANGEMENTS) * len(MATCHED_TAU)
    if len(result) != expected:
        raise ValueError(
            f"Expected {expected} midpoint records for {study}, found {len(result)}."
        )
    return result


def check_common_medium_case(data: pd.DataFrame, value_column: str, atol: float = 1e-8) -> None:
    medium = data[data["tau"] == 0.10]

    for arrangement in ARRANGEMENTS.values():
        for model in MODELS:
            subset = medium[
                (medium["arrangement"] == arrangement) &
                (medium["model"] == model)
            ]
            if set(subset["study"]) != {"Geometry", "Optical"}:
                continue

            geom = float(subset[subset["study"] == "Geometry"][value_column].iloc[0])
            optical = float(subset[subset["study"] == "Optical"][value_column].iloc[0])
            scale = max(abs(geom), abs(optical), 1.0)
            if abs(geom - optical) > atol * scale:
                warnings.warn(
                    f"Medium matched case differs for {arrangement}, {model}, "
                    f"{value_column}: Geometry={geom}, Optical={optical}"
                )


def padded_limits(values, padding_fraction=0.10, lower_floor=None):
    series = pd.Series(values).dropna().astype(float)
    ymin = float(series.min())
    ymax = float(series.max())
    span = ymax - ymin
    if span == 0.0:
        span = max(abs(ymax), 1.0) * 0.10

    lower = ymin - padding_fraction * span
    upper = ymax + padding_fraction * span

    if lower_floor is not None:
        lower = max(lower, lower_floor)

    return lower, upper


def add_compact_legends(ax):
    arrangement_handles = [
        Line2D([0], [0], marker="o", linestyle="None", markersize=9,
               markerfacecolor=colour, markeredgecolor="black", label=label)
        for label, colour in ARRANGEMENT_COLOURS.items()
    ]
    model_handles = [
        Line2D([0], [0], marker=marker, linestyle="None", markersize=9,
               markerfacecolor="0.75", markeredgecolor="black", label=model)
        for model, marker in MODEL_MARKERS.items()
    ]
    study_handles = [
        Line2D([0], [0], marker="o", linestyle="--", linewidth=1.8,
               markersize=8, markerfacecolor="0.35", markeredgecolor="black",
               label=r"Spacing: vary $S/D$"),
        Line2D([0], [0], marker="o", linestyle="-.", linewidth=1.8,
               markersize=9, markerfacecolor="none", markeredgecolor="0.25",
               markeredgewidth=1.8, label=r"Optical: vary $a$"),
    ]

    legend1 = ax.legend(
        handles=arrangement_handles,
        title="Arrangement",
        loc="upper left",
        bbox_to_anchor=(1.015, 1.00),
        frameon=False,
    )
    ax.add_artist(legend1)

    legend2 = ax.legend(
        handles=model_handles,
        title="Radiation model",
        loc="upper left",
        bbox_to_anchor=(1.015, 0.67),
        frameon=False,
    )
    ax.add_artist(legend2)

    ax.legend(
        handles=study_handles,
        title="Matched variation",
        loc="upper left",
        bbox_to_anchor=(1.015, 0.38),
        frameon=False,
    )


def save_figure(fig, output_root: Path, filename: str) -> None:
    fig.savefig(output_root / f"{filename}.pdf", bbox_inches="tight")
    fig.savefig(output_root / f"{filename}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def plot_matched_metric(
    data: pd.DataFrame,
    value_column: str,
    ylabel: str,
    title: str,
    output_root: Path,
    filename: str,
    y_limits=None,
    scientific_y=False,
):
    fig, ax = plt.subplots(figsize=(10.8, 6.2))

    study_style = {
        "Geometry": {
            "linestyle": "--",
            "linewidth": 1.8,
            "marker_size": 105,
            "filled": True,
        },
        "Optical": {
            "linestyle": "-.",
            "linewidth": 1.8,
            "marker_size": 155,
            "filled": False,
        },
    }

    for arrangement in ["Alternating", "Surrounded"]:
        colour = ARRANGEMENT_COLOURS[arrangement]

        for model in MODELS:
            marker = MODEL_MARKERS[model]

            for study in ["Geometry", "Optical"]:
                subset = data[
                    (data["arrangement"] == arrangement) &
                    (data["model"] == model) &
                    (data["study"] == study)
                ].sort_values("tau")

                x = subset["tau"].to_numpy()
                y = subset[value_column].to_numpy()
                style = study_style[study]

                ax.plot(
                    x,
                    y,
                    linestyle=style["linestyle"],
                    linewidth=style["linewidth"],
                    color=colour,
                    alpha=0.90,
                    zorder=2,
                )

                if style["filled"]:
                    ax.scatter(
                        x,
                        y,
                        s=style["marker_size"],
                        marker=marker,
                        c=colour,
                        edgecolors="black",
                        linewidths=0.9,
                        zorder=4,
                    )
                else:
                    ax.scatter(
                        x,
                        y,
                        s=style["marker_size"],
                        marker=marker,
                        facecolors="none",
                        edgecolors=colour,
                        linewidths=2.0,
                        zorder=5,
                    )

    ax.set_xlabel(r"Matched inter-tube optical thickness, $\tau_g$")
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    ax.set_xticks(MATCHED_TAU)
    ax.set_xticklabels([
        r"$\tau_g=0.05$" + "\n" + r"Close $\leftrightarrow$ $a=0.5$",
        r"$\tau_g=0.10$" + "\n" + r"Medium $\leftrightarrow$ $a=1.0$",
        r"$\tau_g=0.15$" + "\n" + r"Wide $\leftrightarrow$ $a=1.5$",
    ])
    ax.set_xlim(0.035, 0.165)

    if y_limits is not None:
        ax.set_ylim(*y_limits)
    else:
        ax.set_ylim(*padded_limits(data[value_column], lower_floor=0.0))

    if scientific_y:
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

    ax.grid(True, which="major", alpha=0.22, linewidth=0.8)
    ax.set_axisbelow(True)
    add_compact_legends(ax)

    fig.subplots_adjust(right=0.73, bottom=0.18)
    save_figure(fig, output_root, filename)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python plot_DOMP1HeatExchangerOpticalSpatialComparison.py <project_root>\n"
            "Example (run from project root):\n"
            "  python3 ValidationTests/DOMP1HeatExchangerOpticalThicknessTest/"
            "plot_DOMP1HeatExchangerOpticalSpatialComparison.py ."
        )
        sys.exit(1)

    project_root = resolve_project_root(Path(sys.argv[1]))

    optical_root = project_root / "Output" / OPTICAL_TEST_NAME
    spatial_root = project_root / "Output" / SPATIAL_TEST_NAME

    if not optical_root.is_dir():
        raise FileNotFoundError(f"Optical-thickness output directory not found:\n{optical_root}")
    if not spatial_root.is_dir():
        raise FileNotFoundError(f"Spatial-difference output directory not found:\n{spatial_root}")

    output_root = optical_root

    optical_summary = read_summary_metric(optical_root, "Optical")
    spatial_summary = read_summary_metric(spatial_root, "Geometry")
    summary = pd.concat([spatial_summary, optical_summary], ignore_index=True)

    optical_midpoint = read_midpoint_metric(optical_root, "Optical")
    spatial_midpoint = read_midpoint_metric(spatial_root, "Geometry")
    midpoint = pd.concat([spatial_midpoint, optical_midpoint], ignore_index=True)

    check_common_medium_case(summary, "heat_recovery_ratio")
    check_common_medium_case(summary, "maximum_heat_flux_magnitude")
    check_common_medium_case(midpoint, "average_midpoint_temperature")

    plot_matched_metric(
        summary,
        "heat_recovery_ratio",
        r"$Q_{\mathrm{cold}}/Q_{\mathrm{hot}}$",
        "Matched heat-recovery ratio",
        output_root,
        "01_matched_heat_recovery_ratio",
        y_limits=(0.45, 0.90),
    )

    plot_matched_metric(
        midpoint,
        "average_midpoint_temperature",
        r"Average midpoint temperature, $\overline{T}_{\mathrm{mid}}$ (K)",
        "Matched average inter-tube midpoint temperature",
        output_root,
        "02_matched_average_midpoint_temperature",
    )

    plot_matched_metric(
        summary,
        "maximum_heat_flux_magnitude",
        r"Maximum heat-flux magnitude, $|\mathbf{q}_r|_{\max}$ (W m$^{-2}$)",
        "Matched maximum radiative heat-flux magnitude",
        output_root,
        "03_matched_maximum_heat_flux_magnitude",
        scientific_y=True,
    )

    print(f"Optical input : {optical_root}")
    print(f"Spatial input : {spatial_root}")
    print(f"Figure output : {output_root}")
    print("Created 3 matched-comparison figures, each saved as PDF and PNG.")


if __name__ == "__main__":
    main()
