import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from scipy.stats import norm

from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def _generate_x_axis(portfolio_percentage_changes: pd.Series) -> NDArray:
    """Generates values for the X-axis.

    Generates an array of evenly spaced values between the minimum and maximum portfolio percentage changes.

    Args:
        portfolio_percentage_changes (pd.Series): Daily portfolio percentage changes.

    Returns:
        NDArray: Array of evenly spaced percentage change values.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _generate_x_axis(portfolio_percentage_changes)
        [-1.26243136e-01 -1.26006073e-01 -1.25769011e-01 -1.25531948e-01
        ...
        1.09871128e-01  1.10108190e-01  1.10345253e-01  1.10582315e-01]

    """
    min_percentage = portfolio_percentage_changes.min()
    max_percentage = portfolio_percentage_changes.max()
    return np.linspace(min_percentage, max_percentage, num=1000)


def _generate_y_axis(x_axis: NDArray, portfolio_mean: float, portfolio_vol: float) -> NDArray:
    r"""Calculates the Probability Density for Each X-axis Value.

    Applies the univariate normal probability density function (PDF) using the formula:
    $f(x) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left(-\frac{1}{2}\left(\frac{x - \mu}{\sigma}\right)^2\right)$
    to each value of the X-axis to compute a density array.

    Args:
        x_axis (NDArray): Array of evenly spaced percentage change values.
        portfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.

    Returns:
        NDArray: Array of probability density values.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _generate_y_axis(x_axis_array, portfolio_mean, portfolio_vol)
        [18.58194447 15.19095559 20.01126733 ... 20.00501504 20.76917395
        20.28235856]

    """
    return norm.pdf(x_axis, portfolio_mean, portfolio_vol)


def plot_return_density_with_var(portfolio_percentage_changes: pd.Series, portfolio_mean: float, portfolio_vol: float, var_value: float, confidence_level: int | float) -> plt.Figure:
    """Plots the Empirical Density of Portfolio Returns with a Normal Distribution and VaR overlay.

    Plots a normalized percentage changes histogram (empirical density). It overlays an adjusted 
    normal distribution curve (Gauss Bell) and marks the VaR value with a line.

    Args:
        portfolio_percentage_changes (pd.Series): Daily portfolio percentage changes.
        portfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.
        var_value (float): Percentage VaR value.
        confidence_level (int | float): Confidence level value.

    Returns:
        plt.Figure: Figure object.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> plot_return_density_with_var(portfolio_percentage_changes, portfolio_mean, portfolio_vol, var_value, confidence_level)
        # Returns a Figure object.

    """
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor("#161B22")
    ax.set_facecolor("#161B22")

    # Empirical Histogram Plot.
    ax.hist(
        portfolio_percentage_changes, 
        bins=70,
        density=True,
        color="#00E1FF",
        edgecolor='black',
        linewidth=0.5,
        alpha=0.7
    )
    ax.set_title("Portfolio Percentage Changes", fontsize=24, fontweight='bold', pad=20, color="#F0F6FC")
    ax.set_xlabel("Daily Returns (%)", fontsize=16, color="#FFFFFF")
    ax.set_ylabel("Empirical Density", fontsize=16, color="#FFFFFF")
    ax.tick_params(colors="#FFFFFF")
    ax.grid(
        axis='y',
        linestyle='dashed',
        alpha=0.3,
        color="#30363D"
    )
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1.0))

    # Normal Distribution (Gauss Bell) Plot.
    x_axis = _generate_x_axis(portfolio_percentage_changes)
    y_axis = _generate_y_axis(x_axis, portfolio_mean, portfolio_vol)
    ax.plot(
        x_axis,
        y_axis,
        color="#FF2600",
        linewidth=2,
        label='Normal Distribution'
    )

    # VaR Value Line.
    ax.axvline(
        var_value,
        color="#FF7300",
        linestyle='dashed',
        linewidth=1.8,
        label=f'VaR {confidence_level:.0%}'
    )

    ax.fill_betweenx(
        [0, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 60],
        portfolio_percentage_changes.min(),
        var_value,
        alpha=0.08,
        color="#FFE600",
    )

    ax.legend(facecolor="#161B22", edgecolor="#30363D", labelcolor="#F0F6FC", fontsize=12)
    
    logger.info("Successfully rendered portfolio returns density plot with VaR overlay.")

    return fig