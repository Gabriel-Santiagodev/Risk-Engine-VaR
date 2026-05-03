import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from numpy.typing import NDArray
from matplotlib.ticker import PercentFormatter
from scipy.stats import norm

def _generate_x_axis(portfolio_percentages_changes: pd.Series) -> NDArray:
    """Generate Values in the X-axis.

    This function is in charge to pick the minimum percentage change value of the 
    portfolio's percentages changes and the maximum percentage change value in order to
    return a percentage changes values array from the minimum to the maximum with the same
    numerical space between them.

    Args:
        portfolio_percentages_changes (pd.Series): Daily portfolio percentage changes.

    Returns:
        NDArray: Percentage changes values array with the same numerical space between them.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _generate_x_axis(portfolio_percentages_changes:pd.Series)
        [-1.26243136e-01 -1.26006073e-01 -1.25769011e-01 -1.25531948e-01
        ...
        1.09871128e-01  1.10108190e-01  1.10345253e-01  1.10582315e-01]

    """
    min_percentage = portfolio_percentages_changes.min()
    max_percentage = portfolio_percentages_changes.max()
    return np.linspace(min_percentage, max_percentage, num=1000)

def _generate_y_axis(x_axis: NDArray, portfolio_mean: float, portfolio_vol: float) -> NDArray:
    r"""Calculate Empirical Density of each X-axis value.

    This function is in charge to apply probability density function formula (PDF)
    f(w) = 1 / ((2\pi)^{d/2} \cdot |\Sigma|^{1/2}) \cdot exp(-1/2 \cdot (w - \mu)^T \cdot \Sigma^{-1} \cdot (w - \mu))
    to each value of the X-axis in order to calculate their density in the Y-axis and return a densities array.

    Args:
        x_axis (NDArray): Percentage changes values array with the same numerical space between them.
        portfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.

    Returns:
        NDArray: Densities Array.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> _generate_y_axis(x_axis_array, portfolio_mean, portfolio_vol)
        [18.58194447 15.19095559 20.01126733 ... 20.00501504 20.76917395
        20.28235856]

    """
    return norm.pdf(x_axis, portfolio_mean, portfolio_vol)

def plot_return_density_with_var(portfolio_percentages_changes: pd.Series, portfolio_mean: float, portfolio_vol: float, var_value: float, confidence_level: int | float) -> None:
    """Plots the Empirical Density Portfolio Returns with a Normal Distribution and a Parametric VaR Line.

    This function is in charge to plot a normalized percentages changes histogram (empirical density).
    It overlays an adjusted normal distribution curve (Gauss Bell) and marks the VaR value
    with a line.

    Args:
        portfolio_percentages_changes (pd.Series): Daily portfolio percentage changes.
        portfolio_mean (float): Portfolio mean value.
        portfolio_vol (float): Portfolio volatility value.
        var_value (float): Percentage VaR value.
        confidence_level (int | float): Confidence level value.

    Returns:
        None: Renders the plot directly to the graphical output.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> plot_return_density_with_var(portfolio_percentages_changes, portfolio_mean, portfolio_vol, var_value, confidence_level)
        # Opens a matplotlib window displaying the empirical density histogram.

    """
    fig, ax = plt.subplots(figsize=(12,6))

    # Empirical Histogram Plot.
    ax.hist(
        portfolio_percentages_changes, 
        bins=70,
        density=True,
        color='steelblue',
        edgecolor='black',
        linewidth=0.5,
        alpha=0.7
    )
    ax.set_title("Portfolio Percentage Changes", fontsize=24, fontweight='bold', pad=20)
    ax.set_xlabel("Daily Returns (%)", fontsize=16)
    ax.set_ylabel("Empirical Density", fontsize=16)
    ax.grid(
        axis='y',
        linestyle='dashed',
        alpha=0.3
    )
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1.0))

    # Normal Distribution (Gauss Bell) Plot.
    
    x_axis = _generate_x_axis(portfolio_percentages_changes)
    y_axis = _generate_y_axis(x_axis, portfolio_mean, portfolio_vol)
    ax.plot(
        x_axis,
        y_axis,
        color='red',
        linewidth=2,
        label='Normal Distribution'
    )

    # VaR Value Line.

    ax.axvline(
        var_value,
        color='darkorange',
        linestyle='dashed',
        label=f'VaR {confidence_level*100}%'
    )

    ax.legend()

    plt.show()

