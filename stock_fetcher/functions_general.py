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
        client_id='zzAJ_bRHjE-f9dJh5ivO1w',
        client_secret='JXTg1re8ADZYCkCFKFw48D-j8BTUyg',
        user_agent='script:multi_subreddit_extractor (by u/Legal-Assistance6692)',
        username='Legal-Assistance6692',
        password='f54Uk92Z'
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
        
        # Plotting with Plotly
        st.subheader(f"Stock Price for {company}")
        
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
    kpi_data = {
        "Revenue": [income_stmt.loc["Total Revenue"].get(year, None).values[0] if year in income_stmt.columns else None for year in years],
        "Operating Margin": [(income_stmt.loc["Operating Income"].get(year, None).values[0] / income_stmt.loc["Total Revenue"].get(year, None).values[0]
            if income_stmt.loc["Total Revenue"].get(year, None) is not None and income_stmt.loc["Total Revenue"].get(year, None).values[0] != 0 else None)
            if year in income_stmt.columns else None for year in years],
        "Free Cash Flow": [cash_flow.loc["Free Cash Flow"].get(year, None).values[0] if year in cash_flow.columns else None for year in years],
        "CapEx": [cash_flow.loc["Capital Expenditure"].get(year, None).values[0] if year in cash_flow.columns else None for year in years],
    }

    # Add TTM values
    kpi_data["Revenue"].append(get_ttm_value(stock.quarterly_financials, "Total Revenue"))
    kpi_data["Operating Margin"].append((get_ttm_value(stock.quarterly_financials, "Operating Income") / get_ttm_value(stock.quarterly_financials, "Total Revenue")) if get_ttm_value(stock.quarterly_financials, "Total Revenue") != 0 else None)
    kpi_data["Free Cash Flow"].append(get_ttm_value(stock.quarterly_cashflow, "Free Cash Flow"))
    kpi_data["CapEx"].append(get_ttm_value(stock.quarterly_cashflow, "Capital Expenditure"))

    # KPIs without multi-year values
    current_info = stock.info
    non_historical_kpis = {
        "Dividend Yield": current_info.get("dividendYield"),
        "P/E Ratio": current_info.get("trailingPE"),
        "P/B Ratio": current_info.get("priceToBook"),
        "EV/EBITDA": current_info.get("enterpriseToEbitda"),
        "P/S Ratio": current_info.get("priceToSalesTrailing12Months"),
        "ROA": current_info.get("returnOnAssets"),
        "ROE": current_info.get("returnOnEquity"),
    }
    
    return kpi_data, non_historical_kpis
    

def plot_kpi_data(ticker, kpi_data, non_historical_kpis):
    # Display KPIs with historical data as bar plots
    st.title(f"Financial KPI Analysis for {ticker}")
    
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

    # Display KPIs without historical data in a table
    st.subheader("Current KPIs (Non-historical)")
    kpi_table = pd.DataFrame(non_historical_kpis.items(), columns=["KPI", "Value"])
    st.table(kpi_table)
    
def plot_summary(summary):
    st.subheader("Summary")
    st.write(summary)
    

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
