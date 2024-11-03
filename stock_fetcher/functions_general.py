import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
# import requests
# import boto3
# import json

# # Access AWS credentials from Streamlit secrets
# aws_access_key_id = st.secrets["aws"]["aws_access_key_id"]
# aws_secret_access_key = st.secrets["aws"]["aws_secret_access_key"]
# aws_session_token = st.secrets["aws"]["aws_session_token"]

# # Initialize the Boto3 client
# bedrock_client = boto3.client(
#     'bedrock-runtime',
#     region_name='us-west-2',
#     aws_access_key_id=aws_access_key_id,
#     aws_secret_access_key=aws_secret_access_key,
#     aws_session_token=aws_session_token
# )

# Function to fetch S&P/TSX Composite companies dynamically from Wikipedia
@st.cache_data
def fetch_tsx_tickers():
    url = "https://en.wikipedia.org/wiki/S%26P/TSX_Composite_Index"
    tables = pd.read_html(url)
    
    # Select the correct table (3rd table, index 2)
    df = tables[3]
    
    # Ensure the correct columns are selected: 'Ticker' and 'Company'
    df = df[['Ticker', 'Company']]
    
    # Create a dictionary mapping Company names to Tickers
    tsx_tickers = df.set_index('Company')['Ticker'].to_dict()
    
    # Add ".TO" suffix for Toronto Exchange tickers compatible with Yahoo Finance
    tsx_tickers = {k: str(v).replace('.', '-') + ".TO" for k, v in tsx_tickers.items()}
    return tsx_tickers

# Fetching Data
@st.cache_data
def get_stock_data(ticker, start, end):
    stock_data = yf.download(ticker, start=start, end=end)
    return stock_data

#Fetching Index Data
@st.cache_data
def get_index_data(ticker, start, end):
    index_data = yf.download(ticker, start=start, end=end)
    return index_data

# Function to plot stock data
@st.cache_data
def plot_selected_stock(company, data) :
    # Check if data is valid
    if data.empty:
        st.warning("No data available for the selected ticker and date range.")
    else:
        # Get the name of the first column, which is the ticker symbol for 'Close' prices
        close_column = data.columns[0]
        data[close_column] = data[close_column].fillna(method='ffill').fillna(method='bfill')
        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[close_column],
                name="Close Price",
                fill='tozeroy',
                fillcolor='rgba(255,100,000,0.1)',
                line=dict(color='red', width=2)
            )
        )

        fig.update_layout(
            title=f"{company} Stock Price Over Time",
            xaxis_title="Date",
            yaxis_title="Stock Price (CAD)",
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )

        # Show plot
        st.plotly_chart(fig)
        


# Function to plot stock data
@st.cache_data
def plot_selected_index(company, data) :
    # Check if data is valid
    if data.empty:
        st.warning("No data available for the selected ticker and date range.")
    else:
        # Get the name of the first column, which is the ticker symbol for 'Close' prices
        close_column = data.columns[0]
        data[close_column] = data[close_column].fillna(method='ffill').fillna(method='bfill')
        
        # Plotting with Plotly        
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data[close_column],
                name="Close Price",
                fill='tozeroy',
                fillcolor='rgba(000,255,000,0.1)',
                line=dict(color='green', width=2)
            )
        )

        fig.update_layout(
            title=f"{company} Index Price Over Time",
            xaxis_title="Date",
            yaxis_title="Index Price (CAD)",
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )

        # Show plot
        st.plotly_chart(fig)
        
        
# Function to get TTM values from the quarterly financials
def get_ttm_value(df, row_name):
    try:
        return df.loc[row_name][:4].sum()  # Sum of the last four quarters for TTM
    except KeyError:
        return None
    
def safe_get_value(df, row, year):
    """
    Safely retrieves the value at a specific row and year in the DataFrame.
    
    Parameters:
    - df: The DataFrame to retrieve data from.
    - row: The row label (index) to access in the DataFrame.
    - year: The year (column) to access in the DataFrame.
    
    Returns:
    - The value at df.loc[row, year] if it exists; otherwise, None.
    """
    if row in df.index and year in df.columns:
        value = df.loc[row].get(year, None)
        # Ensure value is not None and has elements
        return value.values[0] if value is not None and len(value.values) > 0 else None
    return None
        
        
# Get company data for KPI's
@st.cache_data
def get_financial_metrics(ticker):
    stock = yf.Ticker(ticker)
    
    # Get current year
    current_year = pd.Timestamp.now().year
    years = [str(current_year - i) for i in range(3,0,-1)]

    # Extract historical financial data
    # Income statement for revenue and operating income (multi-year)
    income_stmt = stock.financials

    # Balance sheet for assets, liabilities, and equity (multi-year)
    balance_sheet = stock.balance_sheet

    # Cash flow statement for free cash flow, CapEx, etc. (multi-year)
    cash_flow = stock.cashflow

    # # Create a dictionary to store the KPI values for each year
    # kpi_data = {
    #     "Revenue": [income_stmt.loc["Total Revenue"].get(year, None).values[0] if year in income_stmt.columns else None for year in years],
    #     "Operating Margin": [(income_stmt.loc["Operating Income"].get(year, None).values[0] / income_stmt.loc["Total Revenue"].get(year, None).values[0]
    #         if income_stmt.loc["Total Revenue"].get(year, None) is not None and income_stmt.loc["Total Revenue"].get(year, None).values[0] != 0 else None)
    #         if year in income_stmt.columns else None for year in years],
    #     "Free Cash Flow": [cash_flow.loc["Free Cash Flow"].get(year, None).values[0] if year in cash_flow.columns else None for year in years],
    #     "CapEx": [cash_flow.loc["Capital Expenditure"].get(year, None).values[0] if year in cash_flow.columns else None for year in years],
    # }

    # # Add TTM values
    # kpi_data["Revenue"].append(get_ttm_value(stock.quarterly_financials, "Total Revenue"))
    # kpi_data["Operating Margin"].append((get_ttm_value(stock.quarterly_financials, "Operating Income") / get_ttm_value(stock.quarterly_financials, "Total Revenue")) if get_ttm_value(stock.quarterly_financials, "Total Revenue") != 0 else None)
    # kpi_data["Free Cash Flow"].append(get_ttm_value(stock.quarterly_cashflow, "Free Cash Flow"))
    # kpi_data["CapEx"].append(get_ttm_value(stock.quarterly_cashflow, "Capital Expenditure"))

    # Create a dictionary to store the KPI values for each year
    operating_income = [safe_get_value(income_stmt, "Operating Income", year) for year in years]
    total_revenue = [safe_get_value(income_stmt, "Total Revenue", year) for year in years]
    # Calculate Operating Margin with element-wise checking
    operating_margin = [(operating_income[i] / total_revenue[i] if operating_income[i] is not None and total_revenue[i] is not None and total_revenue[i] != 0 else None) for i in range(len(years))]
    kpi_data = {
        "Revenue": [safe_get_value(income_stmt, "Total Revenue", year) for year in years],
        "Operating Margin": operating_margin,
        "Free Cash Flow": [safe_get_value(cash_flow, "Free Cash Flow", year) for year in years],
        "CapEx": [safe_get_value(cash_flow, "Capital Expenditure", year) for year in years],
    }

    # Add TTM values
    operating_income_ttm = get_ttm_value(stock.quarterly_financials, "Operating Income")
    total_revenue_ttm = get_ttm_value(stock.quarterly_financials, "Total Revenue")
    if (total_revenue_ttm and operating_income_ttm) is not None and total_revenue_ttm != 0:
        operating_margin_ttm = (operating_income_ttm / total_revenue_ttm)
    else:
        operating_margin_ttm = None
    kpi_data["Revenue"].append(get_ttm_value(stock.quarterly_financials, "Total Revenue"))
    kpi_data["Operating Margin"].append(operating_margin_ttm)
    kpi_data["Free Cash Flow"].append(get_ttm_value(stock.quarterly_cashflow, "Free Cash Flow"))
    kpi_data["CapEx"].append(get_ttm_value(stock.quarterly_cashflow, "Capital Expenditure"))

    
    # KPIs without multi-year values
    current_info = stock.info
    non_historical_kpis = {
        "Dividend Yield": current_info.get("dividendYield"),
        "Dividend Growth Rate": current_info.get("dividendRate"),
        "P/E Ratio": current_info.get("trailingPE"),
        "P/B Ratio": current_info.get("priceToBook"),
        "EV/EBITDA": current_info.get("enterpriseToEbitda"),
        "P/S Ratio": current_info.get("priceToSalesTrailing12Months"),
        "ROA": current_info.get("returnOnAssets"),
        "ROE": current_info.get("returnOnEquity"),
    }
    
    return kpi_data, non_historical_kpis
    

def plot_kpi_data(ticker, kpi_data, non_historical_kpis):
    
    # Get current year
    current_year = pd.Timestamp.now().year
    years = [str(current_year - i) for i in range(3,0,-1)]
    years.append("TTM")
    
    # Set up columns for plotting
    col1, col2 = st.columns(2)  # Create two columns for side-by-side plotting

    for idx, (kpi, values) in enumerate(kpi_data.items()):
        
        # Check if all values are available
        if all(value is not None for value in values):
        # Adjust values for Operating Margin to display as percentages
            if kpi == "Operating Margin":
                y_values = [v * 100 for v in values]  # Convert to percentages
                text_values = [f"{v*100:.1f}%" for v in values]  # Format as percentages
            else:
                y_values = values  # Keep values as they are
                text_values = [f"${v/1e6:.1f}M" for v in values]  # Format as millions

            # Create the figure
            fig = go.Figure()
            
            # Add bar trace with enhanced aesthetics
            fig.add_trace(go.Bar(
                x=years,
                y=y_values,
                text=text_values,  # Display formatted values
                textposition='outside',  # Show text above bars
                textfont=dict(
                    size=14,  # Larger font size for better readability
                    color='black',  # Darker color for contrast; could also use white for dark bars
                    family="Arial",  # Professional font family
                ),
                insidetextanchor="middle",  # Center text inside if necessary
                marker=dict(
                    color=['#1f77b4', '#0e4d92', '#08306b', '#e69138'],  # Gradient-like colors
                    line=dict(color='black', width=1.2)  # Black edge for clarity
                ),
                name=kpi
            ))

            # Update layout for a professional, financial style
            fig.update_layout(
                title=dict(
                    text=f"{kpi} Over Years",
                    font=dict(size=20, color="#333333"),
                    x=0.5,  # Center the title
                    xanchor="center"
                ),
                xaxis=dict(
                    title="Year",
                    tickfont=dict(size=14, color="#333333"),
                    titlefont=dict(size=16, color="#333333"),
                    type="category"
                ),
                yaxis=dict(
                    title=f"{kpi} ({'%' if kpi == 'Operating Margin' else 'in millions'})",  # Use '%' for Operating Margin
                    tickfont=dict(size=14, color="#333333", family="Arial", weight="bold"),  # Bold font for ticks
                    titlefont=dict(size=16, color="#333333", family="Arial", weight="bold"),  # Bold font for title
                    gridcolor='grey',  # Light gridlines for y-axis
                    gridwidth=0.5,  # Light gridlines for y-axis
                ),
                plot_bgcolor='#f0f2f5',  # Background color for contrast
                showlegend=False,  # Hide legend if only one trace
                margin=dict(l=40, r=40, t=60, b=40)  # Adjust margins
            )

            # Display the plot in alternating columns
            if idx % 2 == 0:
                col1.plotly_chart(fig)
            else:
                col2.plotly_chart(fig)
            
        else:
            st.write(f"{kpi}: Insufficient data for all years")

    # Define the units for each KPI
    kpi_units = {
        "Dividend Yield": "%",
        "Dividend Growth Rate": "-",
        "P/E Ratio": "$/$",
        "P/B Ratio": "$/$",
        "EV/EBITDA": "$/$",
        "P/S Ratio": "$/$",
        "ROA": "%",
        "ROE": "%",
    }

    # Multiply percentage KPIs by 100
    for kpi in ["Dividend Yield", "ROA", "ROE"]:
        if non_historical_kpis[kpi] is not None:
            non_historical_kpis[kpi] *= 100

    # Define the layout of columns
    kpi_names = list(non_historical_kpis.keys())
    kpi_values = list(non_historical_kpis.values())

    # Use Streamlit columns to create the layout
    col1, col2, col3 = st.columns(3)

    # Function to display a KPI in a specific style
    def display_kpi(column, name, value, unit):
        # Formatting value with 2 decimal places
        formatted_value = f"{value:.2f}" if value is not None else "N/A"
        column.markdown(
            f"""
            <div style='text-align: center; background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin: 5px;'>
                <div style='font-size: 16px; font-weight: bold;'>{name}</div>
                <div style='font-size: 32px; font-weight: bold; color: #333333;'>{formatted_value}</div>
                <div style='font-size: 16px;'>{unit}</div>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # Display KPIs in a 3-column layout, except for ROA and ROE
    for i in range(0, len(kpi_names) - 2, 3):
        display_kpi(col1, kpi_names[i], kpi_values[i], kpi_units[kpi_names[i]])
        if i + 1 < len(kpi_names) - 2:
            display_kpi(col2, kpi_names[i + 1], kpi_values[i + 1], kpi_units[kpi_names[i + 1]])
        if i + 2 < len(kpi_names) - 2:
            display_kpi(col3, kpi_names[i + 2], kpi_values[i + 2], kpi_units[kpi_names[i + 2]])

    # Center ROA and ROE in the middle of two columns
    col_center_1, col_center_2 = st.columns([1, 1])  # Two equally sized columns
    display_kpi(col_center_1, "ROA", non_historical_kpis["ROA"], kpi_units["ROA"])
    display_kpi(col_center_2, "ROE", non_historical_kpis["ROE"], kpi_units["ROE"])



# # Function to retrieve financial metrics via Bedrock
# def get_financial_metrics(company_name):
#     # Define the prompt for Bedrock to extract financial metrics
#     prompt = f"Please provide key financial metrics such as revenue, profit, and EPS for {company_name}."

#     # Prepare the request payload for Bedrock
#     request_payload = {
#         "inputText": prompt,
#         "textGenerationConfig": {
#             "maxTokenCount": 512,
#             "temperature": 0.5,
#             "topP": 0.9
#         }
#     }

#     # Convert the payload to JSON format
#     request_body = json.dumps(request_payload)

#     # Invoke the Bedrock model
#     response = bedrock_client.invoke_model(
#         modelId='amazon.titan-text-express-v1',  # Replace with the appropriate Bedrock model ID
#         body=request_body
#     )

#     # Parse and return the response
#     response_body = json.loads(response['body'].read())
#     financial_metrics = response_body['results'][0]['outputText']

#     return financial_metrics

# def extract_data(uploaded_file):
#     if uploaded_file is not None:
#         for page_layout in extract_pages(uploaded_file):
#             for element in page_layout:
#                 st.write(element)

def calculate_dcf(fcf, y2_revenues, operating_margin, capex):
    """
    Calculates the value using the Discounted Cash Flow (DCF) Model.
    Returns None if any required KPI is missing.
    """
    revenue_growth_rate = 100*(y2_revenues[-1]-y2_revenues[-2]) / y2_revenues[-2]
    if None in (fcf, revenue_growth_rate, operating_margin, capex):
        return None  # Missing data; return None to indicate incomplete input
    
    try:
        # Simplified DCF calculation: assuming one period for demonstration
        # DCF = FCF * (1 + growth_rate) / (discount_rate - growth_rate)
        discount_rate = 0.1  # Placeholder discount rate, usually derived from WACC
        growth_rate = revenue_growth_rate  # Growth in FCF
        projected_fcf = fcf * (1 + growth_rate)
        dcf_value = projected_fcf / (discount_rate - growth_rate)
        return dcf_value
    except ZeroDivisionError:
        return None


def calculate_ddm_value(dividend_yield, dividend_growth_rate, roe, fcf, discount_rate=None):
    # Assume a default discount rate if not provided (e.g., use ROE as a proxy if appropriate)
    if discount_rate is None:
        discount_rate = roe  # Assuming ROE can represent the required rate of return

    # Convert dividend yield into an annualized dividend amount
    dividend_per_share = fcf * dividend_yield

    # Calculate DDM value using the formula
    if discount_rate > dividend_growth_rate:
        ddm_value = (dividend_per_share * (1 + dividend_growth_rate)) / (discount_rate - dividend_growth_rate)
    else:
        ddm_value = None  # Set to None if calculation conditions aren't met

    return ddm_value


def calculate_relative_valuation(pe_ratio, pb_ratio, ev_to_ebitda, ps_ratio, sentiment_score=None):
    # Calculate an average of key valuation multiples
    relative_valuation = (pe_ratio + pb_ratio + ev_to_ebitda + ps_ratio) / 4

    # Adjust based on sentiment score (optional)
    if sentiment_score is not None:
        relative_valuation *= (1 + sentiment_score)

    return relative_valuation

def valuation_analysis(ticker):
    stock = yf.Ticker(ticker)
    
    # Access available analyst-related data
    target_mean_price = stock.info.get("targetMeanPrice")
    target_low_price = stock.info.get("targetLowPrice")
    target_high_price = stock.info.get("targetHighPrice")
    current_price = stock.history(period="1d")["Close"].iloc[-1]
    forward_pe = stock.info.get("forwardPE")
    trailing_pe = stock.info.get("trailingPE")
    eps = stock.info.get("trailingEps")

    # Display data in Streamlit
    st.title(f"Research Analysis for {ticker}")

    # Display Analyst Price Targets
    st.subheader("Analyst Price Targets")
    st.metric("Current Price", f"${current_price:.2f}")
    st.metric("Average Target Price", f"${target_mean_price:.2f}" if target_mean_price else "N/A")
    st.metric("Low Target Price", f"${target_low_price:.2f}" if target_low_price else "N/A")
    st.metric("High Target Price", f"${target_high_price:.2f}" if target_high_price else "N/A")

    # Display PE Ratios and EPS
    st.subheader("Valuation Metrics")
    st.metric("Trailing P/E", f"{trailing_pe:.2f}" if trailing_pe else "N/A")
    st.metric("Forward P/E", f"{forward_pe:.2f}" if forward_pe else "N/A")
    st.metric("EPS (Trailing)", f"${eps:.2f}" if eps else "N/A")
    
    # Plot price vs target range
    fig = go.Figure()

    # Add current price
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=current_price,
        title={'text': "Current Price"},
        delta={'reference': target_mean_price},
        gauge={'axis': {'range': [target_low_price, target_high_price]}}
    ))

    # Show in Streamlit
    st.plotly_chart(fig)