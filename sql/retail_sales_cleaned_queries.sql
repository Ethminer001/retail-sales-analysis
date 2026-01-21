-- ============================================================
-- RETAIL SALES ANALYSIS - CLEANED QUERIES
-- Database: MINI_SALES_PROJECT
-- ============================================================

-- Database Setup
CREATE DATABASE IF NOT EXISTS MINI_SALES_PROJECT;
USE MINI_SALES_PROJECT;

-- ============================================================
-- TABLE STRUCTURE CORRECTIONS
-- ============================================================

-- Standardize data types
ALTER TABLE retail_sales
MODIFY COLUMN transactions_id INT,
MODIFY COLUMN sale_date DATE,
MODIFY COLUMN sale_time TIME,
MODIFY COLUMN customer_id INT,
MODIFY COLUMN gender VARCHAR(10),
MODIFY COLUMN age INT,
MODIFY COLUMN category VARCHAR(50),
MODIFY COLUMN quantity INT,
MODIFY COLUMN price_per_unit DECIMAL(10,2),
MODIFY COLUMN cogs DECIMAL(10,2),
MODIFY COLUMN total_sale DECIMAL(10,2);

-- Verify structure
DESCRIBE retail_sales;
SELECT * FROM retail_sales LIMIT 10;

-- ============================================================
-- 1. REVENUE ANALYSIS
-- ============================================================

SELECT SUM(total_sale) AS total_revenue,
       COUNT(*) AS total_transactions,
       ROUND(AVG(total_sale), 2) AS avg_transaction_value
FROM retail_sales;

SELECT category,
       SUM(total_sale) AS total_revenue,
       COUNT(*) AS transaction_count,
       ROUND(AVG(total_sale), 2) AS avg_sale_per_transaction
FROM retail_sales
GROUP BY category
ORDER BY total_revenue DESC;

SELECT category,
       SUM(total_sale) AS total_revenue
FROM retail_sales
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 1;

SELECT ROUND(AVG(total_sale), 2) AS avg_sale_per_transaction
FROM retail_sales;

-- ============================================================
-- 2. TEMPORAL ANALYSIS
-- ============================================================

SELECT MONTHNAME(sale_date) AS month_name,
       MONTH(sale_date) AS month_number,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count
FROM retail_sales
GROUP BY month_name, month_number
ORDER BY month_number;

SELECT MONTHNAME(sale_date) AS month_name,
       SUM(total_sale) AS total_sales
FROM retail_sales
GROUP BY month_name
ORDER BY total_sales DESC
LIMIT 1;

SELECT MONTHNAME(sale_date) AS month_name,
       SUM(total_sale) AS total_sales
FROM retail_sales
GROUP BY month_name
ORDER BY total_sales ASC
LIMIT 1;

SELECT DAYNAME(sale_date) AS day_of_week,
       DAYOFWEEK(sale_date) AS day_number,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count
FROM retail_sales
GROUP BY day_of_week, day_number
ORDER BY day_number;

SELECT HOUR(sale_time) AS hour_of_day,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count
FROM retail_sales
GROUP BY hour_of_day
ORDER BY total_sales DESC;

-- ============================================================
-- 3. CUSTOMER ANALYSIS
-- ============================================================

SELECT CASE
           WHEN age BETWEEN 18 AND 25 THEN '18-25'
           WHEN age BETWEEN 26 AND 35 THEN '26-35'
           WHEN age BETWEEN 36 AND 45 THEN '36-45'
           WHEN age BETWEEN 46 AND 55 THEN '46-55'
           WHEN age BETWEEN 56 AND 65 THEN '56-65'
           ELSE '65+'
       END AS age_group,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count,
       ROUND(AVG(total_sale), 2) AS avg_transaction_value
FROM retail_sales
GROUP BY age_group
ORDER BY total_sales DESC;

SELECT age,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count
FROM retail_sales
GROUP BY age
ORDER BY total_sales DESC
LIMIT 1;

SELECT customer_id,
       SUM(total_sale) AS total_spend,
       COUNT(*) AS purchase_frequency,
       ROUND(AVG(total_sale), 2) AS avg_purchase_value
FROM retail_sales
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 10;

SELECT customer_id,
       ROUND(AVG(quantity), 2) AS avg_quantity_purchased,
       SUM(quantity) AS total_quantity,
       COUNT(*) AS transaction_count
FROM retail_sales
GROUP BY customer_id
ORDER BY avg_quantity_purchased DESC
LIMIT 20;

SELECT gender,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count,
       ROUND(AVG(total_sale), 2) AS avg_transaction_value
FROM retail_sales
GROUP BY gender
ORDER BY total_sales DESC;

-- ============================================================
-- 4. PRODUCT & PROFITABILITY ANALYSIS
-- ============================================================

SELECT category,
       SUM(total_sale - cogs) AS total_profit,
       SUM(total_sale) AS total_revenue,
       SUM(cogs) AS total_cost,
       ROUND((SUM(total_sale - cogs) / SUM(total_sale)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY category
ORDER BY total_profit DESC;

SELECT category,
       SUM(total_sale - cogs) AS total_profit,
       ROUND((SUM(total_sale - cogs) / SUM(total_sale)) * 100, 2) AS profit_margin_pct
FROM retail_sales
GROUP BY category
ORDER BY total_profit DESC
LIMIT 1;

SELECT category,
       ROUND(AVG(price_per_unit), 2) AS avg_price_per_unit,
       MIN(price_per_unit) AS min_price,
       MAX(price_per_unit) AS max_price
FROM retail_sales
GROUP BY category
ORDER BY avg_price_per_unit DESC;

-- ============================================================
-- 5. STRATEGIC INSIGHTS
-- ============================================================

SELECT category,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count,
       ROUND((SUM(total_sale) / (SELECT SUM(total_sale) FROM retail_sales)) * 100, 2) AS revenue_share_pct
FROM retail_sales
GROUP BY category
ORDER BY total_sales ASC
LIMIT 1;

SELECT CASE
           WHEN age BETWEEN 18 AND 25 THEN '18-25 (Young)'
           WHEN age >= 40 THEN '40+ (Older)'
           ELSE 'Other'
       END AS target_segment,
       SUM(total_sale) AS total_sales,
       COUNT(*) AS transaction_count,
       ROUND(AVG(total_sale), 2) AS avg_transaction_value
FROM retail_sales
WHERE age BETWEEN 18 AND 25 OR age >= 40
GROUP BY target_segment
ORDER BY total_sales DESC;

-- ============================================================
-- 6. EXECUTIVE SUMMARY
-- ============================================================

SELECT COUNT(*) AS total_transactions,
       COUNT(DISTINCT customer_id) AS unique_customers,
       SUM(total_sale) AS total_revenue,
       SUM(cogs) AS total_costs,
       SUM(total_sale - cogs) AS total_profit,
       ROUND(AVG(total_sale), 2) AS avg_transaction_value,
       ROUND((SUM(total_sale - cogs) / SUM(total_sale)) * 100, 2) AS overall_profit_margin_pct
FROM retail_sales;
