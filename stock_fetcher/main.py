import streamlit as st
import datetime
import yfinance as yf
from functions_general import *
from functions_general import clients
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from generate_summary import generate_summary_from_sources


if __name__ == '__main__' :
    
    st.set_page_config(layout="wide")
    
    # Get the S&P/TSX tickers
    tsx_tickers = fetch_tsx_tickers()

    # Streamlit App Layout
    st.title("S&P/TSX Company AI Analysis Tool")
    # Introduction
    st.write("Select a company from the S&P/TSX Composite Index and use AI agent to collect and analyse the data.")
    st.write("Use wide mode and light theme for a better experience in Streamlit settings.")

    # Select company and date range
    company = st.selectbox("Choose an S&P/TSX Company:", list(tsx_tickers.keys()))
    ticker = tsx_tickers[company]
    if ticker == 'nan.TO' :
        ticker = 'NA.TO'
    # Create two columns for the date selectors
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.date(2020, 1, 1))
    with col2:
        end_date = st.date_input("End Date", datetime.date.today())

    # Heading
    title_to_use = str(company) + " - " + str(ticker)
    # Display the title with centered alignment and all caps
    st.markdown(
        f"<h1 style='text-align: center; text-transform: uppercase;'>{title_to_use}</h1>",
        unsafe_allow_html=True
    )
    
    # General ingformation on company :
    st.title(f"Up-to-date General information on {company}")
    # Stock price and index price
    st.subheader(f"Stock Price for {ticker} and S&P/TSX Composite Index")
    # Create two columns for the date selectors
    col1, col2 = st.columns(2)
    
    with  col1:
        # Plotting the selected company's stock data
        stock_data = get_stock_data(ticker, start_date, end_date)
        plot_selected_stock(company, stock_data)

    with col2:
        # Plotting the S&P/TSX index
        spx_data = get_index_data("^GSPTSE", start_date, end_date)
        plot_selected_index("S&P/TSX Composite Index", spx_data)
    
    # Short company description
    st.subheader(f"Short description of {company}")
    stock = yf.Ticker(ticker)
    #st.write(stock.info)
    company_info = stock.info.get("longBusinessSummary", "No description available")
    st.write(company_info)
    
    # Get financial company data
    historical_kpis, non_historical_kpis, _ = get_financial_metrics(ticker)
    
    # Display financial metrics
    st.title(f"Financial KPI Analysis for {company}")
    plot_kpi_data(ticker, historical_kpis, non_historical_kpis)
    
    # Call DDM with cost of equity as discount rate
    ddm_value = calculate_ddm_value(ticker)
    current_stock = stock_data["Adj Close"].iloc[-1].values[0]
    if ddm_value:
        # Plot the valuation gauge and display it in Streamlit
        fig = plot_valuation_gauge(current_stock, ddm_value, ticker)
        st.plotly_chart(fig)
    else:
        st.markdown(
            "<div style='padding: 10px; border-left: 4px solid #FF5733; background-color: #f9f9f9;'>"
            "<h4 style='color: #FF5733;'>Unable to Calculate DDM Value</h4>"
            "<p style='font-size: 16px;'>The Dividend Discount Model (DDM) valuation couldn't be determined due to one of the following reasons:</p>"
            "<ul style='padding-left: 20px; font-size: 16px;'>"
            "<li><b>Insufficient Dividend Data</b>: The required historical or current dividend information is unavailable on yfinance.</li>"
            "<li><b>Unstable Dividend Rate</b>: The company may not have a consistent, predictable dividend payout, making DDM unsuitable for valuation.</li>"
            "<li><b>Negative Dividend Growth Rate</b>: The DDM is not applicable when dividends are expected to decline, as the model assumes a steady, positive growth rate.</li>"
            "<li><b>Issue with the Discount Rate</b>: The discount rate for the given company is smaller than the divident growth rate.</li>"
            "</ul>"
            "<p style='font-size: 16px;'>Please ensure the company has a stable dividend history and data is available for accurate DDM analysis.</p>"
            "</div>",
            unsafe_allow_html=True
        )
    
    st.title(f"Financial Analysis summary for {company}")
    
    # Ensure the folder exists
    output_folder = "../pdf/uploaded_history_"+str(ticker)
    os.makedirs(output_folder, exist_ok=True)

    # PDF Drop Zone
    st.subheader("PDF Drop Zone: for enhanced AI analysis")
    st.write(f"Drop a relevant Financial Document PDF about {company} here to improve AI generated report")

    # Create a PDF drop zone with multiple file upload support
    uploaded_files = st.file_uploader("Drop your PDF files here", type="pdf", accept_multiple_files=True)

    # Initialize an empty list to store the paths of the uploaded files
    if "pdf" not in st.session_state:
        st.session_state.pdf = []
    
    # Button to confirm all files are uploaded
    if st.button("Confirm Upload"):
        st.session_state.pdf = []
        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Create a file path for each uploaded file
                file_path = os.path.join(output_folder, uploaded_file.name)

                # Save the file to the specified directory
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                # pdfs is appended the path of the pdfs
                st.session_state.pdf.append(file_path)

            st.success(f"All files have been saved to {output_folder}")
        else:
            st.warning("No files were uploaded.")
    
    st.write('\n')
    
    if st.button("Generate analysis summary from AI (can take a few minutes)"):
        model_id = "meta.llama3-1-405b-instruct-v1:0"
        try:
            summary = generate_summary_from_sources(clients, company, ticker, model_id, st.session_state.pdf, verbose=True)
        except Exception as e:
            summary = f"Error in generating summary"
            
        plot_summary(summary)
        print("Done")
    