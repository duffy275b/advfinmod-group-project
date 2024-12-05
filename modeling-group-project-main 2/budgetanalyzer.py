import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import plotly.express as px
import locale
from babel.numbers import format_currency

# App Title
st.title("Smart Finance Planner")
st.subheader("Your Budget, Savings, and Investment Companion")

# Sidebar for navigation
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select a section:", 
    ["Home", "Income Input", "Expense Input", "Spending Analysis", "Savings Prediction", "Investment Planning"]
)

# Home Section
if menu == "Home":
    st.header("Welcome to the Personal Finance Tool")
    st.write("""
        This tool helps you:
        - Analyze your monthly expenses
        - Predict future savings
        - Plan your investments
    """)
    st.image("/Users/michaelduffy/Downloads/savings.png", caption="Manage your finances effectively.")  # Replace with your image path.

# Monthly Income Input Section
elif menu == "Income Input":
    st.header("Enter Your Monthly Income")

    # Input for monthly income
    monthly_income = st.number_input(
        "Enter your total monthly income ($):", 
        min_value=0.0, 
        step=100.0
    )
    
    if st.button("Save Income"):
        # Save the income to a CSV file (overwriting previous values)
        income_df = pd.DataFrame({"Monthly Income": [monthly_income]})
        income_df.to_csv("income.csv", index=False)
        st.success("Monthly income saved successfully!")

    # Display Total Saved Income
    try:
        # Load existing income from CSV
        saved_income_df = pd.read_csv("income.csv")
        total_income_saved = saved_income_df["Monthly Income"].iloc[0]  # There will be only one value
        st.write(f"### Saved Monthly Income: ${total_income_saved:.2f}")
    except FileNotFoundError:
        # If no file exists yet, show a default message
        st.write("### Saved Monthly Income: $0.00")


# Expense Input Section
elif menu == "Expense Input":
    st.header("Enter Your Monthly Expenses")
    
    # Define expense categories
    categories = ["Rent", "Utilities", "Groceries", "Transportation", "Entertainment", "Others"]
    
    # Initialize expenses dictionary
    expenses = {category: st.number_input(f"Enter your expense for {category} ($):", min_value=0.0, step=10.0) for category in categories}

    # Save expenses to CSV (overwriting previous values)
    if st.button("Save Expenses"):
        # Convert input to a DataFrame
        expenses_df = pd.DataFrame([expenses])
        
        # Save the current expenses, overwriting any existing file
        expenses_df.to_csv("expenses.csv", index=False)
        st.success("Expenses saved!")

    # Display Total and Individual Category Totals
    try:
        # Load existing expenses from CSV
        saved_expenses_df = pd.read_csv("expenses.csv")

        # Calculate total saved expenses
        total_expenses_saved = saved_expenses_df.sum().sum()

        # Display total expenses
        st.write(f"### Total Saved Expenses: ${total_expenses_saved:.2f}")

    except FileNotFoundError:
        # If no file exists yet, show a default message
        st.write("### Total Saved Expenses: $0.00")
        st.write("No expenses saved yet.")



# Spending Analysis Section
elif menu == "Spending Analysis":
    st.header("Spending Analysis")

    # Load data
    try:
        expenses_df = pd.read_csv("expenses.csv")
        total_expenses = expenses_df.sum().sum()

        try:
            # Load existing income from CSV
            saved_income_df = pd.read_csv("income.csv")
            monthly_income = saved_income_df["Monthly Income"].iloc[0]
            savings_potential = monthly_income - total_expenses
        except FileNotFoundError:
            st.warning("Monthly income not provided. Please input it in the 'Income Input' section.")
            savings_potential = None

        # Format currency for the table
        def format_as_currency(value, currency="USD"):
            return format_currency(value, currency, locale='en_US')

        # Format expense data for display
        formatted_expenses_df = expenses_df.applymap(lambda x: format_as_currency(x, "USD"))

        # Summarize expenses by category
        expense_totals = expenses_df.sum().reset_index()
        expense_totals.columns = ["Category", "Amount"]

        # Create Pie Chart
        fig = px.pie(
            expense_totals,
            values="Amount",
            names="Category",
            title="Monthly Expenses Breakdown",
            color_discrete_sequence=px.colors.sequential.RdBu,
            hole=0.3
        )
        fig.update_traces(textinfo="percent+label", textfont_size=12)
        fig.update_layout(
            margin=dict(t=20, b=20, l=0, r=0),
            title_x=0.5,
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
            height=350,  # Reduce chart height
        )

        # Display Pie Chart
        st.plotly_chart(fig, use_container_width=True)

        # Add Spacing
        st.markdown("---")  # Divider for better separation

        # Display Summary Section
        st.write(f"### Total Expenses: {format_as_currency(total_expenses, 'USD')}")
        if savings_potential is not None:
            st.write(f"### Savings Potential: {format_as_currency(savings_potential, 'USD')}")

        # Add Spacing
        st.markdown("---")  # Divider for better separation

        # Display Expense Table Below
        st.subheader("Your Monthly Expenses")
        st.table(formatted_expenses_df)  # Display formatted table

    except FileNotFoundError:
        st.warning("No expense data found. Please input expenses first.")


# Savings Predictor Section
elif menu == "Savings Prediction":
    st.header("Predict Your Savings")

    # Step 1: Load Saved Income
    try:
        saved_income_df = pd.read_csv("income.csv")
        monthly_income = saved_income_df["Monthly Income"].iloc[0]
        st.write(f"### Using Saved Monthly Income: ${monthly_income:.2f}")
    except FileNotFoundError:
        st.warning("No income data available. Please enter your income in the 'Income Input' section.")
        monthly_income = None

    # Step 2: Input Fixed Expenses
    st.subheader("Enter Your Fixed Expenses (One-Time)")
    fixed_categories = ["Rent", "Utilities", "Insurance"]
    fixed_expenses = {category: st.number_input(f"{category} ($):", min_value=0.0, step=10.0) for category in fixed_categories}

    # Save fixed expenses
    if st.button("Save Fixed Expenses"):
        fixed_expenses_df = pd.DataFrame([fixed_expenses])
        fixed_expenses_df.to_csv("fixed_expenses.csv", index=False)
        st.success("Fixed expenses saved successfully!")

    # Step 3: Input Variable Expenses for the Past 3 Months
    st.subheader("Enter Your Variable Expenses for the Past 3 Months")
    variable_categories = ["Groceries", "Transportation", "Entertainment", "Others"]
    variable_data = {}

    for month in ["Month 1", "Month 2", "Month 3"]:
        st.write(f"### {month}")
        variable_data[month] = {category: st.number_input(f"{month} - {category} ($):", min_value=0.0, step=10.0) for category in variable_categories}

    # Save variable expenses and predict
    if st.button("Predict Savings"):
        # Ensure income is available
        if monthly_income is None:
            st.error("Income data is required to predict savings.")
        elif len(variable_data) == 3:
            # Calculate total fixed expenses
            try:
                fixed_expenses_df = pd.read_csv("fixed_expenses.csv")
                fixed_total = fixed_expenses_df.sum().sum()
            except FileNotFoundError:
                fixed_total = 0.0

            # Convert variable data to DataFrame
            variable_expenses_df = pd.DataFrame(variable_data).T  # Transpose for correct format
            variable_expenses_df["Total Variable"] = variable_expenses_df.sum(axis=1)

            # Calculate savings
            total_expenses = fixed_total + variable_expenses_df["Total Variable"]
            savings = monthly_income - total_expenses

            # Create DataFrame for visualization
            savings_df = pd.DataFrame({
                "Month": ["Month 1", "Month 2", "Month 3"],
                "Income": [monthly_income] * 3,
                "Total Expenses": total_expenses,
                "Savings": savings
            })

            # Display savings data
            st.write("### Historical Savings Data")
            st.table(savings_df)

            # Calculate and display predicted savings
            avg_savings = savings.mean()
            st.write(f"### Predicted Monthly Savings: ${avg_savings:.2f}")

            # Line Chart Visualization
            fig = px.line(
                savings_df,
                x="Month",
                y=["Income", "Total Expenses", "Savings"],
                title="Income, Expenses, and Savings Trends",
                labels={"value": "Amount ($)", "variable": "Category"}
            )
            fig.update_layout(legend_title_text="Category")
            st.plotly_chart(fig)
        else:
            st.warning("Please fill out all data for the past 3 months to predict savings.")

# Investment Planning Section
elif menu == "Investment Planning":
    st.header("Investment Planning")
    risk_tolerance = st.selectbox("Select your risk tolerance:", ["Low", "Medium", "High"])
    time_horizon = st.slider("Select your investment time horizon (years):", 1, 30, 5)
    initial_investment = st.number_input("Enter your initial investment amount ($):", min_value=0.0, value=10000.0)
    
    st.write(f"Based on your preferences, here are some suggestions:")
    if risk_tolerance == "Low":
        st.write("- Bonds, Treasury Notes")
    elif risk_tolerance == "Medium":
        st.write("- Balanced Mutual Funds, Index Funds")
    else:
        st.write("- Stocks, ETFs")
    
    # Option for inflation adjustment
    adjust_for_inflation = st.checkbox("Adjust for Inflation")
    
    if st.button("Simulate Investment Growth"):
        years = np.arange(1, time_horizon + 1)
    
        # Set expected return and volatility ranges based on risk tolerance
        if risk_tolerance == "Low":
            expected_return_range = (0.01, 0.05)
            volatility_range = (0.01, 0.05)
        elif risk_tolerance == "Medium":
            expected_return_range = (0.04, 0.08)
            volatility_range = (0.05, 0.10)
        else:
            expected_return_range = (0.06, 0.12)
            volatility_range = (0.10, 0.20)
        
        # Inflation rate
        inflation_rate = 0.02  # 2% inflation rate
        
        # Number of simulation runs
        num_simulations = 1000
        simulation_results = []
    
        for _ in range(num_simulations):
            # Randomly select expected return and volatility within the ranges
            expected_return = np.random.uniform(*expected_return_range)
            volatility = np.random.uniform(*volatility_range)
            
            # Adjust expected return for inflation if selected
            if adjust_for_inflation:
                expected_return -= inflation_rate
            
            # Generate annual returns
            annual_returns = np.random.normal(expected_return, volatility, time_horizon)
            cumulative_growth = initial_investment * np.cumprod(1 + annual_returns)
            simulation_results.append(cumulative_growth)
        
        # Convert to a NumPy array for easier manipulation
        simulation_results = np.array(simulation_results)
        
        # Calculate percentiles for confidence intervals
        percentiles = np.percentile(simulation_results, [5, 25, 50, 75, 95], axis=0)
        
        # Plotting
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, percentiles[2], label='Median Outcome')
        ax.fill_between(years, percentiles[0], percentiles[4], color='gray', alpha=0.2, label='5-95 Percentile')
        ax.fill_between(years, percentiles[1], percentiles[3], color='gray', alpha=0.4, label='25-75 Percentile')
        ax.set_title('Investment Growth Over Time')
        ax.set_xlabel('Year')
        ax.set_ylabel('Investment Value ($)')
        ax.legend()
        st.pyplot(fig)
        
        # Add Disclaimers
        st.markdown("""
        **Disclaimer:** This simulation is based on historical data and assumptions. Actual investment returns may vary significantly and are not guaranteed. This tool is for educational purposes and should not be considered financial advice. Please consult with a financial advisor before making investment decisions.
        """)

# Footer
st.sidebar.markdown("---")
st.sidebar.write("Project by Thomas Feely, Lucas Longfellow, Zach Cheney, Michael Duffy")
