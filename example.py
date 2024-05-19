import streamlit as st
import pandas as pd
import numpy as np
# For data exporting
from io import BytesIO
import xlsxwriter
from pyxlsb import open_workbook as open_xlsb
from yahooquery import Ticker

mil = 1000000
fetched_data = []
ebitda_ttm_list = []
total_debt = []
cash = []
shareoutstanding = []
total_revenue_list = []
minority_interest = []
netincome_ttm_list = []

def fetching_data(stock):
    try:
        data = Ticker(stock)
        # Market Cap
        market_cap = round(data.summary_detail[stock]['marketCap'] / mil, 3)
        # Income Statement Data
        # Total revenue
        if np.isnan(data.income_statement()['TotalRevenue'].iloc[4]):
            total_revenue = round(data.income_statement()['TotalRevenue'].iloc[3] / mil, 3)
            total_revenue_list.append(total_revenue)
        else:
            total_revenue = round(data.income_statement()['TotalRevenue'].iloc[4] / mil, 3)
            total_revenue_list.append(total_revenue)

        # Net income
        if np.isnan(data.cash_flow()['NetIncome'].iloc[4]):
            netincome = round(data.cash_flow()['NetIncome'].iloc[3] / mil, 3)
        else:
            netincome = round(data.cash_flow()['NetIncome'].iloc[4] / mil, 3)

        # EBITDA
        if np.isnan(data.income_statement()['EBITDA'].iloc[4]):
            ebitda = round(data.income_statement()['EBITDA'].iloc[3] / mil, 3)
        else:
            ebitda = round(data.income_statement()['EBITDA'].iloc[4] / mil, 3)

        # Income Statement (TTM)
        # Total revenue (TTM)
        if np.isnan(data.income_statement()['TotalRevenue'].iloc[5]):
            total_revenue_ttm = 'NaN'
        else:
            total_revenue_ttm = round(data.income_statement()['TotalRevenue'].iloc[5] / mil, 3)

        # Net income (TTM)
        if np.isnan(data.cash_flow()['NetIncome'].iloc[4]):
            netincome_ttm = 'NaN'
            netincome_ttm_list.append(netincome_ttm)
        else:
            netincome_ttm = round(data.cash_flow()['NetIncome'].iloc[4] / mil, 3)
            netincome_ttm_list.append(netincome_ttm)

        # EBITDA (TTM)
        if np.isnan(data.income_statement()['EBITDA'].iloc[5]):
            ebitda_ttm = 'NaN'
            ebitda_ttm_list.append(ebitda_ttm)
        else:
            ebitda_ttm = round(data.income_statement()['EBITDA'].iloc[5] / mil, 3)
            ebitda_ttm_list.append(ebitda_ttm)

        # PE, EV to Revenue, EV to Ebitda (TTM)
        # PE Ratio (TTM)
        pe_ttm = data.summary_detail[stock]['trailingPE']

        # PE forward
        pe = data.summary_detail[stock]['forwardPE']

        # EV to Ebitda (TTM)
        EVtoEBITDA_ttm = data.key_stats[stock]['enterpriseToEbitda']

        # EV to Revenue (TTM)
        EVtoRevenue_ttm = data.key_stats[stock]['enterpriseToRevenue']

        # Enterprise
        enterprise = round(data.key_stats[stock]['enterpriseValue'] / mil, 3)

        # Ebit = ebitda - depreciation_and_amortization
        if np.isnan(data.income_statement()['EBIT'].iloc[4]):
            ebit = round(data.income_statement()['EBIT'].iloc[3] / mil, 3)
        else:
            ebit = round(data.income_statement()['EBIT'].iloc[4] / mil, 3)

        # Ebit (TTM)
        if np.isnan(data.income_statement()['EBIT'].iloc[5]):
            ebit_ttm = 'NaN'
        else:
            ebit_ttm = round(data.income_statement()['EBIT'].iloc[5] / mil, 3)

        # EV to Ebitda
        EVtoEBITDA = round(enterprise / ebitda, 3)

        # EV to Revenue
        EVtoRevenue = round(enterprise / total_revenue, 3)

        # Balance Sheet
        # Cash and cash equivalents
        if np.isnan(data.balance_sheet()['CashAndCashEquivalents'].iloc[3]):
            cash.append('N/A')
        else:
            cash.append(round(data.balance_sheet()['CashAndCashEquivalents'].iloc[3] / mil,3))
        # Total debt = long-term debt + short-term + current portion of long-term debt
        if np.isnan(data.balance_sheet()['TotalDebt'].iloc[3]):
            total_debt.append('N/A')
        else:
            total_debt.append(round(data.balance_sheet()['TotalDebt'].iloc[3] / mil,3))

        # Shares Outstanding
        shareoutstanding.append(round(data.key_stats[stock]['sharesOutstanding'] / mil, 3))

        # Company Name (long name)
        company_name = data.quote_type[stock]['longName'] if data.quote_type[stock]['longName'] else "N/A"

        # Industry
        industry = data.asset_profile[stock]['industry'] if data.asset_profile[stock]['industry'] else "N/A"

        # Extract the required information
        fetch_data = (
            stock,
            company_name,
            industry,
            market_cap,
            enterprise,
            total_revenue,
            ebitda,
            ebit,
            total_revenue_ttm,
            ebitda_ttm,
            ebit_ttm,
            netincome,
            EVtoRevenue,
            EVtoRevenue_ttm,
            EVtoEBITDA,
            EVtoEBITDA_ttm,
            pe,
            pe_ttm,
        )
        fetched_data.append(fetch_data)
    except Exception as e:
        st.warning(e)
        print(e)

max_value = ['', '', '', '', '', '', '', '', '', '', '', 'Max']
min_value = ['', '', '', '', '', '', '', '', '', '', '', 'Min']
percentile_90 = ['', '', '', '', '', '', '', '', '', '', '', '90th percentile']
percentile_80 = ['', '', '', '', '', '', '', '', '', '', '', '80th percentile']
percentile_70 = ['', '', '', '', '', '', '', '', '', '', '', '70th percentile']
percentile_60 = ['', '', '', '', '', '', '', '', '', '', '', '60th percentile']
percentile_40 = ['', '', '', '', '', '', '', '', '', '', '', '40th percentile']
percentile_25 = ['', '', '', '', '', '', '', '', '', '', '', '25th percentile']
mean_value = ['', '', '', '', '', '', '', '', '', '', '', 'Mean']
median_value = ['', '', '', '', '', '', '', '', '', '', '', 'Median']
intrinsic_value = []

# Calculate percentile of EV/Revenue, EV/EBITDA, etc
def stats_calc(fetched_data):
    data = [[], [], [], [], [], []]
    for item in fetched_data:
        values = item
        try:
            if float(values[12]) > 0:
                data[0].append(float(values[12]))
        except:
            pass
        try:
            if float(values[13]) > 0:
                data[1].append(float(values[13]))
        except:
            pass
        try:
            if float(values[14]) > 0:
                data[2].append(float(values[14]))
        except:
            pass
        try:
            if float(values[15]) > 0:
                data[3].append(float(values[15]))
        except:
            pass
        try:
            if float(values[16]) > 0:
                data[4].append(float(values[16]))
        except:
            pass
        try:
            if float(values[17]) > 0:
                data[5].append(float(values[17]))
        except:
            pass
    for item in data:
        max_value.append(round(np.max(item), 2))
        min_value.append(round(np.min(item), 2))
        percentile_90.append(round(np.percentile(item, 90), 2))
        percentile_80.append(round(np.percentile(item, 80), 2))
        percentile_70.append(round(np.percentile(item, 70), 2))
        percentile_60.append(round(np.percentile(item, 60), 2))
        percentile_40.append(round(np.percentile(item, 40), 2))
        percentile_25.append(round(np.percentile(item, 25), 2))
        mean_value.append(round(np.mean(item), 2))
        median_value.append(round(np.median(item), 2))

# Display data
def display():
    df = pd.DataFrame(fetched_data, columns=("Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                                             "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)", "TTM EBITDA (m)",
                                             "TTM EBIT (m)",
                                             "TTM Net Income (m)", "EV/Revenue", "TTM EV/Revenue", "EV/EBITDA",
                                             "TTM EV/EBITDA", "Trailling PE", "TTM PE"))
    index = ['Main Company']
    for i in range(1, count + 1):
        j = 'Competitor ' + str(i)
        index.append(j)
    df.index = index
    data = []
    data.append(max_value)
    data.append(min_value)
    data.append(percentile_90)
    data.append(percentile_80)
    data.append(percentile_70)
    data.append(percentile_60)
    data.append(percentile_40)
    data.append(percentile_25)
    data.append(median_value)
    data.append(mean_value)
    df1 = pd.DataFrame(data, columns=("Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                                      "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)", "TTM EBITDA (m)", "TTM EBIT (m)",
                                      "TTM Net Income (m)", "EV/Revenue", "TTM EV/Revenue", "EV/EBITDA",
                                      "TTM EV/EBITDA", "Trailling PE", "TTM PE"))
    df1_index = ['Max Value', 'Min Value', '90th Percentile', '80th Percentile', '70th Percentile', '60th Percentile',
                 '40th Percentile', '25th Percentile', 'Median Value', 'Mean Value']
    df1.index = df1_index
    result = pd.concat([df, df1])
    st.dataframe(result)
    print(result)

EVtoEBITDA_iv = []
EVtoRevenue_iv = []
PEratio_iv = []

# Find main company's intrinsic value
def intrinsic_va():
    cal = [max_value, min_value, percentile_90, percentile_80, percentile_70, percentile_60, mean_value,
           percentile_40, percentile_25]
    # intrinsic value
    for i in range(0, 9):
        try:
            EVtoEBITDA_iv.append(round(((cal[i][15] * ebitda_ttm_list[0]) - total_debt[0] + cash[0]) / shareoutstanding[0], 2))
        except Exception as e:
            EVtoEBITDA_iv.append('N/A')
            print(e)
        try:
            EVtoRevenue_iv.append(round(
                ((cal[i][13] * total_revenue_list[0]) - total_debt[0] + cash[0]) / shareoutstanding[0], 2))
        except Exception as e:
            EVtoRevenue_iv.append('N/A')
            print(e)
        try:
            PEratio_iv.append(round(cal[i][17] * netincome_ttm_list[0] / shareoutstanding[0], 2))
        except:
            PEratio_iv.append('N/A')

    intrinsic_value = [EVtoEBITDA_iv, EVtoRevenue_iv, PEratio_iv]
    iv = pd.DataFrame(intrinsic_value, columns=(
    'Max', 'Min', '90th percentile', '80th percentile', '70th percentile', '60th percentile', '50th percentile',
    '40th percentile', '25th percentile'))
    index_iv = ['EV/EBITDA', 'EV/Revenue', 'PE ratio']
    iv.index = index_iv
    st.dataframe(iv)
    print('intrinsic value:\n')
    print(iv)

# Find current stock price
def current_price(main_company):
    data = Ticker(main_company)
    currentprice = data.financial_data[main_company]['currentPrice']
    return currentprice

# Find company's name
def longname(stock):
    data = Ticker(stock)
    company_name = data.quote_type[stock]['longName'] if data.quote_type[stock]['longName'] else "N/A"
    return company_name

# Exporting data for users to download it as excel or csv file
def export_data():
    df = pd.DataFrame(fetched_data, columns=("Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                                             "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)", "TTM EBITDA (m)",
                                             "TTM EBIT (m)",
                                             "TTM Net Income (m)", "EV/Revenue", "TTM EV/Revenue", "EV/EBITDA",
                                             "TTM EV/EBITDA", "Trailling PE", "TTM PE"))
    index = ['Main Company']
    for i in range(1, count + 1):
        j = 'competitor' + str(i)
        index.append(j)
    df.index = index
    data = []
    data.append(max_value)
    data.append(min_value)
    data.append(percentile_90)
    data.append(percentile_80)
    data.append(percentile_70)
    data.append(percentile_60)
    data.append(percentile_40)
    data.append(percentile_25)
    data.append(median_value)
    data.append(mean_value)
    df1 = pd.DataFrame(data, columns=("Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                                      "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)", "TTM EBITDA (m)", "TTM EBIT (m)",
                                      "TTM Net Income (m)", "EV/Revenue", "TTM EV/Revenue", "EV/EBITDA",
                                      "TTM EV/EBITDA", "Trailling PE", "TTM PE"))
    temp = pd.concat([df, df1])

    index_iv = ['Intrinsic Value', 'EV/EBITDA', 'EV/Revenue', 'PE ratio']
    intrinsic_value = [EVtoEBITDA_iv, EVtoRevenue_iv, PEratio_iv]
    iv_column = ['Max', 'Min', '90th percentile', '80th percentile', '70th percentile', '60th percentile',
                 '50th percentile', '40th percentile', '25th percentile']
    temp_iv = [iv_column, EVtoEBITDA_iv, EVtoRevenue_iv, PEratio_iv]
    iv = pd.DataFrame(temp_iv, columns=("Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                                      "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)"))

    iv.index = index_iv
    result = pd.concat([temp,iv])
    col1, col2 = st.columns(2)
    with col1:
        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')
        csv = convert_df(result)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='Trading_Comps.csv',
            mime='text/csv',
        )
    with col2:
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True, 'nan_inf_to_errors': True})
        worksheet = workbook.add_worksheet()
        column = ["","Ticker", "Name", "Industry", 'Market Cap (m)', "EV (m)", "Revenue (m)",
                   "EBITDA (m)", "EBIT (m)", "TTM Revenue (m)", "TTM EBITDA (m)", "TTM EBIT (m)",
                   "TTM Net Income (m)", "EV/Revenue", "TTM EV/Revenue", "EV/EBITDA",
                   "TTM EV/EBITDA", "Trailling PE", "TTM PE"]
        for i in range(0,len(column)):
            worksheet.write(0, i, column[i])
        worksheet.write(1, 0, 'Main Company')
        for i in range(2, count+2):
            worksheet.write(i, 0, 'Competitors '+str(i-1))
        final = result.values.tolist()
        for i in range(1, count+2):
            for j in range(1, len(column)):
                worksheet.write(i, j, final[i-1][j-1])
        for i in range(count+2, count+12):
            for j in range(1, len(column)):
                worksheet.write(i, j, data[i-count-2][j-1])

        for i in range(1,10):
            worksheet.write(count+12,i,iv_column[i-1])
        for i in range(count+13, count+16):
                for j in range(1,10):
                    worksheet.write(i, j, intrinsic_value[i-count-13][j-1])
        for i in range(count+12,count+16):
            worksheet.write(i, 0, index_iv[i-count-12])
        workbook.close()
        st.download_button(
            label="Download data as Excel",
            data=output.getvalue(),
            file_name="Trading-Comps.xlsx",
            mime="application/vnd.ms-excel"
        )
###################################################################
# Page setup
st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
	page_title='Trading Comps',  # String or None. Strings get appended with "• Streamlit".
	page_icon='jams_icon.ico',  # String, anything supported by st.image, or None.
)
image_url = "https://i.imgur.com/cnx9XYd.png"
st.image(image_url, output_format="PNG", width=200)
header = '<p style="font-family:Times New Roman; color:black; font-size: 30px;">Trading Comps</p>'
st.markdown(header, unsafe_allow_html=True)
col1, col2 = st.columns([1,3])
with col1:
    ticker = st.text_input('Enter main company\'s ticker:')
with col2:
    competitors = st.text_input('Enter competitor\'s ticker: (split by comma and a space)')
count = 0
fetch_button = st.button('Fetch data')
if fetch_button:
    #checker = check_name(ticker)
    #if checker == 1:
    #    st.warning('Please enter correct ticker!')
    #    st.stop()
    fetching_data(ticker)
    tickers = competitors.split(', ')
    for ticker2 in tickers:
        #checker = check_name(ticker2)
        #if checker == 1:
        #    st.warning('Please enter correct ticker!')
        #    st.stop()
        fetching_data(ticker2)
        count = count + 1

    stats_calc(fetched_data)
    display()
    col3, col4 = st.columns([1, 3])
    with col3:
        header = '<p style="font-family:Times New Roman; color:black; font-size: 25px;">Current Price</p>'
        st.markdown(header, unsafe_allow_html=True)
        name = longname(ticker)
        st.markdown(name, unsafe_allow_html=False)
        price = current_price(ticker)
        st.markdown(price, unsafe_allow_html=False)
    with col4:
        header = '<p style="font-family:Times New Roman; color:black; font-size: 25px;">Intrinsic Value</p>'
        st.markdown(header, unsafe_allow_html=True)
        # Intrinsic value
        intrinsic_va()
    export_data()

# Display rights
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('example.css')
# Footer
st.markdown(
    """
    <div class="footer">
        Developed by JAMS Investment. All rights reserved. Version 2 2023.11
    </div>
    """,
    unsafe_allow_html=True
)