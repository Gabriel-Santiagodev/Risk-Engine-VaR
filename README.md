# 💸 Portfolio Value at Risk (VaR) Dashboard

**Try it live!** [Value at Risk Dashboard](https://value-at-risk-dashboard.streamlit.app)

<img width="1897" height="911" alt="var_image_one" src="https://github.com/user-attachments/assets/2e8604ef-de42-4ad4-84fc-3d16a954eac6" />

---

<img width="1891" height="899" alt="var_image_two" src="https://github.com/user-attachments/assets/3db44706-553b-4307-b1fe-8940ca548486" />


A straightforward, interactive web application built with Python and Streamlit to calculate the 1-Day Parametric Value at Risk (VaR) of a custom stock portfolio. 

The project extracts historical market data, computes the portfolio's variance-covariance matrix, and visualizes the risk using a normal distribution curve. It was built with a focus on clean code, separation of concerns, and stateless architecture.

## 🏗️ Architecture & Design

This application runs entirely in memory (Stateless Architecture) to ensure fast calculations and a smooth user experience. 

* **Separation of Concerns:** The project is strictly divided into an ETL extractor, a mathematical quantitative engine, a visualizer, and a frontend controller.
* **In-Memory Processing:** It fetches data directly from the Yahoo Finance API and processes it on the fly. 
* **Caching (`@st.cache_data`):** Repeated queries with the same dates and tickers are cached in RAM. This minimizes API calls and allows the user to tweak confidence levels or portfolio capital instantly.
* **Defensive Programming:** Both the Streamlit UI and the backend Quantitative Engine validate inputs independently (e.g., ensuring portfolio weights sum exactly to 1.0).

## 🧮 Mathematical Approach

The engine calculates risk based on the parametric method (Variance-Covariance), using linear algebra to account for asset correlation:

1. **Daily Returns:** Transforms adjusted close prices into daily percentage changes.
2. **Covariance Matrix ($\Sigma$):** Calculates the variance and covariance across all selected assets.
3. **Portfolio Variance ($\sigma_p^2$):** Computed using the matrix multiplication of the transposed weights vector, the covariance matrix, and the weights vector:
   $$\sigma_p^2 = w^T \cdot \Sigma \cdot w$$
4. **VaR Calculation:** Uses SciPy to find the Z-score based on the selected confidence level (e.g., 95% or 99%), combining it with the portfolio's mean return and volatility.

## ✨ Key Features

* **Dynamic UI:** Users can select multiple tickers, assign custom weights, and set historical time horizons.
* **Data Visualization:** Uses Matplotlib to render an empirical density histogram overlaid with a theoretical normal distribution (Gaussian Bell) and the VaR threshold.
* **Automated Testing:** The core logic is covered by unit tests using `pytest` and mocked API responses to ensure mathematical accuracy and correct exception handling.
* **PEP 8 Compliance:** Code is cleanly formatted and documented with explicit type hints and docstrings.

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Data Extraction:** yfinance, Requests
* **Data Manipulation & Math:** Pandas, NumPy, SciPy
* **Visualization:** Matplotlib
* **Testing:** Pytest, pytest-mock

## 📁 Repository Structure

```text
├── .streamlit/
│   └── config.toml         # Custom dark theme configuration
├── src/
│   ├── core/
│   │   ├── extractor.py    # Yahoo Finance API client and data transformation
│   │   ├── quant_engine.py # Linear algebra and VaR mathematical models
│   │   └── visualizer.py   # Matplotlib histogram and distribution plotting
│   └── utils/
│       └── logger.py       # Custom singleton rotating file logger
├── tests/                  # Pytest unit tests with mocked dependencies
│   ├── core/
│   │   ├── test_extractor.py    
│   │   ├── test_quant_engine.py 
│   │   └── test_visualizer.py
│   ├── utils/
│   │   └── test_logger.py
│   └── test_app.py
├── app.py                  # Main Streamlit application and UI controller
└── requirements.txt        # Production dependencies
```

## 🚀 How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Gabriel-Santiagodev/Risk-Engine-VaR
   cd Risk-Engine-VaR
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Streamlit Dashboard:**
   ```bash
   streamlit run app.py
   ```

5. **Run the test suite (Optional):**
   To run the tests, you need to install the testing dependencies first:
   ```bash
   pip install pytest pytest-mock
   pytest tests
   ```


> **Note:** This app is hosted on Streamlit Community Cloud.
> If it appears asleep, click "Yes, get this app back up!" and wait a few seconds.


## 👨‍💻 Author

**Gabriel Santiago**
* LinkedIn: www.linkedin.com/in/gabrielsantiagodev1
* GitHub: [@Gabriel-Santiagodev](https://github.com/Gabriel-Santiagodev)

## 📄 License

This project is open-source and available under the **MIT License**. Feel free to copy, modify, and use it for your own educational or commercial purposes.