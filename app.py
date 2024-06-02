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
def fetch_data(query):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            return result
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

# Fetching live data
query_states = """
SELECT DISTINCT State
FROM agg_trans
"""
states_result = fetch_data(query_states)
if states_result:
    # Extracting unique states from the fetched data
    states = [row[0] for row in states_result]
    states.sort()  # Sort the states alphabetically
    
    # Create a DataFrame for the fetched states
    states_df = pd.DataFrame(states, columns=['State'])
    
    # State coordinates data
    state_coordinates = {
        "Andhra Pradesh": [15.9129, 79.7400],
        "Arunachal Pradesh": [28.2180, 94.7278],
        "Assam": [26.2006, 92.9376],
        "Bihar": [25.0961, 85.3131],
        "Chhattisgarh": [21.2787, 81.8661],
        "Goa": [15.2993, 74.1240],
        "Gujarat": [22.2587, 71.1924],
        "Haryana": [29.0588, 76.0856],
        "Himachal Pradesh": [31.1048, 77.1734],
        "Jharkhand": [23.6102, 85.2799],
        "Karnataka": [15.3173, 75.7139],
        "Kerala": [10.8505, 76.2711],
        "Madhya Pradesh": [22.9734, 78.6569],
        "Maharashtra": [19.7515, 75.7139],
        "Manipur": [24.6637, 93.9063],
        "Meghalaya": [25.4670, 91.3662],
        "Mizoram": [23.1645, 92.9376],
        "Nagaland": [26.1584, 94.5624],
        "Odisha": [20.9517, 85.0985],
        "Punjab": [31.1471, 75.3410],
        "Rajasthan": [27.0238, 74.2179],
        "Sikkim": [27.5330, 88.5122],
        "Tamil Nadu": [11.1271, 78.6569],
        "Telangana": [18.1124, 79.0193],
        "Tripura": [23.9408, 91.9882],
        "Uttar Pradesh": [26.8467, 80.9462],
        "Uttarakhand": [30.0668, 79.0193],
        "West Bengal": [22.9868, 87.8550]
    }
    
    # Create the sidebar dropdown for selecting a state
    selected_state = st.sidebar.selectbox('Select State', states)
    
    # Fetching live data based on the selected state
    query = f"""
    SELECT State, Year, SUM(Transaction_count) as Transaction_count, SUM(Transaction_amount) as Transaction_amount
    FROM agg_trans
    WHERE State = '{selected_state}'
    GROUP BY State, Year
    """
    state_result = fetch_data(query)
    if state_result:
        # Create a DataFrame from the fetched data
        transaction_data = pd.DataFrame(state_result, columns=['State', 'Year', 'Transaction_count', 'Transaction_amount'])

        # Add coordinates to transaction data
        transaction_data['Latitude'] = state_coordinates[selected_state][0] if selected_state in state_coordinates else None
        transaction_data['Longitude'] = state_coordinates[selected_state][1] if selected_state in state_coordinates else None
        
        # Create the choropleth map using Plotly
        fig = go.Figure(go.Choroplethmapbox(
            geojson='https://raw.githubusercontent.com/open-numbers/ddf--gapminder--geo_entities/master/geo%20entities/country/IND.geojson',
            locations=transaction_data['State'],  # DataFrame's State column
            z=transaction_data['Transaction_count'],  # DataFrame's Transaction_count column
            colorscale='Viridis',
            zmin=transaction_data['Transaction_count'].min(),
            zmax=transaction_data['Transaction_count'].max(),
            marker_opacity=0.7,
            marker_line_width=0,
        ))

        # Configure layout settings for the map
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=3,
            mapbox_center={"lat": 20.5937, "lon": 78.9629},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            title='Live Transactions in Indian States',
            hovermode='closest',
        )

        # Add hover text with transaction details
        hover_text = [f"State: {state}<br>Year: {year}<br>Total Transactions: {count}<br>Total Transaction Amount: {amount}" for state, year, count, amount in zip(transaction_data['State'], transaction_data['Year'], transaction_data['Transaction_count'], transaction_data['Transaction_amount'])]
        fig.update_traces(hovertext=hover_text, hoverinfo="text")

        # Display the map in Streamlit
        st.plotly_chart(fig)

        # Display transaction data for the selected state
    if not transaction_data.empty:
        st.header(f'Transaction Details for {selected_state}')
    selected_state_data = transaction_data[transaction_data['State'] == selected_state]
    st.write(selected_state_data[['Year', 'Transaction_count', 'Transaction_amount']])
else:
        st.write("No data available for the selected state.")


# Dropdown options
options = {
    "Transaction Type Breakdown": 1,
    "User Metrics": 2,
    "Geographical Analysis": 3,
    "Quarterly Performance": 4,
    "Top Performing States": 5,
    "Comparison Across Entities": 6,
    "Yearly Trends": 7,
    "Top Transactions by Entity": 8,
    "Top Users by Category": 9,
    "Overall Summary": 10
}

# Dropdown widget
selected_option = st.sidebar.selectbox("Data Analysis", list(options.keys()))

# Show result based on selected option
if selected_option:
    selected_option_index = options[selected_option]

    # Display corresponding SQL query based on selected option index
    if selected_option_index == 1:
        st.write("SQL Query for Transaction Type Breakdown")
        # SQL query for Transaction Type Breakdown
        query = """
        SELECT Transaction_type, 
               SUM(Transaction_count) AS Total_Transactions, 
               SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        GROUP BY Transaction_type;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['Transaction Type', 'Total Transactions', 'Total Amount'])
        st.write(df)
       
    elif selected_option_index == 2:
        st.write("User Metrics")
        # SQL query for User Metrics
        query = """
        SELECT State, Year, Quarter, RegisteredUsers, AppOpens
        FROM agg_user;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'Year', 'Quarter', 'Registered Users', 'App Opens'])
        st.write(df)

    elif selected_option_index == 3:
        st.write("Geographical Analysis")
        # SQL query for Geographical Analysis
        query = """
        SELECT State, District, Year, Quarter, TransactionCount, TransactionAmount
        FROM map_trans;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'District', 'Year', 'Quarter', 'Transaction Count', 'Transaction Amount'])
        st.write(df)

    elif selected_option_index == 4:
        st.write("Quarterly Performance")
        # SQL query for Quarterly Performance
        selected_quarter = st.sidebar.selectbox("Select a quarter", [1, 2, 3, 4], index=0)
        query = f"""
        SELECT *
        FROM agg_trans
        WHERE Quarter = {selected_quarter};
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'Year', 'Quarter', 'Transaction Type', 'Transaction Count', 'Transaction Amount'])
        st.write(df)

    elif selected_option_index == 5:
        st.write("Top Performing States")
        # SQL query for Top Performing States
        query = """
        SELECT State, 
               SUM(Transaction_count) AS Total_Transactions, 
               SUM(Transaction_amount) AS Total_Amount
        FROM agg_trans
        GROUP BY State
        ORDER BY Total_Transactions DESC
        LIMIT 10;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'Total Transactions', 'Total Amount'])
        st.write(df)

    elif selected_option_index == 6:
        st.write("Comparison Across Entities")
        # SQL query for Comparison Across Entities
        selected_state = st.sidebar.selectbox("Select a state", ["State A", "State B", "State C"])
        query = f"""
        SELECT t.State, 
               t.Transaction_count AS Trans_Count, 
               t.Transaction_amount AS Trans_Amount,
               u.RegisteredUsers,
               u.AppOpens
        FROM agg_trans t
        JOIN agg_user u ON t.State = u.State
        WHERE t.Year = u.Year
          AND t.Quarter = u.Quarter
          AND t.State = '{selected_state}';
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'Transaction Count', 'Transaction Amount', 'Registered Users', 'App Opens'])
        st.write(df)

    elif selected_option_index == 7:
        st.write("Yearly Trends")
        # SQL query for Yearly Trends
        query = """
        SELECT 
            agg_trans.Year, 
            SUM(agg_trans.Transaction_count) AS Total_Transactions, 
            SUM(agg_trans.Transaction_amount) AS Total_Amount,
            SUM(agg_user.RegisteredUsers) AS Total_Users,
            SUM(agg_user.AppOpens) AS Total_App_Opens
        FROM 
            agg_trans
        JOIN 
            agg_user 
        ON 
            agg_trans.Year = agg_user.Year
        GROUP BY 
            agg_trans.Year;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['Year', 'Total Transactions', 'Total Amount', 'Total Users', 'Total App Opens'])
        st.write(df)

    elif selected_option_index == 8:
        st.write("Top Transactions by Entity")
        # SQL query for Top Transactions by Entity
        selected_entity = st.sidebar.text_input("Enter an entity", "Entity A")
        query = f"""
        SELECT State, 
               Transaction_type, 
               Year, 
               Quarter, 
               Transaction_count AS Total_Transactions, 
               Transaction_amount AS Total_Amount
        FROM top_trans
        WHERE Entity = '{selected_entity}'
        ORDER BY Total_Transactions DESC
        LIMIT 10;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['State', 'Transaction Type', 'Year', 'Quarter', 'Total Transactions', 'Total Amount'])
        st.write(df)

    elif selected_option_index == 9:
        st.write("Top Users by Category")
        # SQL query for Top Users by Category
        selected_category = st.sidebar.text_input("Enter a category", "Category A")
        query = f"""
        SELECT Name, 
               Year, 
               Quarter, 
               RegisteredUsers AS Total_Users
        FROM top_user
        WHERE Category = '{selected_category}'
        ORDER BY Total_Users DESC
        LIMIT 10;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['Name', 'Year', 'Quarter', 'Total Users'])
        st.write(df)

    elif selected_option_index == 10:
        st.write("Overall Summary")
        # SQL query for Overall Summary
        query = """
        SELECT 'Transaction Type Breakdown' AS Option, COUNT(*) AS Value
        FROM agg_trans
        UNION ALL
        SELECT 'User Metrics' AS Option, COUNT(*)
        FROM agg_user
        UNION ALL
        SELECT 'Geographical Analysis', COUNT(*)
        FROM map_trans
        UNION ALL
        SELECT 'Quarterly Performance', COUNT(*)
        FROM agg_trans
        UNION ALL
        SELECT 'Top Performing States', COUNT(*)
        FROM agg_trans
        UNION ALL
        SELECT 'Comparison Across Entities', COUNT(*)
        FROM agg_trans
        UNION ALL
        SELECT 'Yearly Trends', COUNT(*)
        FROM agg_trans
        UNION ALL
        SELECT 'Top Transactions by Entity', COUNT(*)
        FROM top_trans
        UNION ALL
        SELECT 'Top Users by Category', COUNT(*)
        FROM top_user;
        """
        # Execute the query and fetch results
        result = fetch_data(query)
        # Convert result to DataFrame for better display
        df = pd.DataFrame(result, columns=['Option', 'Count'])
        st.write(df)
