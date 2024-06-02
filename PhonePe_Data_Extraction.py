import os
import pandas as pd
import json
import mysql.connector

# Aggregate Extraction

Agg_Trans_path = r"G:\Data Science Projects\PhonePe\Clone\pulse\data\aggregated\transaction\country\india\state"

Agg_state_list = os.listdir(Agg_Trans_path)

clm = {'State': [], 'Year': [], 'Quarter': [], 'Transaction_type': [], 'Transaction_count': [], 'Transaction_amount': []}

for i in Agg_state_list:
    p_i = os.path.join(Agg_Trans_path, i)
    try:
        Agg_yr = os.listdir(p_i)
    except FileNotFoundError:
        print(f"Directory not found: {p_i}")
        continue
    
    for j in Agg_yr:
        p_j = os.path.join(p_i, j)
        try:
            Agg_yr_list = os.listdir(p_j)
        except FileNotFoundError:
            print(f"Directory not found: {p_j}")
            continue
        
        for k in Agg_yr_list:
            p_k = os.path.join(p_j, k)
            try:
                with open(p_k, 'r') as Data:
                    D = json.load(Data)
                    for z in D['data']['transactionData']:
                        Name = z['name']
                        count = z['paymentInstruments'][0]['count']
                        amount = z['paymentInstruments'][0]['amount']
                        clm['Transaction_type'].append(Name)
                        clm['Transaction_count'].append(count)
                        clm['Transaction_amount'].append(amount)
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quarter'].append(int(k.strip('.json')))
            except FileNotFoundError:
                print(f"File not found: {p_k}")
                continue

# Successfully created a dataframe
Agg_Trans = pd.DataFrame(clm)
print("Aggregated Transaction Data:")
print(Agg_Trans)


# Define the path to get the data as states
user_path = "G:/Data Science Projects/PhonePe/Clone/pulse/data/aggregated/user/country/india/state"
Agg_state_list = os.listdir(user_path)

# Initialize an empty list to hold DataFrame objects
dfs = []

# Iterate through each state
for state in Agg_state_list:
    state_path = os.path.join(user_path, state)
    years = os.listdir(state_path)

    for year in years:
        year_path = os.path.join(state_path, year)
        quarters = os.listdir(year_path)

        for quarter in quarters:
            quarter_path = os.path.join(year_path, quarter)

            with open(quarter_path, 'r') as data_file:
                data = json.load(data_file)

                # Extract registered users and app opens directly
                registered_users = data['data']['aggregated'].get('registeredUsers', None)
                app_opens = data['data']['aggregated'].get('appOpens', None)

                # Create a DataFrame for the current data
                df = pd.DataFrame({
                    'State': [state],
                    'Year': [year],
                    'Quarter': [int(quarter.strip('.json'))],
                    'RegisteredUsers': [registered_users],
                    'AppOpens': [app_opens]
                })

                # Append the DataFrame to the list
                dfs.append(df)

# Concatenate all DataFrames in the list into one DataFrame
Agg_User = pd.concat(dfs, ignore_index=True)

# Print or manipulate Agg_User DataFrame as needed
print("Aggregate User Data:")
print(Agg_User)

# Map extraction

Map_Trans_path = r"G:\Data Science Projects\PhonePe\Clone\pulse\data\map\transaction\hover\country\india\state"

Map_state_list = os.listdir(Map_Trans_path)

# Initialize an empty list to hold DataFrame objects
dfs = []

# Iterate through each state, year, and quarter
for state in Map_state_list:
    state_path = os.path.join(Map_Trans_path, state)
    years = os.listdir(state_path)

    for year in years:
        year_path = os.path.join(state_path, year)
        quarters = os.listdir(year_path)

        for quarter in quarters:
            quarter_path = os.path.join(year_path, quarter)

            with open(quarter_path, 'r') as data_file:
                data = json.load(data_file)

                # Check if hoverDataList is in the data
                if 'data' in data and 'hoverDataList' in data['data']:
                    hover_data_list = data['data']['hoverDataList']

                    # Extract data for each state/district in hoverDataList
                    for item in hover_data_list:
                        name = item['name']
                        metric = item['metric'][0]  # Assuming only one metric per state/district
                        transaction_count = metric['count']
                        transaction_amount = metric['amount']

                        # Create a DataFrame for the current data
                        df = pd.DataFrame({
                            'State': [state],
                            'District': [name],
                            'Year': [year],
                            'Quarter': [int(quarter.strip('.json'))],
                            'TransactionCount': [transaction_count],
                            'TransactionAmount': [transaction_amount]
                        })

                        # Append the DataFrame to the list
                        dfs.append(df)

# Concatenate all DataFrames in the list into one DataFrame
Map_Trans = pd.concat(dfs, ignore_index=True)

# Print Map Transaction Data
print("Map Transaction Data:")
print(Map_Trans)


Map_user_path = r"G:\Data Science Projects\PhonePe\Clone\pulse\data\map\user\hover\country\india\state"
Map_state_list = os.listdir(Map_user_path)

# Initialize an empty list to hold DataFrame objects
dfs = []

# Iterate through each state, year, and quarter
for state in Map_state_list:
    state_path = os.path.join(Map_user_path, state)
    years = os.listdir(state_path)

    for year in years:
        year_path = os.path.join(state_path, year)
        quarters = os.listdir(year_path)

        for quarter in quarters:
            quarter_path = os.path.join(year_path, quarter)

            with open(quarter_path, 'r') as data_file:
                data = json.load(data_file)

                # Check if hoverData is in the data
                if 'data' in data and 'hoverData' in data['data']:
                    hover_data = data['data']['hoverData']

                    # Extract data for each state/district in hoverData
                    for district, metrics in hover_data.items():
                        registered_users = metrics['registeredUsers']
                        app_opens = metrics['appOpens']

                        # Create a DataFrame for the current data
                        df = pd.DataFrame({
                            'State': [state],
                            'District': [district],
                            'Year': [year],
                            'Quarter': [int(quarter.strip('.json'))],
                            'RegisteredUsers': [registered_users],
                            'AppOpens': [app_opens]
                        })

                        # Append the DataFrame to the list
                        dfs.append(df)

# Concatenate all DataFrames in the list into one DataFrame
Map_User = pd.concat(dfs, ignore_index=True)

# Print Map user data
print("Map User Data:")
print(Map_User)

#Top Extraction

Top_Trans_path = r"G:\Data Science Projects\PhonePe\Clone\pulse\data\top\transaction\country\india\state"
Top_state_list = os.listdir(Top_Trans_path)

# Initialize an empty list to hold DataFrame objects
dfs = []

# Iterate through each state, year, and quarter
for state in Top_state_list:
    state_path = os.path.join(Top_Trans_path, state)
    years = os.listdir(state_path)

    for year in years:
        year_path = os.path.join(state_path, year)
        quarters = os.listdir(year_path)

        for quarter in quarters:
            quarter_path = os.path.join(year_path, quarter)

            with open(quarter_path, 'r') as data_file:
                data = json.load(data_file)

                # Check if 'districts' or 'pincodes' key is in the data
                if 'districts' in data['data']:
                    entities = data['data']['districts']
                elif 'pincodes' in data['data']:
                    entities = data['data']['pincodes']
                else:
                    continue  # Skip this data if neither key is present

                # Extract data for each entity in the list
                for entity in entities:
                    name = entity['entityName']
                    transaction_count = entity['metric']['count']
                    transaction_amount = entity['metric']['amount']

                    # Create a DataFrame for the current data
                    df = pd.DataFrame({
                        'State': [state],
                        'Entity': [name],
                        'Year': [year],
                        'Quarter': [int(quarter.strip('.json'))],
                        'TransactionCount': [transaction_count],
                        'TransactionAmount': [transaction_amount]
                    })

                    # Append the DataFrame to the list
                    dfs.append(df)

# Concatenate all DataFrames in the list into one DataFrame
Top_Trans = pd.concat(dfs, ignore_index=True)

# Print Top Transaction Data
print("Top Transaction Data:")
print(Top_Trans)


Top_User_path = r"G:\Data Science Projects\PhonePe\Clone\pulse\data\top\user\country\india\state"
Top_state_list = os.listdir(Top_User_path)

# Initialize an empty list to hold DataFrame objects
dfs = []

# Iterate through each state, year, and quarter
for state in Top_state_list:
    state_path = os.path.join(Top_User_path, state)
    years = os.listdir(state_path)

    for year in years:
        year_path = os.path.join(state_path, year)
        quarters = os.listdir(year_path)

        for quarter in quarters:
            quarter_path = os.path.join(year_path, quarter)

            with open(quarter_path, 'r') as data_file:
                data = json.load(data_file)

                # Check if 'data' is in the JSON structure
                if 'data' in data and data['data']:
                    # Extract data from 'states', 'districts', and 'pincodes'
                    for category in ['states', 'districts', 'pincodes']:
                        if category in data['data'] and data['data'][category]:
                            for item in data['data'][category]:
                                name = item['name']
                                registered_users = item['registeredUsers']

                                # Create a DataFrame for the current data
                                df = pd.DataFrame({
                                    'Category': [category],
                                    'Name': [name],
                                    'Year': [year],
                                    'Quarter': [int(quarter.strip('.json'))],
                                    'RegisteredUsers': [registered_users]
                                })

                                # Append the DataFrame to the list
                                dfs.append(df)

# Concatenate all DataFrames in the list into one DataFrame
if dfs:
    Top_User = pd.concat(dfs, ignore_index=True)
else:
    Top_User = pd.DataFrame()

# Print Top User Data
print("Top User Data:")
print(Top_User)

# Connecting To MySQL
mydb = mysql.connector.connect(
    user = 'root',
    password = 'charan',
    host = 'localhost',
    database = 'phonepe'

)

# Inserting Aggregate Transaction details

insert_query = """
INSERT INTO Agg_Trans(State, Year, Quarter, Transaction_type, Transaction_count, Transaction_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""
cursor = mydb.cursor()

# Convert DataFrame to list of tuples
aggregate_trans_db = [tuple(row) for row in Agg_Trans.values]

# Execute the query
cursor.executemany(insert_query, aggregate_trans_db)

# Commit the changes
mydb.commit()



# Inserting Aggregate User details

insert1_query = """
INSERT INTO Agg_user (State, Year, Quarter, RegisteredUsers, AppOpens)
VALUES (%s, %s, %s, %s, %s)
"""

# Convert DataFrame to list of tuples
aggregate_user_db = [tuple(row) for row in Agg_User.values]

# Execute the query
cursor.executemany(insert1_query, aggregate_user_db)

# Commit the changes
mydb.commit()



# Inserting Map Transaction details

insert2_query = """
INSERT INTO Map_Trans (State, District, Year, Quarter, TransactionCount, TransactionAmount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Convert DataFrame to list of tuples
map_trans_db = [tuple(row) for row in Map_Trans.values]

# Execute the query
cursor.executemany(insert2_query, map_trans_db)

# Commit the changes
mydb.commit()


# Inserting Map user details

insert3_query = """
INSERT INTO Map_user (State, District, Year, Quarter, RegisteredUsers, AppOpens)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Convert DataFrame to list of tuples
Map_user_db = [tuple(row) for row in Map_User.values]

# Execute the query
cursor.executemany(insert3_query, Map_user_db)

# Commit the changes
mydb.commit()



# Inserting Top Transaction details


insert4_query = """
INSERT INTO Top_Trans (State, Entity, Year, Quarter, Transaction_count, Transaction_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

# Convert DataFrame to list of tuples
top_trans_db = [tuple(row) for row in Top_Trans.values]

# Execute the query
cursor.executemany(insert4_query, top_trans_db)

# Commit the changes
mydb.commit()


# Inserting Top User details

insert5_query = """
INSERT INTO Top_user (Category, Name, Year, Quarter, RegisteredUsers)
VALUES (%s, %s, %s, %s, %s)
"""

# Convert DataFrame to list of tuples
top_user_db = [tuple(row) for row in Top_User.values]

# Execute the query
cursor.executemany(insert5_query,top_user_db)

# Commit the changes
mydb.commit()






