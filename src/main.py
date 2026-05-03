from visualizer import plot_histogram
from quant_engine import run_quant_engine
from extractor import run_etl_pipeline
from db_config import get_db_engine
from js_config import get_js_config
    
def execute_dashboard() -> None:
    """Execute the visualization dashboard.

    This function orchestrates the quantitative analysis process. It calls the quant
    engine to retrieve the portfolio's percentage changes and passes them to the
    visualizer to render the histogram.

    Args:
        None: This function does not have arguments.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    data = get_js_config()
    engine = get_db_engine()
    run_etl_pipeline(data,engine)
    quant_engine_dictionary = run_quant_engine(data,engine)
    portfolio_percentages_changes = quant_engine_dictionary["portfolio_percentages_changes"]
    plot_histogram(portfolio_percentages_changes)

def main() -> None:
    """Entry point for the dashboard application.

    This function triggers the execution of the main dashboard logic.

    Args:
        None: This function does not have arguments.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    execute_dashboard()
    print("Dashboard has been executed successfully.")

if __name__ == "__main__":
    main()