import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import pandas as pd

def plot_histogram(portfolio_percentages_changes:pd.Series) -> None:
    """Plots the Empirical Density Histogram of Portfolio Returns

    This function generates a matplotlib histogram showing the distribution
    of daily percentage changes. It normalizes the data to display empirical
    density on the Y-axis and formats the X-axis as percentages.

    Args:
        portfolio_percentages_changes (pd.Series): Daily portfolio percentage changes.

    Returns:
        None: Renders the plot directly to the graphical output.

    Raises:
        None: This function does not have raises.

    Examples:
        >>> plot_histogram(portfolio_percentages_changes)
        # Opens a matplotlib window displaying the empirical density histogram.

    """
    fig, ax = plt.subplots(figsize=(12,6))
    ax.hist(
        portfolio_percentages_changes, 
        bins=70,
        density=True,
        color='steelblue',
        edgecolor='black',
        linewidth=0.5,
        alpha=0.7
    )
    ax.set_title("Portfolio Percentage Changes",fontsize=24,fontweight='bold', pad=20)
    ax.set_xlabel("Daily Returns (%)",fontsize=16)
    ax.set_ylabel("Empirical Density",fontsize=16)
    ax.grid(
        axis='y',
        linestyle='--',
        alpha=0.3
    )
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1.0))
    plt.show()

