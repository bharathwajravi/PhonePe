import streamlit as st
import plotly.graph_objects as go
import mysql.connector
import pandas as pd

# Set the title of the Streamlit app
st.title("Live Geo Visualization Dashboard")

# MySQL database connection details
db_config = {
    'user': 'root',
    'password': 'charan',
    'host': 'localhost',
    'database': 'phonepe'
}

# Function to fetch data from MySQL
def fetch_data(query, params=None):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return result, columns
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None, None
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

# Dropdown for selecting state
query_states = "SELECT DISTINCT State FROM agg_trans"
states_result, _ = fetch_data(query_states)
if states_result:
    states = [row[0] for row in states_result]
    states.sort()

    selected_state = st.sidebar.selectbox('Select State', states)

    # Fetch and display data for the selected state
    query = """
    SELECT State, Year, SUM(Transaction_count) as Transaction_count, SUM(Transaction_amount) as Transaction_amount
    FROM agg_trans
    WHERE State = %s
    GROUP BY State, Year
    """
    state_result, columns = fetch_data(query, (selected_state,))
    if state_result:
        transaction_data = pd.DataFrame(state_result, columns=columns)
        
        if not transaction_data.empty:
            st.header(f'Transaction Details for {selected_state}')
            st.subheader('States Data Table')
            st.write(transaction_data[['Year', 'Transaction_count', 'Transaction_amount']])
            
            # Pie chart for Transaction Count
            fig_trans_count = go.Figure(go.Pie(
                labels=transaction_data['Year'],
                values=transaction_data['Transaction_count'],
                hole=0.3
            ))
            fig_trans_count.update_layout(
                title=f'Transaction Count Distribution for {selected_state}'
            )
            st.plotly_chart(fig_trans_count)
            
            # Pie chart for Transaction Amount
            fig_trans_amount = go.Figure(go.Pie(
                labels=transaction_data['Year'],
                values=transaction_data['Transaction_amount'],
                hole=0.3
            ))
            fig_trans_amount.update_layout(
                title=f'Transaction Amount Distribution for {selected_state}'
            )
            st.plotly_chart(fig_trans_amount)
        else:
            st.write("No data available for the selected state.")

# Dropdown for selecting data analysis option
options = {
    "Transaction Type Breakdown": 1,
    "User Metrics": 2,
    "Geographical Analysis": 3,
    "Quarterly Performance": 4,
    "Top Performing States": 5,
    "Yearly Trends": 6,
    "Overall Summary": 7
}

selected_option = st.sidebar.selectbox("Data Analysis", list(options.keys()))

# Show result based on selected option
if selected_option:
    selected_option_index = options[selected_option]

    # Define queries for each option
    queries = {
        1: """
        SELECT Transaction_type, 
               SUM(Transaction_count) AS Total_Transactions, 
               SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        GROUP BY Transaction_type;
        """,
        2: """
        SELECT State, Year, Quarter, RegisteredUsers, AppOpens
        FROM agg_user;
        """,
        3: """
        SELECT State, SUM(Transaction_count) AS Total_Transactions, SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        GROUP BY State;
        """,
        4: """
        SELECT State, Year, Quarter, SUM(Transaction_count) as Total_Transactions, SUM(Transaction_amount) as Total_Amount
        FROM agg_trans
        WHERE Quarter = %s
        GROUP BY State, Year, Quarter;
        """,
        5: """
        SELECT State, SUM(Transaction_count) AS Total_Transactions, SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        GROUP BY State
        ORDER BY Total_Transactions DESC
        LIMIT 10;
        """,
        6: """
        SELECT State, Year, SUM(Transaction_count) as Total_Transactions, SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        WHERE Year = %s
        GROUP BY State, Year;
        """,
        7: """
        SELECT State, Year, 
               SUM(Transaction_count) AS Total_Transactions, 
               SUM(Transaction_amount) AS Total_Amount,
               SUM(RegisteredUsers) AS Total_Registered_Users,
               SUM(AppOpens) AS Total_App_Opens
        FROM agg_trans
        JOIN agg_user USING(State, Year)
        GROUP BY State, Year
        ORDER BY Total_Transactions DESC
        LIMIT 10;
        """
    }

    if selected_option_index in queries:
        query = queries[selected_option_index]
        
        # Handling options requiring additional parameters
        params = None
        if selected_option_index == 4:  # Quarter selection
            selected_quarter = st.sidebar.selectbox("Select a quarter", [1, 2, 3, 4], index=0)
            params = (selected_quarter,)
        elif selected_option_index == 6:  # Year selection
            selected_year = st.sidebar.selectbox("Select a year", [2018, 2019, 2020, 2021], index=0)
            params = (selected_year,)

        result, columns = fetch_data(query, params)
        if result:
            df = pd.DataFrame(result, columns=columns)
            
            # Show data table
            st.write(df)
            
            # Pie charts for each option
            if selected_option_index == 1:  # Transaction Type Breakdown
                fig_trans_type_count = go.Figure(go.Pie(
                    labels=df['Transaction_type'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_trans_type_count.update_layout(
                    title='Transaction Type Count Distribution'
                )
                st.plotly_chart(fig_trans_type_count)

                fig_trans_type_amount = go.Figure(go.Pie(
                    labels=df['Transaction_type'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_trans_type_amount.update_layout(
                    title='Transaction Type Amount Distribution'
                )
                st.plotly_chart(fig_trans_type_amount)

            elif selected_option_index == 2:  # User Metrics
                fig_user_reg = go.Figure(go.Pie(
                    labels=df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str),
                    values=df['RegisteredUsers'],
                    hole=0.3
                ))
                fig_user_reg.update_layout(
                    title='Registered Users Over Time'
                )
                st.plotly_chart(fig_user_reg)

                fig_user_opens = go.Figure(go.Pie(
                    labels=df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str),
                    values=df['AppOpens'],
                    hole=0.3
                ))
                fig_user_opens.update_layout(
                    title='App Opens Over Time'
                )
                st.plotly_chart(fig_user_opens)

            elif selected_option_index == 3:  # Geographical Analysis (Pie Charts)
                fig_geo_trans_count = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_geo_trans_count.update_layout(
                    title='Geographical Transaction Count Distribution'
                )
                st.plotly_chart(fig_geo_trans_count)

                fig_geo_trans_amount = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_geo_trans_amount.update_layout(
                    title='Geographical Transaction Amount Distribution'
                )
                st.plotly_chart(fig_geo_trans_amount)

            elif selected_option_index == 4:  # Quarterly Performance
                fig_quarterly_trans_count = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_quarterly_trans_count.update_layout(
                    title=f'Transaction Count Distribution for Q{selected_quarter}'
                )
                st.plotly_chart(fig_quarterly_trans_count)

                fig_quarterly_trans_amount = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_quarterly_trans_amount.update_layout(
                    title=f'Transaction Amount Distribution for Q{selected_quarter}'
                )
                st.plotly_chart(fig_quarterly_trans_amount)

            elif selected_option_index == 5:  # Top Performing States
                fig_top_states_count = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_top_states_count.update_layout(
                    title='Top States by Transaction Count'
                )
                st.plotly_chart(fig_top_states_count)

                fig_top_states_amount = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_top_states_amount.update_layout(
                    title='Top States by Transaction Amount'
                )
                st.plotly_chart(fig_top_states_amount)

            elif selected_option_index == 6:  # Yearly Trends
                fig_yearly_trans_count = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_yearly_trans_count.update_layout(
                    title=f'Transaction Count Distribution for {selected_year}'
                )
                st.plotly_chart(fig_yearly_trans_count)

                fig_yearly_trans_amount = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_yearly_trans_amount.update_layout(
                    title=f'Transaction Amount Distribution for {selected_year}'
                )
                st.plotly_chart(fig_yearly_trans_amount)

            elif selected_option_index == 7:  # Overall Summary
                st.write("Overall Summary of Total Metrics")

                # Pie chart for Total Transactions
                fig_total_trans = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Transactions'],
                    hole=0.3
                ))
                fig_total_trans.update_layout(
                    title='Total Transactions Distribution'
                )
                st.plotly_chart(fig_total_trans)

                # Pie chart for Total Amount
                fig_total_amount = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Amount'],
                    hole=0.3
                ))
                fig_total_amount.update_layout(
                    title='Total Amount Distribution'
                )
                st.plotly_chart(fig_total_amount)

                # Pie chart for Total Registered Users
                fig_total_users = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_Registered_Users'],
                    hole=0.3
                ))
                fig_total_users.update_layout(
                    title='Total Registered Users Distribution'
                )
                st.plotly_chart(fig_total_users)

                # Pie chart for Total App Opens
                fig_total_opens = go.Figure(go.Pie(
                    labels=df['State'],
                    values=df['Total_App_Opens'],
                    hole=0.3
                ))
                fig_total_opens.update_layout(
                    title='Total App Opens Distribution'
                )
                st.plotly_chart(fig_total_opens)

        else:
            st.write("No data available for the selected option.")
