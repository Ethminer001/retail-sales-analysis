import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['font.size'] = 10

# ============================================================
# 1. DATABASE CONNECTION
# ============================================================
def connect_to_database():
    """Establish MySQL connection"""
    try:
        import os 
        import mysql.connector 
        from dotenv import load_dotenv
        # Load environment variables from .env file
        load_dotenv() 
        conn = mysql.connector.connect( 
            host="localhost", 
            user="root", 
            password=os.getenv("MYSQL_PASSWORD"), # ✅ no hardcoded password 
            database="MINI_SALES_PROJECT" )
        print("✅ Database connected successfully!")
        return conn
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        return None

conn = connect_to_database()

# ============================================================
# 2. LOAD AND PREPARE DATA
# ============================================================
def load_data(connection):
    """Load and prepare retail sales data"""
    query = """
    SELECT 
        transactions_id,
        sale_date,
        sale_time,
        customer_id,
        gender,
        age,
        category,
        quantity,
        price_per_unit,
        cogs,
        total_sale,
        (total_sale - cogs) AS profit
    FROM retail_sales;
    """
    df = pd.read_sql(query, connection)
    
    # Data type conversions
    df['sale_date'] = pd.to_datetime(df['sale_date'])
    df['sale_time'] = pd.to_timedelta(df['sale_time'].astype(str))
    
    # Extract temporal features
    df['month'] = df['sale_date'].dt.month_name()
    df['month_num'] = df['sale_date'].dt.month
    df['day_of_week'] = df['sale_date'].dt.day_name()
    df['day_num'] = df['sale_date'].dt.dayofweek
    df['hour'] = df['sale_time'].dt.components.hours
    
    # Age groups
    df['age_group'] = pd.cut(df['age'], 
                              bins=[0, 25, 35, 45, 55, 65, 100],
                              labels=['18-25', '26-35', '36-45', '46-55', '56-65', '65+'])
    
    # Profit margin
    df['profit_margin'] = (df['profit'] / df['total_sale'] * 100).round(2)
    
    print(f"✅ Loaded {len(df):,} transactions")
    print(f"✅ Date range: {df['sale_date'].min()} to {df['sale_date'].max()}")
    print(f"✅ Total revenue: ${df['total_sale'].sum():,.2f}")
    
    return df

df = load_data(conn)

# ============================================================
# 3. COMPREHENSIVE VISUALIZATIONS
# ============================================================

# Create output directory
import os
os.makedirs('visuals', exist_ok=True)

# -----------------
# Chart 1: Revenue by Category
# -----------------
plt.figure(figsize=(10, 6))
category_revenue = df.groupby('category')['total_sale'].sum().sort_values(ascending=False)
colors = sns.color_palette("viridis", len(category_revenue))

bars = plt.bar(category_revenue.index, category_revenue.values, color=colors, edgecolor='black', alpha=0.8)
plt.title('Total Revenue by Category', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Category', fontsize=12, fontweight='bold')
plt.ylabel('Revenue ($)', fontsize=12, fontweight='bold')
plt.xticks(rotation=0)

# Add value labels
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('visuals/1_revenue_by_category.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 2: Monthly Sales Trend
# -----------------
plt.figure(figsize=(12, 6))
monthly_sales = df.groupby('month_num')['total_sale'].sum()
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

plt.plot(monthly_sales.index, monthly_sales.values, marker='o', linewidth=2.5, 
         markersize=8, color='#2E86AB', markerfacecolor='#A23B72')
plt.fill_between(monthly_sales.index, monthly_sales.values, alpha=0.3, color='#2E86AB')
plt.title('Monthly Sales Trend', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Month', fontsize=12, fontweight='bold')
plt.ylabel('Total Sales ($)', fontsize=12, fontweight='bold')
plt.xticks(monthly_sales.index, [months[i-1] for i in monthly_sales.index], rotation=45)
plt.grid(True, alpha=0.3, linestyle='--')

# Highlight max and min
max_month = monthly_sales.idxmax()
min_month = monthly_sales.idxmin()
plt.scatter([max_month], [monthly_sales[max_month]], color='green', s=200, zorder=5, label='Highest')
plt.scatter([min_month], [monthly_sales[min_month]], color='red', s=200, zorder=5, label='Lowest')
plt.legend()

plt.tight_layout()
plt.savefig('visuals/2_monthly_sales_trend.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 3: Sales by Day of Week
# -----------------
plt.figure(figsize=(10, 6))
day_sales = df.groupby(['day_num', 'day_of_week'])['total_sale'].sum().reset_index()
day_sales = day_sales.sort_values('day_num')

bars = plt.bar(day_sales['day_of_week'], day_sales['total_sale'], 
               color=sns.color_palette("coolwarm", 7), edgecolor='black', alpha=0.8)
plt.title('Sales by Day of Week', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Day', fontsize=12, fontweight='bold')
plt.ylabel('Total Sales ($)', fontsize=12, fontweight='bold')
plt.xticks(rotation=45)

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'${height:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('visuals/3_sales_by_day.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 4: Peak Sales Hours Heatmap
# -----------------
plt.figure(figsize=(12, 6))
hourly_sales = df.groupby(['day_of_week', 'hour'])['total_sale'].sum().unstack(fill_value=0)
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
hourly_sales = hourly_sales.reindex(day_order)

sns.heatmap(hourly_sales, cmap='YlOrRd', annot=False, fmt='.0f', 
            linewidths=0.5, cbar_kws={'label': 'Revenue ($)'})
plt.title('Sales Heatmap: Day vs Hour', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Hour of Day', fontsize=12, fontweight='bold')
plt.ylabel('Day of Week', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('visuals/4_sales_heatmap.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 5: Age Group Spending
# -----------------
plt.figure(figsize=(10, 6))
age_spending = df.groupby('age_group')['total_sale'].sum().sort_values(ascending=False)

bars = plt.barh(age_spending.index, age_spending.values, 
                color=sns.color_palette("mako", len(age_spending)), 
                edgecolor='black', alpha=0.8)
plt.title('Total Spending by Age Group', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Total Sales ($)', fontsize=12, fontweight='bold')
plt.ylabel('Age Group', fontsize=12, fontweight='bold')

for bar in bars:
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f'${width:,.0f}', ha='left', va='center', fontweight='bold', fontsize=10)

plt.tight_layout()
plt.savefig('visuals/5_age_group_spending.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 6: Profit Margin by Category
# -----------------
plt.figure(figsize=(10, 6))
profit_analysis = df.groupby('category').agg({
    'total_sale': 'sum',
    'profit': 'sum'
}).reset_index()
profit_analysis['profit_margin_pct'] = (profit_analysis['profit'] / profit_analysis['total_sale'] * 100).round(2)

bars = plt.bar(profit_analysis['category'], profit_analysis['profit_margin_pct'],
               color=['#27AE60', '#E67E22', '#3498DB'], edgecolor='black', alpha=0.8)
plt.title('Profit Margin by Category', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Category', fontsize=12, fontweight='bold')
plt.ylabel('Profit Margin (%)', fontsize=12, fontweight='bold')
plt.axhline(y=profit_analysis['profit_margin_pct'].mean(), color='red', 
            linestyle='--', linewidth=2, label=f"Avg: {profit_analysis['profit_margin_pct'].mean():.1f}%")
plt.legend()

for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('visuals/6_profit_margin.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 7: Gender Distribution & Spending
# -----------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Gender transaction count
gender_counts = df['gender'].value_counts()
ax1.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
        colors=['#FF6B9D', '#4ECDC4'], startangle=90, textprops={'fontweight': 'bold'})
ax1.set_title('Transaction Distribution by Gender', fontsize=14, fontweight='bold', pad=20)

# Gender revenue
gender_revenue = df.groupby('gender')['total_sale'].sum()
bars = ax2.bar(gender_revenue.index, gender_revenue.values, 
               color=['#FF6B9D', '#4ECDC4'], edgecolor='black', alpha=0.8)
ax2.set_title('Total Revenue by Gender', fontsize=14, fontweight='bold', pad=20)
ax2.set_ylabel('Revenue ($)', fontweight='bold')
ax2.set_xlabel('Gender', fontweight='bold')

for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'${height:,.0f}', ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('visuals/7_gender_analysis.png', bbox_inches='tight')
plt.close()

# -----------------
# Chart 8: Top 10 Customers
# -----------------
plt.figure(figsize=(10, 7))
top_customers = df.groupby('customer_id')['total_sale'].sum().nlargest(10).sort_values()

bars = plt.barh(range(len(top_customers)), top_customers.values,
                color=sns.color_palette("rocket", len(top_customers)), 
                edgecolor='black', alpha=0.8)
plt.yticks(range(len(top_customers)), [f'Customer {id}' for id in top_customers.index])
plt.title('Top 10 Customers by Total Spend', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Total Spend ($)', fontsize=12, fontweight='bold')
plt.ylabel('Customer ID', fontsize=12, fontweight='bold')

for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f'${width:,.0f}', ha='left', va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig('visuals/8_top_customers.png', bbox_inches='tight')
plt.close()

# ============================================================
# 4. SUMMARY STATISTICS
# ============================================================
print("\n" + "="*60)
print("📊 SALES ANALYTICS SUMMARY")
print("="*60)
print(f"Total Transactions: {len(df):,}")
print(f"Unique Customers: {df['customer_id'].nunique():,}")
print(f"Total Revenue: ${df['total_sale'].sum():,.2f}")
print(f"Total Profit: ${df['profit'].sum():,.2f}")
print(f"Average Transaction: ${df['total_sale'].mean():,.2f}")
print(f"Average Profit Margin: {df['profit_margin'].mean():.2f}%")
print("\nTop Category:", df.groupby('category')['total_sale'].sum().idxmax())
print("Best Day:", df.groupby('day_of_week')['total_sale'].sum().idxmax())
print("Peak Hour:", df.groupby('hour')['total_sale'].sum().idxmax())
print("="*60)
print("\n✅ All 8 charts saved to 'visuals/' folder!")

# Close connection
conn.close()
print("✅ Database connection closed.")