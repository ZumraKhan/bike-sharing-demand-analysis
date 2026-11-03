"""
Shared visual style for the Bike Sharing Demand analysis.

Implements a single, validated design system so every figure in the notebook,
the PDF report and the slide deck reads as one piece of work:

  * Categorical palette (slots 1-3) validated for colour-vision deficiency
    separation, lightness band, chroma floor and contrast.
  * Sequential single-hue blue ramp for magnitude (heatmaps).
  * Diverging blue<->red ramp with a NEUTRAL GREY midpoint for correlations.
  * Thin marks, rounded data-ends, hairline recessive grid, no chart junk.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
SURFACE      = "#fcfcfb"   # chart surface
INK          = "#0b0b0b"   # primary text
INK_SECOND   = "#52514e"   # secondary text
INK_MUTED    = "#898781"   # axis / tick labels
GRID         = "#e1e0d9"   # hairline gridline
AXIS         = "#c3c2b7"   # baseline / axis rule

# Categorical slots, assigned in FIXED order (never cycled).
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
BLUE, ORANGE, AQUA = SERIES

DE_EMPHASIS = "#c3c2b7"    # the "grey the rest" colour for emphasis charts

# Single-hue sequential ramp (light -> dark), for continuous magnitude.
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf",
            "#184f95", "#0d366b"]

# Ordinal ramp (discrete ordered categories): light end clears the surface.
ORDINAL_BLUE = ["#86b6ef", "#3987e5", "#256abf", "#0d366b"]

CMAP_SEQ = LinearSegmentedColormap.from_list("seq_blue", SEQ_BLUE)
# Diverging: two opposite-temperature poles + neutral grey midpoint.
CMAP_DIV = LinearSegmentedColormap.from_list(
    "div_blue_red", ["#0d366b", "#3987e5", "#9ec5f4", "#f0efec",
                     "#f0a0a0", "#e34948", "#a01f1f"])

# Text colour to use INSIDE a coloured fill, keyed by fill luminance.
def label_on(fill: str) -> str:
    return "#0b0b0b" if fill.lower() in ("#eda100", "#fab219", "#86b6ef",
                                         "#cde2fb", "#9ec5f4") else "#ffffff"


def apply_style(dpi: int = 150) -> None:
    """Install the house style as matplotlib defaults."""
    mpl.rcParams.update({
        "figure.dpi":            dpi,
        "savefig.dpi":           dpi,
        "figure.facecolor":      SURFACE,
        "savefig.facecolor":     SURFACE,
        "axes.facecolor":        SURFACE,
        "font.family":           "sans-serif",
        "font.sans-serif":       ["Segoe UI", "DejaVu Sans", "Arial"],
        "font.size":             10,
        "axes.titlesize":        13,
        "axes.titleweight":      "semibold",
        "axes.titlecolor":       INK,
        "axes.titlelocation":    "left",
        "axes.titlepad":         14,
        "axes.labelsize":        10,
        "axes.labelcolor":       INK_SECOND,
        "axes.edgecolor":        AXIS,
        "axes.linewidth":        0.8,            # hairline
        "axes.spines.top":       False,
        "axes.spines.right":     False,
        "axes.grid":             True,
        "axes.axisbelow":        True,
        "grid.color":            GRID,
        "grid.linewidth":        0.8,
        "grid.linestyle":        "-",            # SOLID, never dashed
        "xtick.color":           INK_MUTED,
        "ytick.color":           INK_MUTED,
        "xtick.labelcolor":      INK_MUTED,
        "ytick.labelcolor":      INK_MUTED,
        "xtick.direction":       "out",
        "ytick.direction":       "out",
        "xtick.major.size":      0,
        "ytick.major.size":      0,
        "legend.frameon":        False,
        "legend.fontsize":       9.5,
        "legend.labelcolor":     INK_SECOND,
        "lines.linewidth":       2.0,            # 2px lines
        "lines.solid_capstyle":  "round",
        "lines.markersize":      5,              # >= 8px diameter
        "figure.constrained_layout.use": True,
    })


def titled(ax, title: str, subtitle: str | None = None) -> None:
    """Left-aligned title with an optional quieter subtitle beneath it."""
    if subtitle:
        ax.set_title(f"{title}\n", loc="left")
        ax.text(0, 1.045, subtitle, transform=ax.transAxes, ha="left",
                va="bottom", fontsize=9.5, color=INK_MUTED)
    else:
        ax.set_title(title, loc="left")


def bars(ax, positions, values, color=BLUE, width_pt=11.0, horizontal=False,
         zorder=3, label=None):
    """
    Draw bars as thick round-capped lines: this yields a rounded data-end
    while the baseline end is clipped square by the axis limit -- the house
    mark spec, without drawing a border around any mark.
    """
    for i, (p, v) in enumerate(zip(positions, values)):
        xs, ys = ((0, v), (p, p)) if horizontal else ((p, p), (0, v))
        ax.add_line(Line2D(xs, ys, linewidth=width_pt, color=color,
                           solid_capstyle="round", zorder=zorder,
                           label=label if i == 0 else None))
    return ax


def value_labels(ax, positions, values, fmt="{:,.0f}", horizontal=False,
                 width_pt=11.0, color=INK_SECOND, only=None, fontsize=9):
    """
    Direct-label marks SELECTIVELY (pass `only` = list of indices).

    The offset is expressed in POINTS, not data units, so the label always
    clears the bar's round cap (which overshoots the data value by half the
    mark's thickness) instead of being clipped by it.
    """
    clear = width_pt / 2 + 5
    for i, (p, v) in enumerate(zip(positions, values)):
        if only is not None and i not in only:
            continue
        xy = (v, p) if horizontal else (p, v)
        offset = (clear, 0) if horizontal else (0, clear)
        ax.annotate(fmt.format(v), xy=xy, xytext=offset,
                    textcoords="offset points", fontsize=fontsize, color=color,
                    ha="left" if horizontal else "center",
                    va="center" if horizontal else "bottom")


def ring_marker(ax, x, y, color=BLUE, size=7, zorder=6):
    """End-dot carrying a 2px surface ring so it stays legible on crossings."""
    ax.plot(x, y, "o", markersize=size, color=color,
            markeredgecolor=SURFACE, markeredgewidth=2, zorder=zorder)


def save(fig, path):
    """Save at a fixed size (no bbox re-crop, so pixel specs hold)."""
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path
