#!/usr/bin/env python3

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


TEST_NAME = "DOMP1HeatExchangerTemperatureDifferenceTest"

TEMPERATURE_DIFFERENCES = [900.0, 1000.0, 1100.0, 1200.0, 1300.0]

ARRANGEMENTS = {
    "AlternatingArrangement": "Alternating",
    "HotPipesSurroundedByColdPipes": "Surrounded",
}

MODELS = ["P1", "DOM"]

MODEL_LINESTYLES = {
    "P1": "-",
    "DOM": "--",
}

PARAMETER_MARKERS = ["o", "s", "^", "D", "v"]


plt.rcParams.update({
    "font.size": 14,
    "axes.titlesize": 18,
    "axes.labelsize": 16,
    "xtick.labelsize": 13,
    "ytick.labelsize": 13,
    "legend.fontsize": 11,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def resolve_paths(root: Path):
    project_root = root.expanduser().resolve()

    if project_root.name == "ValidationTests":
        project_root = project_root.parent

    if project_root.name == TEST_NAME:
        if project_root.parent.name in {"ValidationTests", "Output"}:
            project_root = project_root.parent.parent

    output_root = project_root / "Output" / TEST_NAME

    if not output_root.is_dir():
        raise FileNotFoundError(
            f"Could not find simulation results directory:\n{output_root}"
        )

    for model in MODELS:
        if not (output_root / model).is_dir():
            raise FileNotFoundError(
                f"Could not find {model} results under:\n{output_root}"
            )

    return output_root, output_root


def require_columns(df: pd.DataFrame, columns, file_path: Path):
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in {file_path}: {missing}")


def read_profile_data(test_root: Path):
    required_columns = [
        "hot_pipe_temperature",
        "cold_pipe_temperature",
        "x_over_L",
        "dimensionless_temperature",
        "dimensionless_heat_flux_magnitude",
    ]

    records = []

    for model in MODELS:
        for arrangement_folder, arrangement_label in ARRANGEMENTS.items():
            extended_dir = (
                test_root
                / model
                / arrangement_folder
                / "ExtendedDiagnostics"
            )

            if not extended_dir.is_dir():
                raise FileNotFoundError(
                    f"ExtendedDiagnostics directory not found:\n{extended_dir}"
                )

            profile_files = sorted(
                extended_dir.glob("*/central_inter_row_profile.csv")
            )

            if not profile_files:
                raise FileNotFoundError(
                    f"No central inter-row profiles found under:\n{extended_dir}"
                )

            temperature_differences_seen = set()

            for profile_file in profile_files:
                df = pd.read_csv(profile_file)
                require_columns(df, required_columns, profile_file)

                hot_temperature = pd.to_numeric(
                    df["hot_pipe_temperature"],
                    errors="raise",
                )
                cold_temperature = pd.to_numeric(
                    df["cold_pipe_temperature"],
                    errors="raise",
                )

                unique_hot = hot_temperature.unique()
                unique_cold = cold_temperature.unique()

                if len(unique_hot) != 1 or len(unique_cold) != 1:
                    raise ValueError(
                        f"Expected one hot and one cold tube temperature "
                        f"in {profile_file}."
                    )

                delta_t = float(unique_hot[0] - unique_cold[0])

                if not any(
                    abs(delta_t - expected) < 1.0e-10
                    for expected in TEMPERATURE_DIFFERENCES
                ):
                    continue

                temperature_differences_seen.add(delta_t)

                x_over_L = pd.to_numeric(
                    df["x_over_L"],
                    errors="raise",
                )
                theta = pd.to_numeric(
                    df["dimensionless_temperature"],
                    errors="raise",
                )
                q_star = pd.to_numeric(
                    df["dimensionless_heat_flux_magnitude"],
                    errors="raise",
                )

                profile = pd.DataFrame({
                    "model": model,
                    "arrangement": arrangement_label,
                    "temperature_difference": delta_t,
                    "hot_pipe_temperature": float(unique_hot[0]),
                    "cold_pipe_temperature": float(unique_cold[0]),
                    "x_over_L": x_over_L,
                    "dimensionless_temperature": theta,
                    "dimensionless_heat_flux_magnitude": q_star,
                })

                records.append(profile)

            rounded_seen = {
                round(value, 10)
                for value in temperature_differences_seen
            }
            rounded_expected = {
                round(value, 10)
                for value in TEMPERATURE_DIFFERENCES
            }

            if rounded_seen != rounded_expected:
                raise ValueError(
                    f"Expected temperature differences "
                    f"{TEMPERATURE_DIFFERENCES} under {extended_dir}, "
                    f"found {sorted(temperature_differences_seen)}."
                )

    data = pd.concat(records, ignore_index=True)

    expected_profiles = (
        len(MODELS)
        * len(ARRANGEMENTS)
        * len(TEMPERATURE_DIFFERENCES)
    )

    actual_profiles = (
        data[
            [
                "model",
                "arrangement",
                "temperature_difference",
            ]
        ]
        .drop_duplicates()
        .shape[0]
    )

    if actual_profiles != expected_profiles:
        raise ValueError(
            f"Expected {expected_profiles} model/arrangement/temperature "
            f"difference profiles, found {actual_profiles}."
        )

    return data


def padded_limits(values, padding_fraction=0.06, lower_floor=None):
    values = pd.Series(values).dropna().astype(float)

    ymin = float(values.min())
    ymax = float(values.max())
    span = ymax - ymin

    if span == 0.0:
        span = max(abs(ymax), 1.0) * 0.10

    lower = ymin - padding_fraction * span
    upper = ymax + padding_fraction * span

    if lower_floor is not None:
        lower = max(lower, lower_floor)

    return lower, upper


def parameter_style_map():
    default_colours = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    return {
        delta_t: {
            "colour": default_colours[index % len(default_colours)],
            "marker": PARAMETER_MARKERS[index % len(PARAMETER_MARKERS)],
        }
        for index, delta_t in enumerate(TEMPERATURE_DIFFERENCES)
    }


def add_legends(fig, styles):
    temperature_handles = [
        Line2D(
            [0],
            [0],
            color=styles[delta_t]["colour"],
            marker=styles[delta_t]["marker"],
            linestyle="-",
            linewidth=1.8,
            markersize=6,
            label=rf"$\Delta T={delta_t:g}$ K",
        )
        for delta_t in TEMPERATURE_DIFFERENCES
    ]

    model_handles = [
        Line2D(
            [0],
            [0],
            color="black",
            linestyle=MODEL_LINESTYLES[model],
            linewidth=2.0,
            label=model,
        )
        for model in MODELS
    ]

    legend1 = fig.legend(
        handles=temperature_handles,
        title=r"Tube temperature difference",
        loc="upper left",
        bbox_to_anchor=(0.805, 0.88),
        frameon=False,
    )

    fig.add_artist(legend1)

    fig.legend(
        handles=model_handles,
        title="Radiation model",
        loc="upper left",
        bbox_to_anchor=(0.805, 0.35),
        frameon=False,
    )


def save_figure(fig, output_root: Path, filename: str):
    fig.savefig(
        output_root / f"{filename}.pdf",
        bbox_inches="tight",
    )
    fig.savefig(
        output_root / f"{filename}.png",
        dpi=600,
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_profile(
    data: pd.DataFrame,
    arrangement: str,
    y_column: str,
    ylabel: str,
    title: str,
    output_root: Path,
    filename: str,
    lower_floor=None,
):
    styles = parameter_style_map()

    arrangement_data = data[
        data["arrangement"] == arrangement
    ].copy()

    if arrangement_data.empty:
        raise ValueError(f"No data found for {arrangement} arrangement.")

    fig, ax = plt.subplots(
        figsize=(11.8, 6.4),
    )

    y_limits = padded_limits(
        arrangement_data[y_column],
        lower_floor=lower_floor,
    )

    for delta_t in TEMPERATURE_DIFFERENCES:
        style = styles[delta_t]

        for model in MODELS:
            subset = arrangement_data[
                (arrangement_data["model"] == model)
                & (
                    arrangement_data["temperature_difference"].sub(
                        delta_t
                    ).abs()
                    < 1.0e-10
                )
            ].sort_values("x_over_L")

            if subset.empty:
                raise ValueError(
                    f"Missing profile for {model}, {arrangement}, "
                    f"Delta T={delta_t} K."
                )

            ax.plot(
                subset["x_over_L"],
                subset[y_column],
                linestyle=MODEL_LINESTYLES[model],
                color=style["colour"],
                linewidth=1.8,
                marker=style["marker"],
                markevery=55,
                markersize=4.5,
                markerfacecolor="white",
                markeredgewidth=0.8,
                alpha=0.94,
            )

    ax.set_title(title)
    ax.set_xlabel(r"$x/L$")
    ax.set_ylabel(ylabel)

    ax.set_xlim(0.0, 1.0)
    ax.set_xticks([i / 10 for i in range(11)])
    ax.set_xticks([i / 20 for i in range(21)], minor=True)
    ax.set_ylim(*y_limits)

    ax.grid(
        True,
        which="major",
        alpha=0.24,
        linewidth=0.8,
    )
    ax.grid(
        True,
        which="minor",
        axis="x",
        alpha=0.10,
        linewidth=0.6,
    )
    ax.set_axisbelow(True)

    add_legends(fig, styles)

    fig.subplots_adjust(
        left=0.10,
        right=0.78,
        bottom=0.14,
        top=0.90,
    )

    save_figure(fig, output_root, filename)


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python "
            "plot_DOMP1HeatExchangerTemperatureDifferenceTest.py "
            "<project_root>\n"
            "The project root should contain ValidationTests and Output.\n"
            "Example:\n"
            "  python3 "
            "ValidationTests/DOMP1HeatExchangerTemperatureDifferenceTest/"
            "plot_DOMP1HeatExchangerTemperatureDifferenceTest.py ."
        )
        sys.exit(1)

    test_root, output_root = resolve_paths(Path(sys.argv[1]))

    data = read_profile_data(test_root)

    plot_profile(
        data,
        "Alternating",
        "dimensionless_temperature",
        r"$\Theta=(T-T_c)/(T_h-T_c)$",
        "Central inter-row dimensionless temperature -- Alternating arrangement",
        output_root,
        "01_alternating_dimensionless_central_inter_row_temperature_vs_temperature_difference",
        lower_floor=0.0,
    )

    plot_profile(
        data,
        "Surrounded",
        "dimensionless_temperature",
        r"$\Theta=(T-T_c)/(T_h-T_c)$",
        "Central inter-row dimensionless temperature -- Surrounded arrangement",
        output_root,
        "02_surrounded_dimensionless_central_inter_row_temperature_vs_temperature_difference",
        lower_floor=0.0,
    )

    plot_profile(
        data,
        "Alternating",
        "dimensionless_heat_flux_magnitude",
        r"$q_r^*=|\mathbf{q}_r|/(\sigma T_h^4)$",
        "Central inter-row dimensionless radiative heat-flux magnitude -- Alternating arrangement",
        output_root,
        "03_alternating_dimensionless_central_inter_row_heat_flux_magnitude_vs_temperature_difference",
        lower_floor=0.0,
    )

    plot_profile(
        data,
        "Surrounded",
        "dimensionless_heat_flux_magnitude",
        r"$q_r^*=|\mathbf{q}_r|/(\sigma T_h^4)$",
        "Central inter-row dimensionless radiative heat-flux magnitude -- Surrounded arrangement",
        output_root,
        "04_surrounded_dimensionless_central_inter_row_heat_flux_magnitude_vs_temperature_difference",
        lower_floor=0.0,
    )

    print(f"Input directory : {test_root}")
    print(f"Output directory: {output_root}")
    print("Created 4 figures, each saved as PDF and PNG.")


if __name__ == "__main__":
    main()
