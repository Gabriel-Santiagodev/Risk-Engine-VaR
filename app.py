from datetime import datetime, timedelta, date
import pandas as pd
import streamlit as st

from src.core.extractor import _data_extractor, _transform_data
from src.core.quant_engine import run_quant_engine
from src.core.visualizer import plot_return_density_with_var
from src.utils.logger import setup_logging

logger = setup_logging(__name__)


@st.cache_data(show_spinner=False)
def fetch_market_data(tickers: list[str], start_date: str, end_date: str) -> pd.DataFrame:
    """Extracts raw market data from Yahoo Finance to storage it into the cache memory.

    Extracts, transforms, and caches historical market data for the specified tickers and dates.

    Args:
        tickers (list[str]): List of company tickers. (e.g., ['AAPL', 'MSFT']).
        start_date (str): Start date of the historical market. Must be in the following format: "YYYY-MM-DD".
        end_date (str): End date of the historical market. Must be in the following format: "YYYY-MM-DD".

    Returns:
        pd.DataFrame: Transformed historical market dataframe.

    Raises:
        ValueError: If the ticker format or date format is incorrect.
        requests.exceptions.ConnectionError: If there is no internet connection or the server does not respond.
        requests.exceptions.Timeout: If Yahoo Finance request exceeded waiting time.
        requests.exceptions.HTTPError: If there is a HTTP error.

    Examples:
        >>> df = fetch_market_data(["AAPL", "GOOGL"], "2020-01-01", "2020-01-05")
        >>> list(df.columns)
        ['market_date', 'ticker', 'adj_close', 'close_price', 'high_price', 'low_price', 'open_price', 'volume']

    """
    raw_df = _data_extractor(tickers, start_date, end_date)
    df = _transform_data(raw_df)

    return df


def main() -> None:
    """Entry point for the VaR dashboard web application.

    Triggers the execution of the VaR dashboard web application rendering.

    Args:
        None: This function does not have arguments.

    Returns:
        None: This function does not have returns.

    Raises:
        None: This function does not have raises.

    """
    st.set_page_config(
        page_title="VaR dashboard", 
        page_icon="💸",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    st.title("Value at Risk Dashboard")
    with st.sidebar:
        st.header("Configuration")
        today = datetime.now()
        one_year_ago = today - timedelta(days=365)
        today = today.date()
        one_year_ago = one_year_ago.date()

        st.subheader("1. Time Horizon")
        start_date = st.date_input(
            "Start Date",
            value=one_year_ago,
            min_value=date(2000, 1, 1),
            max_value=one_year_ago
        )
        end_date = st.date_input(
            "End Date",
            value=today,
            min_value=date(2000, 1, 2),
            max_value=today
        )
        
        if (end_date - start_date).days < 365:
            st.error("Financial models require at least 1 year (365 days) of historical data to be statistically valid.")
            st.stop()
        
        st.subheader("2. Portfolio Parameters")
        portfolio_value = st.number_input(
            "Total Capital ($)", 
            value=100, 
            min_value=1,
            step=1,
        )
        confidence_level = st.selectbox("Confidence Level", options=[0.95, 0.99])

        st.subheader("3. Tickers & Weights")
        popular_tickers =[
            "AAPL",   
            "MSFT",  
            "GOOGL",  
            "AMZN",   
            "TSLA",   
            "NVDA",   
            "META",   
            "NFLX",   
            "JPM",   
            "BAC",    
            "XOM",   
            "CVX",   
            "V",      
            "MA",     
            "BRK-B",  
            "SPY",    
            "QQQ",    
            "DIA",    
            "IWM",    
            "VTI"     
        ]

        tickers_list = st.multiselect(
            "Select Tickers",
            options=popular_tickers,
            default=["GOOGL", "AAPL"],
            max_selections=5,
        )
        if len(tickers_list) < 2:
            st.error("Please select at least 2 tickers for a diversified portfolio.")
            st.stop()
        
        weights_list = []
        col1, col2 = st.columns(2)
        col1.text("Select Weights %")
        for ticker in tickers_list:
            col1, col2 = st.columns(2)
            col1.markdown(f"{ticker}")
            weight = col2.number_input(
                "Weight %",
                value=100 // len(tickers_list),
                min_value=1,
                max_value=99,
                step=1,
                key=f"weight_{ticker}",
                label_visibility="collapsed"
            )
            weights_list.append(weight)
        if sum(weights_list) != 100:
            st.error("The sum of weights must be exactly 100%")
            st.stop()
        pressed_button = st.button(
            "Calculate Value at Risk", 
            type="primary", 
            icon="📊",
            width="stretch"
        )
    
    if pressed_button:
        with st.spinner("Downloading market data and computing risk matrices..."):
            market_data = fetch_market_data(tickers_list, str(start_date), str(end_date))
            weight_tickers_dict = {ticker: weight / 100 for ticker, weight in zip(tickers_list, weights_list)}
            web_config = {
                "weight_tickers": weight_tickers_dict,
                "portfolio_value": portfolio_value,
                "confidence_level": confidence_level
            }
            risk_results = run_quant_engine(web_config, market_data)

        var_money = risk_results["var_money"]
        portfolio_vol = risk_results["portfolio_vol"]
        portfolio_mean = risk_results["portfolio_mean"]
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "**1-Day Value at Risk (VaR)**",
            value=f"${var_money:,.2f}",
            border=True
        )
        col2.metric(
            "**Portfolio Volatility (Daily)**",
            value=f"{portfolio_vol * 100:.2f}%",
            border=True
        )
        col3.metric(
            "**Expected Return (Daily)**",
            value=f"{portfolio_mean * 100:.2f}%",
            border=True
        )
        st.subheader(f"With a confidence level of :blue[{confidence_level}%] and a portfolio's size of :blue[\\${portfolio_value}] you will lose less than or equal than :blue[\\${var_money:,.2f}]")
        st.divider()
        portfolio_percentage_changes = risk_results["portfolio_percentage_changes"]
        var_value = risk_results["var_value"]
        confidence_level = risk_results["confidence_level"]
        fig = plot_return_density_with_var(portfolio_percentage_changes, portfolio_mean, portfolio_vol, var_value, confidence_level)
        st.pyplot(fig)

    else:
        st.info(
            "Configure your portfolio in the sidebar and click **Calculate Value at Risk** to begin.", 
            icon="💼", 
            width=600
        )

if __name__ == "__main__":
    main()