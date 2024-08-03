import streamlit as st
import plotly.graph_objects as go
import mysql.connector
import pandas as pd
import json

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

# Load the JSON file for coordinates
json_path = "G:\\Data Science Projects\\PhonePe\\Clone\\pulse\\data\\map\\insurance\\country\\india\\2020\\2.json"
try:
    with open(json_path, 'r') as f:
        geojson_data = json.load(f)
except FileNotFoundError:
    st.error(f"File not found: {json_path}")
    geojson_data = {}

# Extract state coordinates from the JSON data
state_coordinates = {item[3]: [item[0], item[1]] for item in geojson_data if len(item) >= 4}

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
        
        # Add coordinates to the DataFrame
        if selected_state in state_coordinates:
            transaction_data['Latitude'], transaction_data['Longitude'] = state_coordinates[selected_state]
        else:
            transaction_data['Latitude'] = None
            transaction_data['Longitude'] = None
        
        # Create the choropleth map using Plotly
        fig = go.Figure()

        # Add Choroplethmapbox
        fig.add_trace(go.Choroplethmapbox(
            geojson=geojson_data,
            locations=transaction_data['State'],
            featureidkey="properties.state",  # Adjust this based on your geojson properties
            z=transaction_data['Transaction_count'],
            colorscale='Viridis',
            zmin=transaction_data['Transaction_count'].min() if not transaction_data.empty else 0,
            zmax=transaction_data['Transaction_count'].max() if not transaction_data.empty else 0,
            marker_opacity=0.7,
            marker_line_width=0,
            colorbar_title="Transaction Count"
        ))

        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox_zoom=5,
            mapbox_center={"lat": 20.5937, "lon": 78.9629},  # Center of India
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            title='Live Transactions in Indian States',
            hovermode='closest',
        )

        hover_text = [f"State: {state}<br>Year: {year}<br>Total Transactions: {count}<br>Total Transaction Amount: {amount}" 
                      for state, year, count, amount in zip(transaction_data['State'], transaction_data['Year'], transaction_data['Transaction_count'], transaction_data['Transaction_amount'])]
        fig.update_traces(hovertext=hover_text, hoverinfo="text")

        st.plotly_chart(fig)

        if not transaction_data.empty:
            st.header(f'Transaction Details for {selected_state}')
            st.write(transaction_data[['Year', 'Transaction_count', 'Transaction_amount']])
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
            
            # Plot bar charts for each option
            if selected_option_index == 1:  # Transaction Type Breakdown
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['Transaction_type'],
                    y=df['Total_Transactions'],
                    name='Total Transactions',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=df['Transaction_type'],
                    y=df['Total_Amount'],
                    name='Total Amount',
                    marker_color='orange'
                ))
                fig.update_layout(
                    title='Transaction Type Breakdown',
                    xaxis_title='Transaction Type',
                    yaxis_title='Value',
                    barmode='group',
                    legend_title="Legend",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

            elif selected_option_index == 2:  # User Metrics
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str),
                    y=df['RegisteredUsers'],
                    name='Registered Users',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=df['Year'].astype(str) + '-Q' + df['Quarter'].astype(str),
                    y=df['AppOpens'],
                    name='App Opens',
                    marker_color='orange'
                ))
                fig.update_layout(
                    title='User Metrics Over Time',
                    xaxis_title='Time (Year-Quarter)',
                    yaxis_title='Value',
                    barmode='group',
                    legend_title="Legend",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

            elif selected_option_index == 3:  # Geographical Analysis (Bar Chart)
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Transactions'],
                    name='Total Transactions',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Amount'],
                    name='Total Amount',
                    marker_color='orange'
                ))
                fig.update_layout(
                    title='Geographical Analysis of Transactions',
                    xaxis_title='State',
                    yaxis_title='Value',
                    barmode='group',
                    legend_title="Legend",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

            elif selected_option_index == 4:  # Quarterly Performance
                fig = go.Figure()
                for state in df['State'].unique():
                    state_data = df[df['State'] == state]
                    fig.add_trace(go.Bar(
                        x=state_data['Year'].astype(str) + '-Q' + state_data['Quarter'].astype(str),
                        y=state_data['Total_Transactions'],
                        name=state
                    ))
                fig.update_layout(
                    title='Quarterly Performance of Transactions',
                    xaxis_title='Time (Year-Quarter)',
                    yaxis_title='Total Transactions',
                    barmode='stack',
                    legend_title="States",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

            elif selected_option_index == 5:  # Top Performing States
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Transactions'],
                    name='Total Transactions',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Amount'],
                    name='Total Amount',
                    marker_color='orange'
                ))
                fig.update_layout(
                    title='Top Performing States',
                    xaxis_title='State',
                    yaxis_title='Value',
                    barmode='group',
                    legend_title="Legend",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

            elif selected_option_index == 6:  # Yearly Trends
                fig = go.Figure()
                for state in df['State'].unique():
                    state_data = df[df['State'] == state]
                    fig.add_trace(go.Scatter(
                        x=state_data['Year'],
                        y=state_data['Total_Transactions'],
                        mode='lines+markers',
                        name=state
                    ))
                fig.update_layout(
                    title='Yearly Trends in Transactions',
                    xaxis_title='Year',
                    yaxis_title='Total Transactions',
                    legend_title="States"
                )
                st.plotly_chart(fig)

            elif selected_option_index == 7:  # Overall Summary
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Transactions'],
                    name='Total Transactions',
                    marker_color='blue'
                ))
                fig.add_trace(go.Bar(
                    x=df['State'],
                    y=df['Total_Amount'],
                    name='Total Amount',
                    marker_color='orange'
                ))
                fig.update_layout(
                    title='Overall Summary of Transactions',
                    xaxis_title='State',
                    yaxis_title='Value',
                    barmode='group',
                    legend_title="Legend",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig)

        else:
            st.write("No data available for the selected analysis option.")
