# PhonePe
This Streamlit app visualizes transaction and user metrics data from ThePhonepePulse GitHub repository. It processes data from a MySQL database to provide insights via interactive visualizations. Users can select states to view transaction counts on a Plotly map and access detailed yearly data.

This project aims to extract, process, and visualize data from ThePhonepePulse GitHub repository, offering insights via an interactive dashboard.

First, the data is extracted from the repository using scripting and stored in a suitable format like CSV or JSON. Next, Python with Pandas is utilized for data transformation, including cleaning, handling missing values, and preparing it for analysis.

The transformed data is then inserted into a MySQL database for efficient storage and retrieval, using the "mysql-connector-python" library for connectivity and SQL commands for insertion.

For visualization, a geovisualization dashboard is created using Streamlit and Plotly in Python. Plotly's map functions and Streamlit's interface enable an interactive and visually appealing display of data.

Key features include dynamic fetching of data from the MySQL database, with at least 10 dropdown options providing users with various facts and figures to explore.

Ensuring security, efficiency, and user-friendliness, the solution is thoroughly tested before deployment. The dashboard offers valuable insights into the data from ThePhonepePulse GitHub repository and is accessible to a wide audience.








