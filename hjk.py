# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 21:32:00 2023

@author: magnn
"""

# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

# Load the dataset from an Excel file
data = pd.read_excel('C:/Users/magnn/dataset.xlsx')

# Create a copy of the dataset for analysis
df = data.copy()

# Display the shape of the dataset (number of rows and columns)
data_shape = df.shape
print("Data shape: ", data_shape)

# Display the data types of variables
variable_types = df.dtypes
print("Variable types:\n", variable_types)

# Count and visualize the distribution of variable types
variable_type_counts = variable_types.value_counts()
variable_type_counts.plot.pie()
plt.title("Distribution of Variable Types")
plt.show()

# Initial analysis of missing values
print(df.head())

# Check for missing values in the dataset
is_missing = df.isna()
print("Missing values:\n", is_missing)

# Visualize missing values as a heatmap using Seaborn
plt.figure(figsize=(12, 8))
sns.heatmap(is_missing, cbar=False)
plt.title("Missing Values Heatmap")
plt.show()

# Calculate and sort missing value percentages for each variable
missing_value_counts = df.isna().sum()
missing_value_percentages = (missing_value_counts / df.shape[0]).sort_values(ascending=True)
print("Missing Value Percentages:\n", missing_value_percentages)

# Data Analysis Results:
# - Target Variable: SARS-Cov-2 Exam Result
# - Number of Rows and Columns: 5644 rows, 111 columns
# - Variable Types: Numeric Variables: 70, Non-Numeric Variables: 41
# - Many variables have NaN values, with some having more than 90% missing data.

# Part 2: Deep Analysis
# 1. Initial Visualization: Select Useful Columns and Eliminate 'Patient ID'
# Select variables with less than 90% missing values
selected_variables = df.isna().sum() / df.shape[0] < 0.9

# Filter the dataset to include only selected variables
useful_data = df[df.columns[selected_variables]]

# Remove the 'Patient ID' column as it's not useful for analysis
useful_data = useful_data.drop('Patient ID', axis=1)

# Visualize missing values for the useful data
plt.figure(figsize=(12, 8))
sns.heatmap(useful_data.isna(), cbar=False)
plt.title("Missing Values Heatmap for Useful Data")
plt.show()

# 2. Analyze the 'Patient age quantile' variable
plt.figure()
sns.distplot(useful_data['Patient age quantile'], bins=20)
plt.title("Distribution of Patient Age Quantile")

# 3. Analyze Non-Numeric Variables
for column in useful_data.select_dtypes('object'):
    unique_values = useful_data[column].unique()
    print(f"{column} unique values: {unique_values}")

# Count the number of unique values in each non-numeric variable
for column in useful_data.select_dtypes('object'):
    print(f"{column}:")
    print(useful_data[column].value_counts())
    # Optionally, you can visualize this data using pie charts

# Part 3: Analyze Relationships Between Target and Variables
# Create subsets for positive and negative COVID-19 cases
positive_cases = useful_data[useful_data['SARS-Cov-2 exam result'] == 'positive']
negative_cases = useful_data[useful_data['SARS-Cov-2 exam result'] == 'negative']

# Further analysis, visualizations, and statistical tests can be performed here
# For example, visualizing the distribution of specific variables for positive and negative cases.

# Correlation analysis can be performed on numeric variables, and additional visualizations can be created.

# Part 3: Analyze Relationships Between Target and Variables (Continued)
# Create subsets for blood and viral variables based on missing value rates
missing_rates = useful_data.isna().sum() / useful_data.shape[0]
blood_columns = useful_data.columns[(missing_rates < 0.9) & (missing_rates > 0.88)]
viral_columns = useful_data.columns[(missing_rates < 0.88) & (missing_rates > 0.75)]

# Visualize the distribution of variables for positive and negative cases
for column in blood_columns:
    plt.figure()
    sns.distplot(positive_cases[column], label='positive')
    sns.distplot(negative_cases[column], label='negative')
    plt.legend()
    plt.title(f"Distribution of {column} for Positive and Negative Cases")

# Create a count plot to analyze the distribution of 'Patient age quantile' by COVID-19 result
sns.countplot(x='Patient age quantile', hue='SARS-Cov-2 exam result', data=useful_data)
plt.title("Distribution of Patient Age Quantile by COVID-19 Result")

# Analyze the relationship between the target and viral variables
for column in viral_columns:
    cross_tab = pd.crosstab(useful_data['SARS-Cov-2 exam result'], useful_data[column])
    print(f"Cross-tabulation for {column}:\n{cross_tab}")

# Deep Details Analysis
# Uncomment the following lines to perform additional analysis if needed
# For example, pair plots for continuous variables, correlation matrix, and more visualizations

# sns.pairplot(useful_data[blood_columns])
# plt.figure()
# sns.heatmap(useful_data[blood_columns].corr())
# plt.figure()
# sns.clustermap(useful_data[blood_columns].corr())

# Show all plots and visualizations
plt.show()
