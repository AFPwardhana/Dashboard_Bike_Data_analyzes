import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

all_df = pd.read_csv("all_data.csv")
seasons = ['Spring', 'Winter', 'Summer', 'Fall']
month_names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
years = [2011, 2012]



def agg_season_data(data, season, yr):
    data_season = data[(data['season_x'] == season) & (data['yr_x'] == yr)]
    return data_season.groupby("weathersit_x")[["casual_x", "registered_x"]].sum().reset_index()

def agg_monthly_data(data, mnth, yr):
    data_monthly = data[(data['mnth_x'] == mnth) & (data['yr_x'] == yr)]
    return data_monthly.groupby(["mnth_x", "weathersit_x"])["Total_x"].sum().reset_index().sort_values(by='Total_x', ascending=False)

def agg_high_low(data, yr):
    highest_rent_month = data[data['yr_x'] == yr].groupby(["mnth_x"]).agg({
        "Total_x": "sum"
    }).reset_index().sort_values(by='Total_x', ascending=False).head(3)

    lowest_rent_month = data[data['yr_x'] == yr].groupby(["mnth_x"]).agg({
        "Total_x": "sum"
    }).reset_index().sort_values(by='Total_x', ascending=True).head(3)
    return highest_rent_month, lowest_rent_month

def peek_hour_data(data, mnth, yr):
    year_bike_hours_df = data[(data['mnth_y'] == mnth) & (data['yr_y'] == yr)]
    daily_bike_hours = year_bike_hours_df.loc[year_bike_hours_df.groupby(['mnth_y', 'dteday'])['Total_y'].idxmax()]
    return daily_bike_hours.groupby(['mnth_y', 'dteday', 'hr'])['Total_y'].max().reset_index()




def plot_season_data(year, seasons):
    num_seasons = len(seasons)
    rows = num_seasons
    cols = 1
    fig, axs = plt.subplots(rows, cols, figsize=(15, 5 * num_seasons))
    axs = axs.flatten() if num_seasons > 1 else [axs]

    for i, season in enumerate(seasons):
        agg = agg_season_data(all_df, season, year).sort_values(by="registered_x", ascending=False)
        colors = ['#D3D3D3','#72BCD4'] 
        ax = axs[i]
        sns.barplot(data=agg.melt(id_vars=["weathersit_x"], var_name="Type", value_name="Count"), 
                    x="Count", y="weathersit_x", hue="Type", ax=ax, orient='h',palette=colors)
        ax.set_title(f'{season}')
        ax.set_ylabel('Weather Situation')
        ax.set_xlabel('Sum of Rentals')
        ax.legend(loc='lower right')
        ax.tick_params(axis='x')
        ax.grid(True)
    plt.tight_layout()
    st.pyplot(fig)

def plot_monthly_data(year,selected_months):
    fig, axs = plt.subplots(len(selected_months), 1, figsize=(18, 6 * len(selected_months)), sharey=True)
    if len(selected_months) == 1:
        selected_months = [selected_months[0]]
    for i, month in enumerate(selected_months):
        month_data = agg_monthly_data(all_df, month, year)
        colors = ['#D3D3D3'] * len(month_data) 
        colors[0] = '#72BCD4'
        ax = axs if len(selected_months) == 1 else axs[i]
        sns.barplot(data=month_data, y='weathersit_x', x='Total_x', orient='h', ax=ax, hue="weathersit_x", palette= colors)
        ax.set_title(f'{month} {year}')
        ax.set_xlabel('Total Rentals')
        ax.set_ylabel('Weather Situation')
    plt.tight_layout()
    st.pyplot(fig)

def plot_high_low_data(year):
    highest_rent_month, lowest_rent_month = agg_high_low(all_df, year)
    fig, axs = plt.subplots(1, 2, figsize=(18, 6))
    colors = ['#D3D3D3'] * len(highest_rent_month) 
    colors[2] = '#72BCD4'
    sns.barplot(data=highest_rent_month, x='Total_x', y='mnth_x', ax=axs[0], hue='Total_x', palette= colors)
    axs[0].set_title('Top 3 Months with Highest Total Bike Rentals')
    axs[0].set_xlabel('Total Rentals')
    axs[0].set_ylabel('Month')
    colors = ['#D3D3D3'] * len(lowest_rent_month) 
    colors[0] = '#72BCD4'
    sns.barplot(data=lowest_rent_month, x='Total_x', y='mnth_x', ax=axs[1], hue='Total_x', palette=colors)
    axs[1].set_title('Top 3 Months with Lowest Total Bike Rentals')
    axs[1].set_xlabel('Total Rentals')
    axs[1].set_ylabel('Month')
    axs[1].yaxis.set_label_position('right')
    axs[1].yaxis.tick_right()
    axs[1].invert_xaxis()
    plt.tight_layout()
    st.pyplot(fig)

def plot_peek_hour_data(year, selected_months):
    fig, axs = plt.subplots(len(selected_months), 1, figsize=(18, 6 * len(selected_months)), sharey=True)
    if len(selected_months) == 1:
        selected_months = [selected_months[0]]
    for i, month1 in enumerate(selected_months):
        monthly_data = peek_hour_data(all_df,month1,year)
        ax = axs if len(selected_months) == 1 else axs[i]
        ax.plot(monthly_data['dteday'], monthly_data['hr'], marker='o', linestyle='-')
        for i in range(len(monthly_data)):
            ax.annotate(f'{monthly_data["Total_y"].iloc[i]}',
                        (monthly_data['dteday'].iloc[i], monthly_data['hr'].iloc[i]),
                        textcoords="offset points",
                        xytext=(0, 8),
                        ha='center',
                        rotation=90,
                        color='grey')
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[0], ylim[1] + 0.3 * (ylim[1] - ylim[0]))
        ax.set_xlabel('Date')
        ax.set_ylabel('Hour')
        ax.set_title(f'Peek Hour Bike Rental Count for {month1}\n')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
    plt.tight_layout()
    st.pyplot(fig)


# Streamlit Application
st.title("Bike Rental Analysis Dashboard")
tabs = st.tabs([str(year) for year in years])

with st.sidebar:
    st.header("Filter Pencarian")
    selected_seasons = st.multiselect("Pilih Musim", seasons, default=seasons[:2] ,key=f"seasons_{years}")
    selected_months = st.multiselect("Pilih Bulan", month_names, default=month_names[:1], key="months")
    show_peek_hour = st.checkbox("Show Peek Hour Data", key="peek_hour",value=True)
    show_season = st.checkbox("Show Rentals by Season", key="season",value=True)
    show_month = st.checkbox("Show Rentals by Month", key="month")
    show_high_low = st.checkbox("Show Highest & Lowest Rentals", key="high_low")

for tab, year in zip(tabs, years):
    with tab:
        # Plot Peek Hour Data
        if show_peek_hour:
           st.header(f"Peek Hour Daily in : {', '.join(selected_months)} {year}")
           plot_peek_hour_data(year, selected_months)
        # Plot Season Data
        if show_season:
            st.header(f"Number of Rentals per Season ({year}) relate to weather and type of rent\n")
            plot_season_data(year, selected_seasons)
            
        
        # Plot Monthly Data
        if show_month:
            st.header(f"Number of Rentals in {', '.join(selected_months)} ({year}) relate to weather\n")
            plot_monthly_data(year, selected_months)
        
        # Plot Highest & Lowest Rentals
        if show_high_low:
            st.header(f"Top 3 Months with Highest & Lowest Total Bike Rentals ({year})")
            plot_high_low_data(year)
        
        
       
