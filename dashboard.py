import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_rental_df(df):
    daily_rental_df = df.resample(rule='D', on='dteday_x').agg({
        "instant": "nunique",
        "cnt_x": "sum"
    })
    daily_rental_df = daily_rental_df.reset_index()
    daily_rental_df.rename(columns={
        "instant": "order_count",
        "cnt_x": "revenue"
    }, inplace=True)
    
    return daily_rental_df

def create_sum_order_rental_df(df):
    sum_order_rental_df = df.groupby("mnth_x").cnt_y.sum().reset_index()
    return sum_order_rental_df

def create_byseason_df(df):
    byseason_df = df.groupby('season_x')['instant'].count().reset_index()
    byseason_df.rename(columns={
        'instant': 'customer_count',
        'season_x': 'season'
    }, inplace=True)
    return byseason_df

def create_byholiday_df(df):
    byholiday_df = df.groupby(by="holiday_x")['instant'].nunique().reset_index()
    byholiday_df.rename(columns={
        "instant": "customer_count",
        "holiday_x": "holiday"
    }, inplace=True)
    
    return byholiday_df

def create_byweekday_df(df):
    byweekday_df = df.groupby(by="weekday_x")['instant'].nunique().reset_index()
    byweekday_df.rename(columns={
        "instant": "customer_count",
        "weekday_x": "weekday"
    }, inplace=True)
    
    return byweekday_df


def create_rfm_df(df):
    # Memilih kolom yang dibutuhkan
    rfm_df = df[['instant', 'dteday_x', 'cnt_y']].copy()
    
    # Menghitung Recency (hari terakhir pesanan)
    rfm_df['dteday_x'] = pd.to_datetime(rfm_df['dteday_x'])
    recent_date = rfm_df['dteday_x'].max()
    rfm_df['recency'] = (recent_date - rfm_df['dteday_x']).dt.days
    
    # Menghitung Frequency (jumlah pesanan)
    frequency_df = df.groupby('instant', as_index=False)['cnt_y'].sum()
    rfm_df = pd.merge(rfm_df, frequency_df, on='instant')
    rfm_df.rename(columns={'cnt_y': 'frequency'}, inplace=True)
    
    # Menghitung Monetary (total pembelian)
    monetary_df = df.groupby('instant', as_index=False)['cnt_x'].sum()
    rfm_df = pd.merge(rfm_df, monetary_df, on='instant')
    rfm_df.rename(columns={'cnt_x': 'monetary'}, inplace=True)
    
    # Menghapus kolom yang tidak diperlukan
    rfm_df.drop(['dteday_x'], axis=1, inplace=True)
    
    return rfm_df

main_df = pd.read_csv("main_data.csv")
main_df['dteday_x'] = pd.to_datetime(main_df['dteday_x'])

datetime_columns = ["dteday_x"]  # Perbaikan: Menggunakan hanya satu kolom "dteday_x"

# Sort dan reset index
main_df.sort_values(by="dteday_x", inplace=True)
main_df.reset_index(drop=True, inplace=True)  # Menggunakan drop=True untuk menghapus kolom indeks lama

# Konversi ke datetime
for column in datetime_columns:
    main_df[column] = pd.to_datetime(main_df[column])


# Ambil tanggal minimum dan maksimum dari kolom 'dteday_x'
min_date = main_df["dteday_x"].min()
max_date = main_df["dteday_x"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("data:image/png;base64,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")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
all_df = main_df[(main_df["dteday_x"] >= str(start_date)) & 
                (main_df["dteday_x"] <= str(end_date))]

daily_rental_df = create_daily_rental_df(all_df)
sum_order_rental_df = create_sum_order_rental_df(all_df)
byseason_df = create_byseason_df(all_df)
byholiday_df = create_byholiday_df(all_df)
byweekday_df = create_byweekday_df(all_df)
rfm_df = create_rfm_df(all_df)

#MEMBUAT TOTAL RENTAL MENGGUNAKAN MATRIC
st.header('Bike Sharing')
st.subheader('Daily Rental')

total_rental = daily_rental_df['revenue'].sum()  # Assuming 'cnt_x' represents the revenue

st.metric("Total rental", value=total_rental)

# Plot daily rental
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rental_df["dteday_x"],
    daily_rental_df["revenue"],
    marker='o',
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

#MEMBUAT DIAGRAM RENTAL GRAPHIC
st.subheader("Rental Demographics")
 
col1, col2 = st.columns(2)
 
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y="customer_count", 
        x="holiday",
        data=byholiday_df.sort_values(by="customer_count", ascending=False),
        palette="Blues_d",
        ax=ax
    )
    ax.set_title("Number of Rentals on Holidays", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(
        y="customer_count", 
        x="weekday",
        data=byweekday_df.sort_values(by="customer_count", ascending=False),
        palette="Blues_d",
        ax=ax
    )
    ax.set_title("Number of Rentals on Weekdays", loc="center", fontsize=30)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=15)
    st.pyplot(fig)
 
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(
    x="customer_count", 
    y="season",
    data=byseason_df.sort_values(by="customer_count", ascending=False),
    palette="Blues_d",
    ax=ax
)
ax.set_title("Number of Customers by Season", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel(None)
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

#MEMBUAT DIAGRAM
weekday_data = all_df[all_df['holiday_x'] == 0]
holiday_data = all_df[all_df['holiday_x'] == 1]

# Calculate average casual, registered, and total users for weekday and holiday
avg_casual_weekday = round(weekday_data['casual_y'].mean(), 1)
avg_registered_weekday = round(weekday_data['registered_y'].mean(), 2)
avg_cnt_weekday = round(weekday_data['cnt_y'].mean(), 2)

avg_casual_holiday = round(holiday_data['casual_y'].mean(), 1)
avg_registered_holiday = round(holiday_data['registered_y'].mean(), 2)
avg_cnt_holiday = round(holiday_data['cnt_y'].mean(), 2)

# Display metrics for weekday
st.subheader("Weekday Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average casual users (Weekday)", value=avg_casual_weekday)

with col2:
    st.metric("Average registered users (Weekday)", value=avg_registered_weekday)

with col3:
    st.metric("Average all users (Weekday)", value=avg_cnt_weekday)

# Display metrics for holiday
st.subheader("Holiday Metrics")
col4, col5, col6 = st.columns(3)

with col4:
    st.metric("Average casual users (Holiday)", value=avg_casual_holiday)

with col5:
    st.metric("Average registered users (Holiday)", value=avg_registered_holiday)

with col6:
    st.metric("Average all users (Holiday)", value=avg_cnt_holiday)

# Plotting
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

# Plot for weekday casual users
sns.barplot(y="casual_y", x="instant", data=weekday_data.sort_values(by="casual_y", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("instant", fontsize=30)
ax[0].set_title("By Casual customers (Weekday)", loc="center", fontsize=20)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

# Plot for weekday registered users
sns.barplot(y="registered_y", x="instant", data=weekday_data.sort_values(by="registered_y", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("instant", fontsize=30)
ax[1].set_title("By Registered customers (Weekday)", loc="center", fontsize=20)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

# Plot for weekday total users
sns.barplot(y="cnt_y", x="instant", data=weekday_data.sort_values(by="cnt_y", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("instant", fontsize=30)
ax[2].set_title("Total all users (Weekday)", loc="center", fontsize=20)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

# Copyright
st.caption('Copyright (c) Zahra Areefa Ananta')