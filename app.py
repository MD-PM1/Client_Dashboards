import streamlit as st
import pandas as pd
from datetime import timedelta, datetime

# Set page config
#st.set_page_config(page_title="Payer Matrix Dashboard for " + st.query_params.CID, layout="wide")
st.set_page_config(page_title="Payer Matrix Dashboard for " , layout="wide")

# Helper functions
@st.cache_data
def load_data():

    data = pd.read_csv("Client_Dashboard_Data.csv")
    data['INVOICE_CLOSE_DATE'] = pd.to_datetime(data['INVOICE_CLOSE_DATE'])
   
  #  plan_id = st.query_params.CID
    return data
#.query('INVOICE_PLAN_ID == @plan_id')


def aggregate_data(df, freq): 
    
    return df.groupby(['INVOICE_CLOSE_DATE', 'DISPENSE_TYPE']).agg(
        MEMBERS_SERVED=('MEMBERS_SERVED', 'sum'),
        SAVINGS=('SAVINGS', 'sum'),
        DISPENSES=('DISPENSES', 'sum')

    ).reset_index()

#def get_weekly_data(df):
#    return aggregate_data(df, 'W-MON')

def get_monthly_data(df):
    return aggregate_data(df, 'ME')

def format_with_commas(number):
    return f"{number:,}"

def create_metric_chart(df, column, color, chart_type, height=150):
    st.write(column)
    #chart_data = df[[column]].copy()
    if chart_type=='Bar':
        st.bar_chart(df, x='INVOICE_CLOSE_DATE', y=column, color=color, height=height)
    if chart_type=='Area':
        st.area_chart(df, x='INVOICE_CLOSE_DATE', y=column, color=color, height=height)

def is_period_complete(date, freq):
    today = datetime.now()
    next_month = date.replace(day=28) + timedelta(days=4)
    return next_month.replace(day=1) <= today
    
def calculate_delta(df, column):
    if len(df) < 2:
        return 0, 0
    current_value = df[column].iloc[-1]
    previous_value = df[column].iloc[-2]
    delta = current_value - previous_value
    delta_percent = (delta / previous_value) * 100 if previous_value != 0 else 0
    return delta, delta_percent

def display_metric(col, title, value, df, column, color):
    with col:
        with st.container(border=True):
            delta, delta_percent = calculate_delta(df, column)
            delta_str = f"{delta:+,.0f} ({delta_percent:+.2f}%)"
            st.metric(title, format_with_commas(value), delta=delta_str)
            create_metric_chart(df, column, color, chart_type=chart_selection)
            
            #last_period = df.index[-1]
           # if not is_period_complete(last_period, freq):
           #     st.caption(f"Note: The last {time_frame.lower()[:-2] if time_frame != 'Daily' else 'day'} is incomplete.")

# Load data
df = load_data()

# Set up input widgets
st.logo(image="images/streamlit-logo-primary-colormark-lighttext.png", 
        icon_image="images/streamlit-mark-color.png")

with st.sidebar:
    st.title("Your Savings Dashboard")
    st.header("⚙️ Settings")
    
    max_date = df['INVOICE_CLOSE_DATE'].max().date()
    min_date = df['INVOICE_CLOSE_DATE'].min().date()
    default_start_date = datetime.now() - timedelta(days=365)  # Show a year by default
    default_end_date = datetime.now() 
    start_date = st.date_input("Start date", default_start_date, min_value=None, max_value=None)
    end_date = st.date_input("End date", default_end_date, min_value=default_start_date, max_value=default_end_date )
    
    chart_selection = st.selectbox("Select a chart type",
                                   ("Bar", "Area"))

# Prepare data based on selected time frame
df_display = get_monthly_data(df)

# Display Key Metrics
#st.subheader("All-Time Statistics for " + st.query_params.CID )
st.subheader("All-Time Statistics for ")


metrics = [

    ("Total Members Served", "MEMBERS_SERVED", '#29b5e8'),
    ("Total Savings", "SAVINGS", '#FF9F36'),
    ("Total Dispenses", "DISPENSES", '#D45B90'),
    
]

cols = st.columns(3)

for col, (title, column, color) in zip(cols, metrics):
    total_value = df[column].sum()
    display_metric(col, title, total_value, df_display, column, color)

st.subheader("Selected Duration")

cols = st.columns(3)
for col, (title, column, color) in zip(cols, metrics):
    display_metric(col, title.split()[-1], df_display[column].sum(), df_display, column, color)

st.bar_chart(Data=df_display, x='INVOICE_CLOSE_DATE', y='SAVINGS', stack=False)

# DataFrame display
with st.expander('See DataFrame (Selected time frame)'):
    st.dataframe(df_display)
