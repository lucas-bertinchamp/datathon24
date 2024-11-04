import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import praw
import boto3
import importlib

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

clients = {
        "reddit" : praw.Reddit(
        client_id='-ZK0wLjgukLtWNG69bIKUg',
        client_secret='G_oo7tapJ88FdCIMagvqZGa5CcsKNA',
        user_agent='script:multi_subreddit_extractor (by u/InspectionFlaky5723)',
        username='InspectionFlaky5723',
        password='ledatathon24cdur'
    ),
        "boto" : boto3.client("bedrock-runtime", region_name="us-west-2"),
        "alpha" : ["L7AML53D7MCJ02DE", "IKOXZ7F7QT7662T2"]
    }

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


    forward_dividend_rate = current_info.get("dividendRate", None)
    trailing_dividend_rate = current_info.get("trailingAnnualDividendRate", None)
    if (forward_dividend_rate and trailing_dividend_rate) is not None and trailing_dividend_rate  != 0:
        dividend_growth_rate = (forward_dividend_rate / trailing_dividend_rate) - 1
    else:
        dividend_growth_rate = None

    non_historical_kpis = {
        "Dividend Yield": current_info.get("dividendYield"),
        "Dividend Growth Rate": dividend_growth_rate,
        "P/E Ratio": current_info.get("trailingPE"),
        "P/B Ratio": current_info.get("priceToBook"),
        "EV/EBITDA": current_info.get("enterpriseToEbitda"),
        "P/S Ratio": current_info.get("priceToSalesTrailing12Months"),
        "ROA": current_info.get("returnOnAssets"),
        "ROE": current_info.get("returnOnEquity"),
    }

    return kpi_data, non_historical_kpis, current_info
    
def plot_summary(summary):
    st.subheader("Summary")
    st.write(summary)

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



def plot_valuation_gauge(stock_price, ddm_value, ticker):
    # Display title and description
    st.title(f"DDM Valuation for {ticker}")
    st.markdown(
    "This analysis is based on the Dividend Discount Model (DDM) valuation method. "
    "Growth rate is calculated as the average of the growth rates between consecutive dividends. "
    "The DDM is reliable for stable, mature companies with consistent dividend growth. "
    "Companies with fluctuating growth rates may yield inaccurate DDM valuations, so results should be interpreted with caution. "
    "In general, a margin of safety of 10-30% is recommended to account for potential valuation variances."
    )
    # Calculate the percentage difference between stock price and DDM value
    percentage_diff = ((stock_price - ddm_value) / ddm_value) * 100
    premium_text = f"{abs(percentage_diff):.1f}% {'premium' if percentage_diff > 0 else 'discount'}"

    # Determine if the stock is undervalued, fairly valued, or overvalued
    if percentage_diff < -10:
        valuation_status = "Undervalued"
    elif percentage_diff > 10:
        valuation_status = "Overvalued"
    else:
        valuation_status = "Fairly Valued"

    # Additional ratings based on zones
    if percentage_diff < -20:
        star_rating = "★★★★★"  # 4 stars for light blue
    elif -20 <= percentage_diff < -10:
        star_rating = "★★★★☆"  # 3 stars for sky blue
    elif -10 <= percentage_diff <= 10:
        star_rating = "★★★☆☆"  # 3 stars for light blue
    elif 10 < percentage_diff <= 20:
        star_rating = "★★☆☆☆"  # 2 stars for salmon
    elif percentage_diff > 20:
        star_rating = "★☆☆☆☆"  # 1 star for red

    # Create Plotly figure
    fig = go.Figure()

    # Add the main gauge with percentage difference as scale
    color = '#007bff' if percentage_diff < 0 else '#FF5733'
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=percentage_diff,
        number={'suffix': "%", 'font': {'size': 30}, 'valueformat': ".1f"},
        title={'text': f"<b>DDM Fair Value: <span style='color:{color};'>{premium_text}</span></b>", 'font': {'size': 28, 'color': 'black'}},
        gauge={
            'axis': {'range': [-50, 50], 'tickwidth': 1, 'tickcolor': "darkgray", 'tickmode': 'array', 
                     'tickvals': [-50, -20, -10, 0, 10, 20, 50],
                     'ticktext': ["-50%", "-20%", "-10%", "0%", "10%", "20%", "50%"]},
            'bar': {'color': "black", 'thickness': 0.2},
            'bgcolor': "white",
            'steps': [
                {'range': [-50, -20], 'color': 'skyblue'},
                {'range': [-20, -10], 'color': 'lightblue'},
                {'range': [-10, 10], 'color': 'white'},
                {'range': [10, 20], 'color': 'peachpuff'},
                {'range': [20, 50], 'color': 'salmon'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': percentage_diff
            }
        }
    ))

    # Display DDM fair value, stock price, and valuation status below the gauge
    fig.add_annotation(
        text=f"Stock Price: ${stock_price:.2f} | Fair Value: ${ddm_value:.2f} | Status: {valuation_status} | Investment rating: {star_rating}",
        x=0.5, y=-0.15,
        showarrow=False,
        font=dict(size=14, color="black"),
        xref="paper", yref="paper",
        align="center"
    )

    return fig

def calculate_ddm_value(ticker):
    stock = yf.Ticker(ticker)
    beta = stock.info.get("beta", None)
    dividend_rate = stock.info.get("dividendRate", None)
    
    # Modulated Parameters
    risk_free_rate = 0.0329  # Latest 10-year Canadian government bond yield
    market_return = 0.057  # Long-term geometric average return of S&P/TSX

    if (dividend_rate or beta) is None:
        return None  # Insufficient data for DDM calculation
    
    discount_rate = risk_free_rate + beta * (market_return - risk_free_rate)
    
    # Fetch historical dividends and calculate growth rate
    dividend_history = stock.dividends
    if len(dividend_history) < 2:
        return None  # Insufficient data for calculating growth rate
    
    # Calculate growth rates between consecutive dividends
    growth_rates = []
    for i in range(1, len(dividend_history)):
        prev_dividend = dividend_history[i - 1]
        current_dividend = dividend_history[i]
        growth_rate = (current_dividend / prev_dividend) - 1
        growth_rates.append(growth_rate)
    
    # Calculate the arithmetic mean of the growth rates
    if growth_rates:
        dividend_growth_rate = sum(growth_rates) / len(growth_rates)
    else:
        return None  # No valid growth rate found
    
    # Ensure growth rate is positive and below the discount rate
    if dividend_growth_rate >= discount_rate or dividend_growth_rate <= 0:
        return None
    
    # DDM Calculation using Gordon Growth Model
    ddm_value = dividend_rate / (discount_rate - dividend_growth_rate)
    
    return ddm_value