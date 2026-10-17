#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from functools import lru_cache
from pathlib import Path
from typing import Final

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
import numpy as np
import pandas as pd


CASE_DIRECTORY: Final[str] = "DOMP1HeatExchangerArrangementTest"
DEFAULT_FIGURE_SUBDIRECTORY: Final[Path] = Path("Figures") / "ArrangementProfiles"

ARRANGEMENTS: Final[dict[str, str]] = {
    "Clustered": "ClusteredArrangement",
    "Surrounded": "HotPipesSurroundedByColdPipes",
    "Alternating": "AlternatingArrangement",
}

MODELS: Final[tuple[str, ...]] = ("P1", "DOM")

ARRANGEMENT_COLOURS: Final[dict[str, str]] = {
    "Clustered": "#0072B2",
    "Surrounded": "#D55E00",
    "Alternating": "#009E73",
}

MODEL_STYLES: Final[dict[str, dict[str, object]]] = {
    "P1": {
        "linestyle": "--",
        "linewidth": 2.0,
        "marker": "o",
        "markersize": 4.2,
        "markerfacecolor": "white",
        "markeredgewidth": 0.9,
    },
    "DOM": {
        "linestyle": "-",
        "linewidth": 2.2,
        "marker": None,
    },
}

FIGURE_SIZE: Final[tuple[float, float]] = (7.8, 5.0)
PNG_DPI: Final[int] = 400
MARKER_COUNT: Final[int] = 11

WALL_COLUMNS: Final[set[str]] = {
    "position_over_L",
    "dimensionless_irradiation",
    "dimensionless_normal_wall_heat_flux",
}

INTER_ROW_COLUMNS: Final[set[str]] = {
    "x_over_L",
    "x",
    "y",
    "dimensionless_temperature",
    "dimensionless_heat_flux_magnitude",
    "dimensionless_irradiation",
}


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.size": 12.5,
            "axes.titlesize": 15,
            "axes.labelsize": 14,
            "xtick.labelsize": 11.5,
            "ytick.labelsize": 11.5,
            "legend.fontsize": 10.5,
            "axes.linewidth": 1.0,
            "lines.solid_capstyle": "round",
            "lines.dash_capstyle": "round",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def is_valid_data_root(path: Path) -> bool:
    return all(
        (path / model / "ExtendedDiagnostics").is_dir()
        for model in MODELS
    )


def candidate_data_roots() -> list[Path]:
    script_dir = Path(__file__).resolve().parent
    cwd = Path.cwd().resolve()

    bases: list[Path] = [cwd, script_dir]
    bases.extend(cwd.parents)
    bases.extend(script_dir.parents)

    candidates: list[Path] = []
    for base in bases:
        candidates.extend(
            [
                base / "Output" / CASE_DIRECTORY,
                base / CASE_DIRECTORY,
            ]
        )

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def resolve_data_root(user_root: str | None) -> Path:
    if user_root:
        supplied = Path(user_root).expanduser().resolve()
        possibilities = [
            supplied,
            supplied / CASE_DIRECTORY,
            supplied / "Output" / CASE_DIRECTORY,
        ]
        for possibility in possibilities:
            if is_valid_data_root(possibility):
                return possibility
        raise FileNotFoundError(
            "The supplied path does not contain the expected P1 and DOM "
            f"ExtendedDiagnostics directories: {supplied}"
        )

    for candidate in candidate_data_roots():
        if is_valid_data_root(candidate):
            return candidate

    searched = "\n  ".join(str(path) for path in candidate_data_roots())
    raise FileNotFoundError(
        "Could not locate the arrangement output automatically. Supply the "
        "path explicitly, for example:\n\n"
        "  python3 plot_heat_exchanger_arrangement_profiles.py "
        "/path/to/Output/DOMP1HeatExchangerArrangementTest\n\n"
        f"Searched:\n  {searched}"
    )


def require_columns(df: pd.DataFrame, required: set[str], csv_path: Path) -> None:
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(
            f"Missing required columns in {csv_path}: {', '.join(missing)}"
        )


@lru_cache(maxsize=None)
def read_profile(
    data_root_text: str,
    model: str,
    arrangement_directory: str,
    filename: str,
) -> pd.DataFrame:
    data_root = Path(data_root_text)
    csv_path = (
        data_root
        / model
        / "ExtendedDiagnostics"
        / arrangement_directory
        / filename
    )
    if not csv_path.is_file():
        raise FileNotFoundError(f"Required profile file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"Profile file is empty: {csv_path}")

    if filename.endswith("wall_profile.csv"):
        require_columns(df, WALL_COLUMNS, csv_path)
    else:
        require_columns(df, INTER_ROW_COLUMNS, csv_path)

    return df


def exact_central_profile(df: pd.DataFrame, csv_description: str) -> pd.DataFrame:

    working = df.sort_values(["x_over_L", "y"]).copy()
    counts = working.groupby("x_over_L", sort=True).size()

    if counts.empty or not (counts == 2).all():
        observed = sorted(counts.unique().tolist())
        raise ValueError(
            f"Central-profile averaging requires exactly two rows at every "
            f"x/L in {csv_description}; observed duplicate counts: {observed}"
        )

    y_values = np.sort(working["y"].unique())
    if len(y_values) != 2:
        raise ValueError(
            f"Expected exactly two adjacent y coordinates in {csv_description}; "
            f"found {len(y_values)}: {y_values.tolist()}"
        )

    numeric_columns = working.select_dtypes(include=[np.number]).columns.tolist()
    columns_to_average = [
        column for column in numeric_columns if column not in {"x_over_L", "x"}
    ]

    averaged = (
        working.groupby(["x_over_L", "x"], as_index=False, sort=True)[
            columns_to_average
        ]
        .mean()
        .sort_values("x_over_L")
        .reset_index(drop=True)
    )

    return averaged


def marker_interval(number_of_points: int) -> int:
    return max(1, number_of_points // MARKER_COUNT)


def add_combined_legend(fig: plt.Figure) -> None:
    arrangement_handles = [
        Line2D(
            [0],
            [0],
            color=ARRANGEMENT_COLOURS[label],
            linewidth=2.4,
            linestyle="-",
            label=label,
        )
        for label in ARRANGEMENTS
    ]

    model_handles = [
        Line2D(
            [0],
            [0],
            color="black",
            linestyle=str(MODEL_STYLES["P1"]["linestyle"]),
            linewidth=float(MODEL_STYLES["P1"]["linewidth"]),
            marker=str(MODEL_STYLES["P1"]["marker"]),
            markersize=float(MODEL_STYLES["P1"]["markersize"]),
            markerfacecolor="white",
            markeredgecolor="black",
            markeredgewidth=float(MODEL_STYLES["P1"]["markeredgewidth"]),
            label="P1",
        ),
        Line2D(
            [0],
            [0],
            color="black",
            linestyle=str(MODEL_STYLES["DOM"]["linestyle"]),
            linewidth=float(MODEL_STYLES["DOM"]["linewidth"]),
            label="DOM",
        ),
    ]

    fig.legend(
        handles=arrangement_handles + model_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=5,
        frameon=False,
        handlelength=2.8,
        columnspacing=1.25,
        handletextpad=0.55,
    )


def prepare_axes(ax: plt.Axes, title: str, x_label: str, y_label: str) -> None:
    ax.set_title(title, pad=11)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_xlim(0.0, 1.0)
    ax.xaxis.set_major_locator(MultipleLocator(0.2))
    ax.xaxis.set_minor_locator(AutoMinorLocator(2))
    ax.yaxis.set_minor_locator(AutoMinorLocator(2))
    ax.grid(True, which="major", linewidth=0.65, alpha=0.24)
    ax.grid(False, which="minor")
    ax.tick_params(which="major", direction="in", top=True, right=True, length=5)
    ax.tick_params(which="minor", direction="in", top=True, right=True, length=2.8)
    ax.margins(y=0.06)


def save_figure(fig: plt.Figure, output_directory: Path, filename_stem: str) -> None:
    output_directory.mkdir(parents=True, exist_ok=True)
    pdf_path = output_directory / f"{filename_stem}.pdf"
    png_path = output_directory / f"{filename_stem}.png"

    fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png_path, dpi=PNG_DPI, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

    print(f"Saved: {pdf_path}")
    print(f"Saved: {png_path}")


def plot_comparison(
    data_root: Path,
    output_directory: Path,
    filename: str,
    x_column: str,
    y_column: str,
    title: str,
    x_label: str,
    y_label: str,
    output_stem: str,
    average_central_rows: bool = False,
) -> None:
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    for arrangement_label, arrangement_directory in ARRANGEMENTS.items():
        colour = ARRANGEMENT_COLOURS[arrangement_label]

        for model in MODELS:
            df = read_profile(
                str(data_root), model, arrangement_directory, filename
            ).copy()

            if average_central_rows:
                description = (
                    f"{model}/{arrangement_directory}/{filename}"
                )
                df = exact_central_profile(df, description)
            else:
                df = df.sort_values(x_column).reset_index(drop=True)

            x = pd.to_numeric(df[x_column], errors="raise").to_numpy()
            y = pd.to_numeric(df[y_column], errors="raise").to_numpy()

            if not (np.isfinite(x).all() and np.isfinite(y).all()):
                raise ValueError(
                    f"Non-finite plotting data found in "
                    f"{model}/{arrangement_directory}/{filename}"
                )

            style = dict(MODEL_STYLES[model])
            if model == "P1":
                style["markevery"] = marker_interval(len(x))
                style["markeredgecolor"] = colour

            ax.plot(x, y, color=colour, **style)

    prepare_axes(ax, title, x_label, y_label)
    add_combined_legend(fig)
    fig.subplots_adjust(left=0.15, right=0.975, bottom=0.15, top=0.79)
    save_figure(fig, output_directory, output_stem)


def build_all_figures(data_root: Path, output_directory: Path) -> None:
    wall_irradiation_label = r"$H^{*}=H/(\sigma T_{h}^{4})$"
    wall_flux_label = r"$q_{r,n}^{*}=q_{r,n}/(\sigma T_{h}^{4})$"
    temperature_label = r"$\Theta=(T-T_{c})/(T_{h}-T_{c})$"
    heat_flux_magnitude_label = (
        r"$|\mathbf{q}_{r}|^{*}=|\mathbf{q}_{r}|/(\sigma T_{h}^{4})$"
    )
    internal_irradiation_label = r"$G^{*}=G/(4\sigma T_{h}^{4})$"

    wall_specs = [
        ("north", r"$x/L$"),
        ("south", r"$x/L$"),
        ("east", r"$y/L$"),
        ("west", r"$y/L$"),
    ]

    for index, (wall, coordinate_label) in enumerate(wall_specs, start=1):
        plot_comparison(
            data_root=data_root,
            output_directory=output_directory,
            filename=f"{wall}_wall_profile.csv",
            x_column="position_over_L",
            y_column="dimensionless_irradiation",
            title=f"{wall.capitalize()}-wall irradiation",
            x_label=coordinate_label,
            y_label=wall_irradiation_label,
            output_stem=(
                f"{index:02d}_{wall}_wall_dimensionless_irradiation"
            ),
        )

    for index, (wall, coordinate_label) in enumerate(wall_specs, start=5):
        plot_comparison(
            data_root=data_root,
            output_directory=output_directory,
            filename=f"{wall}_wall_profile.csv",
            x_column="position_over_L",
            y_column="dimensionless_normal_wall_heat_flux",
            title=f"{wall.capitalize()}-wall normal radiative heat flux",
            x_label=coordinate_label,
            y_label=wall_flux_label,
            output_stem=(
                f"{index:02d}_{wall}_wall_dimensionless_normal_heat_flux"
            ),
        )

    inter_row_regions = [
        ("central", "central_inter_row_profile.csv", True),
        ("lower", "lower_inter_row_profile.csv", False),
        ("upper", "upper_inter_row_profile.csv", False),
    ]

    for index, (region, filename, average_central) in enumerate(
        inter_row_regions, start=9
    ):
        plot_comparison(
            data_root=data_root,
            output_directory=output_directory,
            filename=filename,
            x_column="x_over_L",
            y_column="dimensionless_temperature",
            title=f"{region.capitalize()} inter-row temperature",
            x_label=r"$x/L$",
            y_label=temperature_label,
            output_stem=(
                f"{index:02d}_{region}_inter_row_dimensionless_temperature"
            ),
            average_central_rows=average_central,
        )

    for index, (region, filename, average_central) in enumerate(
        inter_row_regions, start=12
    ):
        plot_comparison(
            data_root=data_root,
            output_directory=output_directory,
            filename=filename,
            x_column="x_over_L",
            y_column="dimensionless_heat_flux_magnitude",
            title=f"{region.capitalize()} inter-row heat-flux magnitude",
            x_label=r"$x/L$",
            y_label=heat_flux_magnitude_label,
            output_stem=(
                f"{index:02d}_{region}_inter_row_dimensionless_heat_flux_magnitude"
            ),
            average_central_rows=average_central,
        )

    for index, (region, filename, average_central) in enumerate(
        inter_row_regions, start=15
    ):
        plot_comparison(
            data_root=data_root,
            output_directory=output_directory,
            filename=filename,
            x_column="x_over_L",
            y_column="dimensionless_irradiation",
            title=f"{region.capitalize()} inter-row irradiation",
            x_label=r"$x/L$",
            y_label=internal_irradiation_label,
            output_stem=(
                f"{index:02d}_{region}_inter_row_dimensionless_irradiation"
            ),
            average_central_rows=average_central,
        )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the 17 thesis-quality P1--DOM arrangement-profile plots."
        )
    )
    parser.add_argument(
        "data_root",
        nargs="?",
        help=(
            "Path to Output/DOMP1HeatExchangerArrangementTest, to Output, "
            "or to a directory containing that case folder."
        ),
    )
    parser.add_argument(
        "--fig-dir",
        help=(
            "Optional output directory for figures. The default is "
            "<data-root>/Figures/ArrangementProfiles."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    configure_matplotlib()

    try:
        data_root = resolve_data_root(args.data_root)
        output_directory = (
            Path(args.fig_dir).expanduser().resolve()
            if args.fig_dir
            else data_root / DEFAULT_FIGURE_SUBDIRECTORY
        )

        print(f"Using arrangement data root: {data_root}")
        print(f"Writing figures to: {output_directory}")
        print(
            "Central inter-row profiles will be formed by averaging the two "
            "adjacent cell-centre rows at every x/L."
        )

        build_all_figures(data_root, output_directory)

    except (FileNotFoundError, ValueError, KeyError, pd.errors.ParserError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Completed 17 figures in both PDF and PNG formats.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
