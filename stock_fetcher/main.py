import streamlit as st
import datetime
import yfinance as yf
from functions_general import fetch_tsx_tickers, get_stock_data, get_index_data, plot_selected_stock, plot_selected_index, get_financial_metrics, plot_kpi_data, calculate_dcf_value, calculate_relative_valuation, calculate_ddm_value



if __name__ == '__main__' :
    
    # Get the S&P/TSX tickers
    tsx_tickers = fetch_tsx_tickers()

    # Streamlit App Layout
    st.title("S&P/TSX Stock Data Visualization")
    st.write("Select a company from the S&P/TSX Composite Index and use AI agent to analyse the data.")
    
    # Plotting the S&P/TSX index
    spx_data = get_index_data("^GSPTSE", datetime.date(2020, 1, 1), datetime.date.today())
    plot_selected_index("S&P/TSX Composite Index", spx_data)

    # Select company and date range
    company = st.selectbox("Choose an S&P/TSX Company:", list(tsx_tickers.keys()))
    ticker = tsx_tickers[company]
    # Create two columns for the date selectors
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", datetime.date(2020, 1, 1))

    with col2:
        end_date = st.date_input("End Date", datetime.date.today())

    stock_data = get_stock_data(ticker, start_date, end_date)

    # Plotting
    plot_selected_stock(company, stock_data)
    
    # Get financial company data
    historical_kpis, non_historical_kpis = get_financial_metrics(ticker)
    
    # Display financial metrics
    plot_kpi_data(ticker, historical_kpis, non_historical_kpis)
    
    # Example KPIs from non_historical_kpis
    dividend_yield = non_historical_kpis.get("Dividend Yield")
    dividend_growth_rate = non_historical_kpis.get("Dividend Growth Rate")
    roe = non_historical_kpis.get("ROE")
    fcf = historical_kpis["Free Cash Flow"][-1]  # Use the most recent TTM value
    #print(historical_kpis["Free Cash Flow"])
    pe_ratio = non_historical_kpis.get("P/E Ratio")
    pb_ratio = non_historical_kpis.get("P/B Ratio")
    ev_to_ebitda = non_historical_kpis.get("EV/EBITDA")
    ps_ratio = non_historical_kpis.get("P/S Ratio")
    roa = non_historical_kpis.get("ROA")  # Potentially used in relative valuation adjustments
    sentiment_score = 0.05  # Assuming a sentiment score of 5% for demonstration

    # Calculate each valuation
    ddm_value = calculate_ddm_value(dividend_yield, dividend_growth_rate, roe, fcf)
    dcf_value = calculate_dcf_value(fcf, non_historical_kpis.get("Operating Margin"), revenue_growth_rate=0.05, capex=historical_kpis["CapEx"][-1])
    relative_value = calculate_relative_valuation(pe_ratio, pb_ratio, ev_to_ebitda, ps_ratio, sentiment_score=sentiment_score)

    # Display the results
    st.write(f"DDM Value: {ddm_value}")
    st.write(f"DCF Value: {dcf_value}")
    st.write(f"Relative Value: {relative_value}")
