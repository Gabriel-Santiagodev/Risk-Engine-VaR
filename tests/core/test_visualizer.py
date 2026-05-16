import matplotlib.pyplot as plt
import numpy as np
from numpy.testing import assert_array_almost_equal
import pandas as pd

from src.core.visualizer import (
    _generate_x_axis,
    _generate_y_axis,
    plot_return_density_with_var
)


def test_generate_x_axis_success_with_valid_array_generation():
    """Tests that no exception is raised when the x-axis array values are generated."""
    fake_series = pd.Series([-0.5, 0.0, 0.5])

    valid_array = _generate_x_axis(fake_series)

    assert len(valid_array) == 1000
    assert valid_array[0] == -0.5
    assert valid_array[-1] == 0.5


def test_generate_y_axis_success_with_valid_densities_array_generation():
    """Tests that no exception is raised when the densities array are generated."""
    fake_x_axis = np.array([0.0])
    fake_portfolio_mean = 0.0
    fake_portfolio_vol = 1.0
    expected_density_value = np.array([0.398942])

    expected_densities_array = _generate_y_axis(fake_x_axis, fake_portfolio_mean, fake_portfolio_vol)
    
    assert_array_almost_equal(expected_densities_array, expected_density_value, decimal=6)


def test_return_density_with_var_with_successful_plot_render():
    """Tests that no exception is raised when the plot is rendered."""
    fake_series = pd.Series([-0.5, 0.0, 0.5])
    fake_portfolio_mean = 0.0
    fake_portfolio_vol = 1.0
    var_value = 0.04364060637425606
    confidence_level = 0.99

    result = plot_return_density_with_var(fake_series, fake_portfolio_mean, fake_portfolio_vol, var_value, confidence_level)

    assert isinstance(result, plt.Figure)
    plt.close('all')