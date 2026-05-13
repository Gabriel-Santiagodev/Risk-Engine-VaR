from config.js_config import get_js_config
from database.db_config import get_db_engine
from src.core.extractor import run_etl_pipeline
from src.core.quant_engine import run_quant_engine
from src.core.visualizer import plot_return_density_with_var
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


def execute_dashboard() -> None:
    """Executes the dashboard visualization.

    Orchestrates the quantitative analysis process. It calls the quant
    engine to retrieve the values from its dictionary and passes them to the visualizer 
    to render the histogram.

    Args:
        None: This function does not have arguments.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    data = get_js_config()
    engine = get_db_engine()

    run_etl_pipeline(data, engine)
    quant_engine_dictionary = run_quant_engine(data, engine)

    portfolio_percentage_changes = quant_engine_dictionary["portfolio_percentage_changes"]
    portfolio_mean = quant_engine_dictionary["portfolio_mean"]
    portfolio_vol = quant_engine_dictionary["portfolio_vol"]
    var_value = quant_engine_dictionary["var_value"]
    confidence_level = quant_engine_dictionary["confidence_level"]

    plot_return_density_with_var(
        portfolio_percentage_changes, 
        portfolio_mean, portfolio_vol, 
        var_value, confidence_level
    )


def main() -> None:
    """Entry point for the dashboard application.

    Triggers the execution of the main dashboard logic.

    Args:
        None: This function does not have arguments.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    logger.info("Initializing Value at Risk dashboard application...")
    execute_dashboard()
    logger.info("Value at Risk dashboard executed successfully.")

if __name__ == "__main__":
    main()