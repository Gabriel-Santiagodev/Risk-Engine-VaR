CREATE TABLE historical_market_data(
    market_date DATE NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    low_price NUMERIC(15,4),
    high_price NUMERIC(15,4),
    close_price NUMERIC(15,4) NOT NULL CHECK (close_price >= 0),
    open_price NUMERIC(15,4),
    volume BIGINT,
    adj_close NUMERIC(15,4) NOT NULL CHECK (adj_close >= 0),
    PRIMARY KEY(ticker, market_date)
);

-- Table comment
COMMENT ON TABLE historical_market_data IS 'Stores daily historical OHLCV data for stock tickers.';

-- Columns comments
COMMENT ON COLUMN historical_market_data.market_date IS 'Trading date (YYYY-MM-DD).';
COMMENT ON COLUMN historical_market_data.ticker IS 'Stock symbol (e.g., AAPL, GOOGL).';
COMMENT ON COLUMN historical_market_data.low_price IS 'Lowest traded price for the trading day.';
COMMENT ON COLUMN historical_market_data.high_price IS 'Highest traded price for the trading day.';
COMMENT ON COLUMN historical_market_data.close_price IS 'Closing price for the trading day; last traded price at market close.';
COMMENT ON COLUMN historical_market_data.open_price IS 'Opening price for the trading day; first traded price at market open.';
COMMENT ON COLUMN historical_market_data.volume IS 'Number of shares/contracts traded during the trading day; integer units.';
COMMENT ON COLUMN historical_market_data.adj_close IS 'Adjusted close price. Accounts for corporate actions like splits and dividends. Primary metric for VaR.';
