from visualizer import plot_histogram
from quant_engine import run_engine
    
def execute_dashboard():
    quant_engine_dictionary = run_engine()
    portfolio_percentages_changes = quant_engine_dictionary["portfolio_percentages_changes"]
    plot_histogram(portfolio_percentages_changes)

def main():
    execute_dashboard()

if __name__ == "__main__":
    main()