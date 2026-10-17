#!/usr/bin/env python3

from pathlib import Path
import sys
import csv
import pandas as pd
import matplotlib.pyplot as plt


TEST_PREFIX = "DOMP1HeatExchangerSpatialDifferenceTest"
OUTPUT_NAME = "DOMP1HeatExchangerSpatialDifferenceTest"
SPACINGS = [1.5, 2.0, 2.5]
CASE_TO_SPACING = {
    "CloseSpacing": 1.5,
    "MediumSpacing": 2.0,
    "WideSpacing": 2.5,
}

ARRANGEMENTS = {
    "AlternatingArrangement": "Alternating",
    "HotPipesSurroundedByColdPipes": "Surrounded",
}

MODELS = ["P1", "DOM"]

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

ARRANGEMENT_COLOURS = {
    "Alternating": "#E64A19",
    "Surrounded": "#1565C0",
}

MODEL_MARKERS = {
    "P1": "o",
    "DOM": "D",
}


plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 12,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def resolve_paths(root: Path):
    project_root = root.expanduser().resolve()

    if project_root.name == "ValidationTests":
        project_root = project_root.parent

    if project_root.name == TEST_PREFIX:
        if project_root.parent.name == "ValidationTests":
            project_root = project_root.parent.parent
        elif project_root.parent.name == "Output":
            project_root = project_root.parent.parent

    output_root = project_root / "Output" / OUTPUT_NAME

    if not output_root.is_dir():
        raise FileNotFoundError(
            f"Could not find simulation results directory:\n{output_root}"
        )

    if not (output_root / "P1").is_dir():
        raise FileNotFoundError(
            f"Could not find P1 results under:\n{output_root}"
        )

    if not (output_root / "DOM").is_dir():
        raise FileNotFoundError(
            f"Could not find DOM results under:\n{output_root}"
        )

    return output_root, output_root

def find_summary_file(arrangement_dir: Path, model: str):
    preferred = arrangement_dir / f"{model}_summary.csv"
    if preferred.is_file():
        return preferred

    matches = sorted(arrangement_dir.glob("*_summary.csv"))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise FileNotFoundError(f"No summary CSV found in {arrangement_dir}")
    raise RuntimeError(f"Multiple summary CSV files found in {arrangement_dir}: {matches}")


def require_columns(df: pd.DataFrame, columns, file_path: Path):
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in {file_path}: {missing}")


def read_summary_csv(file_path: Path):
    with file_path.open(newline="") as handle:
        rows = list(csv.reader(handle))

    if len(rows) < 2:
        raise ValueError(f"Summary CSV contains no data rows: {file_path}")

    header = rows[0]
    data_rows = rows[1:]
    row_lengths = {len(row) for row in data_rows}

    if len(row_lengths) != 1:
        raise ValueError(f"Inconsistent row lengths in {file_path}: {sorted(row_lengths)}")

    row_length = next(iter(row_lengths))

    if len(header) == row_length:
        return pd.DataFrame(data_rows, columns=header)

    if row_length == len(CORRECTED_SUMMARY_COLUMNS):
        return pd.DataFrame(data_rows, columns=CORRECTED_SUMMARY_COLUMNS)

    raise ValueError(
        f"Summary header/data length mismatch in {file_path}: "
        f"header has {len(header)} columns and rows have {row_length}."
    )


def read_summary_data(test_root: Path):
    required = [
        "parameter_value",
        "heat_recovery_ratio",
        "wall_loss_ratio",
        "coefficient_of_variation_cold_pipe_heat_load",
        "maximum_dimensionless_temperature",
        "maximum_dimensionless_heat_flux_magnitude",
    ]

    records = []

    for model in MODELS:
        for folder_name, arrangement_label in ARRANGEMENTS.items():
            arrangement_dir = test_root / model / folder_name
            summary_file = find_summary_file(arrangement_dir, model)
            df = read_summary_csv(summary_file)
            require_columns(df, required, summary_file)

            df["parameter_value"] = pd.to_numeric(df["parameter_value"], errors="raise")
            df = df[df["parameter_value"].isin(SPACINGS)].copy()

            if sorted(df["parameter_value"].tolist()) != SPACINGS:
                raise ValueError(
                    f"Expected spacing ratios {SPACINGS} in {summary_file}, "
                    f"found {sorted(df['parameter_value'].tolist())}."
                )

            for _, row in df.iterrows():
                records.append({
                    "model": model,
                    "arrangement": arrangement_label,
                    "spacing": float(row["parameter_value"]),
                    "heat_recovery_ratio": float(row["heat_recovery_ratio"]),
                    "wall_loss_ratio": float(row["wall_loss_ratio"]),
                    "heat_load_cv": float(row["coefficient_of_variation_cold_pipe_heat_load"]),
                    "maximum_dimensionless_temperature": float(row["maximum_dimensionless_temperature"]),
                    "maximum_dimensionless_heat_flux_magnitude": float(row["maximum_dimensionless_heat_flux_magnitude"]),
                })

    return pd.DataFrame(records)


def read_midpoint_data(test_root: Path):
    records = []

    for model in MODELS:
        for folder_name, arrangement_label in ARRANGEMENTS.items():
            extended_dir = test_root / model / folder_name / "ExtendedDiagnostics"
            midpoint_files = sorted(extended_dir.glob("*/midpoint_diagnostics.csv"))

            if not midpoint_files:
                raise FileNotFoundError(f"No midpoint diagnostics found under {extended_dir}")

            spacing_seen = set()

            for midpoint_file in midpoint_files:
                df = pd.read_csv(midpoint_file)
                require_columns(
                    df,
                    ["temperature", "hot_pipe_temperature", "cold_pipe_temperature"],
                    midpoint_file,
                )

                case_name = midpoint_file.parent.name
                if "case_name" in df.columns and not df.empty:
                    case_name = str(df["case_name"].iloc[0])

                if case_name not in CASE_TO_SPACING:
                    continue

                spacing = CASE_TO_SPACING[case_name]
                spacing_seen.add(spacing)

                temperature = pd.to_numeric(df["temperature"], errors="raise")
                hot_temperature = pd.to_numeric(df["hot_pipe_temperature"], errors="raise")
                cold_temperature = pd.to_numeric(df["cold_pipe_temperature"], errors="raise")

                denominator = hot_temperature - cold_temperature
                if (denominator == 0.0).any():
                    raise ZeroDivisionError(f"Hot and cold pipe temperatures are equal in {midpoint_file}")

                theta_mid = (temperature - cold_temperature) / denominator

                records.append({
                    "model": model,
                    "arrangement": arrangement_label,
                    "spacing": spacing,
                    "average_midpoint_dimensionless_temperature": float(theta_mid.mean()),
                })

            if spacing_seen != set(SPACINGS):
                raise ValueError(
                    f"Expected midpoint files for spacings {SPACINGS} under {extended_dir}, "
                    f"found {sorted(spacing_seen)}."
                )

    return pd.DataFrame(records)


def save_figure(fig, output_root: Path, filename: str):
    fig.savefig(output_root / f"{filename}.pdf", bbox_inches="tight")
    fig.savefig(output_root / f"{filename}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def padded_limits(values, lower_floor=None, upper_ceiling=None, padding_fraction=0.10):
    values = pd.Series(values).dropna().astype(float)
    ymin = values.min()
    ymax = values.max()
    span = ymax - ymin
    if span == 0.0:
        span = max(abs(ymax), 1.0) * 0.1

    lower = ymin - padding_fraction * span
    upper = ymax + padding_fraction * span

    if lower_floor is not None:
        lower = max(lower, lower_floor)
    if upper_ceiling is not None:
        upper = min(upper, upper_ceiling)

    return lower, upper


def plot_metric(data: pd.DataFrame, y_column: str, ylabel: str, title: str,
                output_root: Path, filename: str, y_limits=None):
    fig, ax = plt.subplots(figsize=(9.4, 5.8))

    for arrangement in ["Alternating", "Surrounded"]:
        for model in MODELS:
            subset = data[
                (data["arrangement"] == arrangement) &
                (data["model"] == model)
            ].sort_values("spacing")

            ax.scatter(
                subset["spacing"],
                subset[y_column],
                s=130,
                marker=MODEL_MARKERS[model],
                c=ARRANGEMENT_COLOURS[arrangement],
                edgecolors="black",
                linewidths=0.9,
                alpha=0.95,
                label=f"{model} -- {arrangement}",
                zorder=3,
            )

    ax.set_xlabel(r"Tube spacing, $S/D$")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(SPACINGS)
    ax.set_xlim(1.38, 2.62)

    if y_limits is not None:
        ax.set_ylim(*y_limits)
    else:
        ax.set_ylim(*padded_limits(data[y_column]))

    ax.grid(True, which="major", alpha=0.22, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)

    fig.tight_layout()
    save_figure(fig, output_root, filename)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python plot_DOMP1HeatExchangerSpatialDifferenceTest.py <project_root>\n"
            "The project root should contain ValidationTests and Output."
        )
        sys.exit(1)

    test_root, output_root = resolve_paths(Path(sys.argv[1]))

    summary = read_summary_data(test_root)
    midpoint = read_midpoint_data(test_root)
    data = summary.merge(
        midpoint,
        on=["model", "arrangement", "spacing"],
        how="inner",
        validate="one_to_one",
    )

    if len(data) != 12:
        raise ValueError(f"Expected 12 model/arrangement/spacing combinations, found {len(data)}.")

    plot_metric(
        data,
        "heat_recovery_ratio",
        r"$Q_{\mathrm{cold}}/Q_{\mathrm{hot}}$",
        "Heat recovery ratio vs tube spacing",
        output_root,
        "01_heat_recovery_ratio_vs_spacing",
        y_limits=(0.0, 1.0),
    )

    plot_metric(
        data,
        "wall_loss_ratio",
        r"$Q_{\mathrm{wall}}/Q_{\mathrm{hot}}$",
        "Wall loss ratio vs tube spacing",
        output_root,
        "02_wall_loss_ratio_vs_spacing",
        y_limits=(0.0, 1.0),
    )

    plot_metric(
        data,
        "heat_load_cv",
        r"Cold-pipe heat-load $\mathrm{CV}_{Q}$",
        "Cold-pipe heat-load uniformity vs tube spacing",
        output_root,
        "03_heat_load_uniformity_vs_spacing",
    )

    plot_metric(
        data,
        "average_midpoint_dimensionless_temperature",
        r"$\overline{\theta}_{\mathrm{mid}}$",
        "Average inter-tube midpoint temperature vs tube spacing",
        output_root,
        "04_average_midpoint_dimensionless_temperature_vs_spacing",
        y_limits=(0.65, 0.85),
    )

    plot_metric(
        data,
        "maximum_dimensionless_temperature",
        r"$\theta_{\max}$",
        "Maximum medium temperature vs tube spacing",
        output_root,
        "05_maximum_dimensionless_temperature_vs_spacing",
        y_limits=(0.0, 1.0),
    )

    plot_metric(
        data,
        "maximum_dimensionless_heat_flux_magnitude",
        r"$q^*_{\max}$",
        "Maximum radiative heat-flux magnitude vs tube spacing",
        output_root,
        "06_maximum_dimensionless_heat_flux_magnitude_vs_spacing",
    )

    print(f"Input directory : {test_root}")
    print(f"Output directory: {output_root}")
    print("Created 6 figures, each saved as PDF and PNG.")


if __name__ == "__main__":
    main()
