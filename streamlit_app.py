#!/usr/bin/env python
# coding: utf-8

# #Installing the libries: 
# 
# !pip install numpy
# !pip install pandas
# !pip install streamlit
# !pip install altair
# !pip install streamlit_option_menu
# !pip install folium
# !pip install plotly

# In[1]:

# Using Important Libraries:
import streamlit as st
from matplotlib.patches import Circle, Rectangle
import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
import folium
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import string
from PIL import Image
import base64
import requests
import os
from datetime import datetime, timedelta
import warnings
import pandas as pd
import bcrypt
import base64
import json
from io import StringIO
import openpyxl


# Suppress specific warning
warnings.filterwarnings("ignore", message="missing ScriptRunContext!")


# In[2]:


# Define the content of the config.toml file
config_content = """
[theme]
base = "light"
font = "sans serif" 
"""

# Create the .streamlit directory if it doesn't exist
os.makedirs('.streamlit', exist_ok=True)

# Write the config.toml file
with open('.streamlit/config.toml', 'w') as f:
    f.write(config_content.strip())

#print("Configuration file created successfully.")

# In[3]:


#st.set_page_config(layout="wide")
st.set_page_config(
    layout="wide", 
    page_title="Forwarding & Terminal Support Portal",
    initial_sidebar_state="expanded",
)


# In[4]:
#Creating a holding frame for my svg icons: 
def encode_image(image_file):
    with open(image_file, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/svg+xml;base64,{encoded}"

#Importing data into my system: Avoiding instances where my excel file is has str headers: 
def read_csv_from_url(url: str, encoding='ISO-8859-1') -> pd.DataFrame:
    try:
        response = requests.get(url)
        response.raise_for_status() 
           
        csv_text = StringIO(response.text)  
           
        data = pd.read_csv(csv_text, encoding=encoding)
        return data
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the CSV file from {url}: {e}")
    except pd.errors.EmptyDataError:
        print(f"No data found in the CSV file at {url}.")
    except pd.errors.ParserError:
        print(f"Error parsing the CSV file at {url}.")
    except Exception as e:
        print(f"An error occurred while reading the CSV file at {url}: {e}")
    return pd.DataFrame() 
    
#Importing the data that is going to be used in this Project: 

loc = "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/Gomo_data.csv"
data = read_csv_from_url(loc, encoding='ISO-8859-1')
    
dataA = "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/Myles_data.csv"
dataA = read_csv_from_url(dataA, encoding='ISO-8859-1')
    
dataB= "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/Stephen_data.csv"
dataB = read_csv_from_url(dataB, encoding='ISO-8859-1')
    
dataC = "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/Esla_data.csv"
dataC = read_csv_from_url(dataC, encoding='ISO-8859-1')
    
dataD = "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/Anele_data.csv"
dataD = read_csv_from_url(dataD, encoding='ISO-8859-1')


#Merging the Dataframes to have concatinated master data: 

df= pd.concat([data,dataA,dataD,dataB,dataC], ignore_index=True)

# In[6]:


#Mapping Users by country:
end_list = "https://raw.githubusercontent.com/CSBSupport2025/Forwarding-Terminal-Support-Portal/main_support/Data/sys_user.csv"
endusers_list=read_csv_from_url(end_list, encoding='ISO-8859-1')

#Coercing the date:                      
df['sys_updated_on'] = pd.to_datetime(df['sys_updated_on' ], format='%d/%m/%Y',errors='coerce')
df['Year'] = df['sys_updated_on'].dt.year
# Convert to string with desired format
df['sys_updated_on'] = df['sys_updated_on'].dt.strftime('%m/%d/%Y')

# Split the date column--- timestamps & date separated - the day the incident was opened and closed
df['open_Date'] =  df['sys_updated_on']
df['open_Time'] = df['sys_updated_on_time']
df['country'] = df['caller_id'].map(endusers_list.set_index('name')['location'])

#delete all the tickets that are ServiceNow as resolved even though they were recalled by the caller:  Using the Query assignment_groupment
filter = df['short_description'].str.contains('Recall');
clean_df = df[~filter];


# In[7]:


clean_df.loc[:, 'Month'] = pd.to_datetime(clean_df['open_Date']).dt.strftime('%B')


# In[8]:


#clean_df.loc[:, 'Month_1'] = pd.to_datetime(clean_df['open_Date'], format='%Y-%m')
#clean_df.loc[:, 'Month'] = clean_df['Month_1'].dt.strftime('%B')

# Define the month order from January to December:
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
               'July', 'August', 'September', 'October', 'November', 'December']

clean_df.loc[:, 'Month'] = pd.Categorical(clean_df['Month'], categories=month_order, ordered=True)

# Sort the DataFrame by 'Month' to display it in proper chronological order
clean_df.sort_values(by='Month', inplace=True)

# Optionally, reset index if you want a clean DataFrame
clean_df.reset_index(drop=True, inplace=True)


# In[9]:


#Getting my JSONN country bame for Tanzania to correlate with the geospatial name: 
#clean_df["country"] =  clean_df["country"].replace("Tanzania", "United Republic of Tanzania")
# Replacing 'Tanzania' in 'country' column
clean_df.loc[:, 'country'] = clean_df['country'].replace("Tanzania", "United Republic of Tanzania")

# In[10]:


# Define the color schemes:
color_theme_list = {
    'CSBJHB1': ['#5d88b3', '#2e4459','#6d93ba','#becfe0','#495766', '#1d2328','#8c96a0','#d8e3ec'],
    'CSBJHB2': ['#005172','#003044', '#001822', '#4c859c', '#99b9c6','#4c859c' , '#99b2bc','#668b9a'],
    'CSBJHB3': ['#002748', '#193c5a', '#32526c', '#4c677e', '#667d91', '#7f93a3','#99a8b5', '#b2bec8'],
    'CSBJHB4': ['#2d2a27', '#5a544e','#cac5c1','#f4f3f2','#005475', '#008cc4', '#006289', '#005475']
}


# In[11]:

import streamlit as st
import time
import yaml
import streamlit as st
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities import (CredentialsError,
                                               ForgotError,
                                               Hasher,
                                               LoginError,
                                               RegisterError,
                                               ResetError,
                                               UpdateError)

# Specify the relative path to the image
image_path = os.path.join("Images", "download.jpeg")

base64_image = encode_image(image_path)




def render_auth_css(base64_image):
    # CSS with background image for login state:
    st.markdown(
        f"""
        <style>
        [data-testid="stApp"] {{
            background-image: url('data:image/jpeg;base64,{base64_image}');
            background-size: cover; 
        }}
        [data-testid="stElementContainer"] {{
            width: 400px; 
            height: auto; 
            margin: auto; 
            border: 4px solid #3e6184; 
            border-radius: 10px;
            padding: 20px; 
            background-color: rgba(255, 255, 255, 0.8);
        }}
        #[data-testid="stForm"] {{
            width: 460px;
            margin: auto; 
            border: 2px solid #3e6184; 
            border-radius: 10px; 
            padding: 20px; 
            background-color: rgba(255, 255, 255, 0.8);
            margin-top: 120px;
        }}
        [data-testid="stTextInputRootElement"] {{
            width: 85%; 
            margin-bottom: 10px; 
        }}
        .stButton {{
            width: 100%; 
            font-family: 'Arial', sans-serif;
            font-size: 20px; 
        }}
        </style>
        """,
        unsafe_allow_html=True)
    
# Loading config file
with open('.streamlit/config.yaml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Creating the authenticator object:
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


# Creating a login widget:
try:
   authenticator.login()
   #render_auth_css(base64_image)
   #st.stop()
except LoginError as e:
    st.error(e)


def show_message():
    placeholder = st.empty()  # Create an empty placeholder for the message
    placeholder.write(f'Welcome *{st.session_state["name"]}*')
    time.sleep(3)  # Wait for 3 seconds
    placeholder.empty()  # Remove the message

# Authenticating user:
if st.session_state['authentication_status']:
    show_message()
    with st.sidebar:
        #st.markdown("<h3 style='text-align: left;'>SLA FILTERI</h3>", unsafe_allow_html=True)
        # Specify the relative path to the image
        image_sidebar= os.path.join("Images", "logo-c-fc-steinweg2x.png")  

        # Replace with your image name
        #base64_image = get_base64_image(image_path)
        st.image(image_sidebar)
        #st.image("C:/Users/Gomolemo.Kototsi/Downloads/logo-c-fc-steinweg2x.png")
    
        # Initial selection summary:
        if st.checkbox("Annual Report", value=True):
            selected_month = sorted(clean_df["Month"].unique())
        else:
            selected_month = st.sidebar.multiselect("Select Month",sorted((clean_df["Month"]).unique()),default=sorted(clean_df["Month"].unique()))
        
        if st.checkbox("Overall incidents", value=True):
            selected_status = sorted(clean_df["state"].astype('str').unique())
        else:
            selected_status = st.multiselect("Select Incident Phase",sorted((clean_df["state"].astype('str')).unique()), default=sorted(clean_df["state"].astype('str').unique()))
    
        # Interactive Color themes:
        if st.checkbox("Year Filter", value=True):
           selected_year = sorted((clean_df["Year"]).unique())
        else:
            selected_year = st.multiselect('Select a Year',sorted((clean_df["Year"]).unique()),default=sorted(clean_df["Year"].unique()))
        
        selected_color_theme = st.selectbox('Select a color theme', list(color_theme_list.keys()))
        authenticator.logout()

    filtered_data = clean_df[(clean_df['state'].isin(selected_status)) & (clean_df['Month'].isin(selected_month) & (clean_df["Year"].isin(selected_year)))]


    filtered_category_totals_new = filtered_data.groupby(['state', 'assignment_group'])['number'].count().reset_index(name='Count')

    # Step 1: Rename all occurrences of 'A' in the 'Category' column to 'Alpha'
    filtered_category_totals_new.loc[filtered_category_totals_new['state'] == 'Closed', 'state'] = 'Resolved'

    # Step 2: Group by the 'Category' column and sum the 'Count'
    filtered_category_totals = filtered_category_totals_new.groupby(['state','assignment_group'], as_index=False).agg({'Count':'sum'})

    # creating an interactive Country Log Dataframe to be used for the map: 
    country_log_testing = filtered_data.groupby(['Month', 'country'])['number'].count().reset_index(name='incidents') 
    #right dataframe to use:
    country_log = country_log_testing.groupby('country')['incidents'].sum().reset_index()

    tickets_logged = filtered_data.groupby(['Year','Month', 'assignment_group'])['number'].count().reset_index(name='incidents')

    chart_colors = color_theme_list if not selected_color_theme else [color_theme_list['CSBJHB1'], color_theme_list['CSBJHB2']]
    #Setting up the environment for the geojson data:
    url = 'https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json'
    response = requests.get(url)
    counties = response.json()

    def create_choropleth(country_log, counties, selected_color_theme):
        # Check if there are no countries selected or all selected countries have zero incidents
        if country_log.empty or country_log['incidents'].sum() == 0:
            # Placeholder DataFrame: Display all countries with zero incidents
            country_log = pd.DataFrame({
                'country': [feature['properties']['name'] for feature in counties['features']],  # Use all countries in the geojson
                'incidents':  [0] * len(counties['features'])
                })
        
        # Determine the max incidents for setting the color range
        max_incidents = country_log['incidents'].max()
    
        # Avoid division by zero in color range calculation
        range_color = (0, max_incidents if max_incidents > 0 else 1)

        # Use default color theme if selected_color_theme is not found
        chart_colors = color_theme_list if not selected_color_theme else [color_theme_list['CSBJHB1'], color_theme_list['CSBJHB2']]
    
        # Check if all incident counts are zero
        if country_log['incidents'].sum() == 0:
            # Create a base map with no highlights
            fig = px.choropleth_mapbox(
                country_log,
                geojson=counties,
                locations='country',
                featureidkey="properties.name",
                color_discrete_sequence=['lightgrey'],  # Default color when no incidents
                mapbox_style="carto-positron",
                zoom=3,
                center={"lat": 0, "lon": 20},
                opacity=0.5,
                labels={'incidents': 'incidents'}
                )
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            return fig
                         
        # Create the choropleth map with incident highlights:
        max_incidents = country_log['incidents'].max()
        fig = px.choropleth_mapbox(
            country_log,
            geojson=counties,
            locations='country',
            featureidkey="properties.name",
            color='incidents',
            color_continuous_scale=color_theme_list[selected_color_theme][:len(country_log)],
            range_color=(0, country_log['incidents'].max()),
            mapbox_style="carto-positron",
            zoom=3,
            center={"lat": 0, "lon": 20},
            opacity=0.5,
            labels={'incidents': 'incidents rate'}
            )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig
    
    choropleth = create_choropleth(country_log, counties, selected_color_theme)

    name_category_totals = filtered_data.groupby(['assignment_group', 'assigned_to','u_service_offering_subcategory'])['number'].count().reset_index(name='Count')

    category_totals = filtered_data.groupby(['assignment_group', 'assigned_to'])['number'].count().reset_index(name='Count')

    def ensure_all_states(df, required_states=None):
        if required_states is None:
            required_states = ['In Progress', 'New', 'On Hold', 'Canceled', 'Resolved']
    
        # Check for missing states
        missing_states = [state for state in required_states if state not in df['state'].values]
    
        # Create a DataFrame for missing states with count 0
        missing_states_df = pd.DataFrame({'state': missing_states, 'Count': [0] * len(missing_states)})
    
        # Concatenate the original DataFrame with the missing states DataFrame
        df = pd.concat([df, missing_states_df], ignore_index=True)
    
        return df

    # Step 1: Group by 'assignment_group' and sum the 'Count'
    grouped_counts = filtered_category_totals.groupby('assignment_group')['Count'].sum().reset_index()

    # Step 2: Find the maximum count and the corresponding assignment group
    max_assignment_1 = grouped_counts.loc[grouped_counts['Count'].idxmax()]

    max_assignment = max_assignment_1.loc['assignment_group']

    # Step 3: Calculate the total count of all assignment groups
    total_count_groups_count= grouped_counts['Count'].sum()

    max_assignement_value = int(max_assignment_1['Count'])

    # Step 4: Calculate the percentage of the maximum count relative to the total count
    max_percentage = f"{float(round((max_assignment_1['Count'] / total_count_groups_count) * 100, 3))}%"


    def calculate_max_user(users_totals):
        # Check if DataFrame is empty
        if name_category_totals.empty:
            print("The DataFrame is empty.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}

        # Group by 'assigned_to' and sum 'Count'
        total_person = name_category_totals.groupby('assigned_to')['Count'].sum().reset_index()

        # Check if total_person is empty
        if total_person.empty:
            print("No incidents to report.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}

        # Identify the user(s) with the maximum incident count
        max_incident_count = total_person['Count'].max()
        max_users = total_person[total_person['Count'] == max_incident_count]
        
        if len(max_users) > 1:
            state_priority = ['Resolved', 'New', 'In Progress', 'On Hold']
            state_sums = name_category_totals[name_category_totals['state'].isin(state_priority)].groupby(['assigned_to', 'state'])['Count'].sum().unstack(fill_value=0)
            
           
            max_user = None
            max_state_sum = 0
           
            for state in state_priority:
                if state in state_sums.columns:
                    state_sums_sorted = state_sums[state].nlargest(1)
                    if state_sums_sorted.iloc[0] > max_state_sum:
                        max_state_sum = state_sums_sorted.iloc[0]
                        max_user = state_sums_sorted.index[0]
            if max_user is None:
                max_user = max_users.iloc[0]['assigned_to']
        else:
            max_user = max_users.iloc[0]['assigned_to']
           
        if max_user == 0 or not max_user:
            print("No user with incidents to report.")
            return {"max_user": 0, "max_incident_count": 0, "percentage": 0}
   
        #Calculate the percentage of incidents handled by the max user
        total_incident_count = total_person['Count'].sum()
        percentage = (max_incident_count / total_incident_count) * 100 if total_incident_count > 0 else 0
        percentage = round(percentage)

        print(f"User with the highest incidents: {max_user} with {max_incident_count} incidents")
        print(f"Percentage of incidents handled by {max_user}: {percentage}%")

        return max_user, max_incident_count,percentage
   
    max_user,max_incident_count,percentage = calculate_max_user(name_category_totals)

    # Specify the relative path to the SVG icon
    svg_icon_path = os.path.join("Images", "family_history_48dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    local_icon_url = os.path.join("Images", "account_circle_78dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    local_icon_url1 = os.path.join("Images","warning.svg")
    groups_loc = os.path.join("Images","group_add_61dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    
    if os.path.exists(groups_loc):
        with open(groups_loc, "r") as file:
            groups_icon = file.read()
    else:
        None

    testing_svg = encode_image(svg_icon_path)
    #icon_url = encode_image(testing_svg)
    icon_url1 = encode_image(local_icon_url1)
    icon_url2 = encode_image(local_icon_url)
    #groups_icon = encode_image(groups_loc)

    service_groups = filtered_data.groupby(['assignment_group','state', 'assigned_to'])['number'].count().reset_index(name='Count')


    total_group = service_groups.groupby('assignment_group')['Count'].sum().reset_index()

    def get_max_group(service_groups, selected_states):
        # Check if DataFrame is empty
        if service_groups.empty:
            print("The DataFrame is empty.")
            max_group = None
            group_max_incident_count = 0
            percentage_group = 0
            return None, None, 0
        
        else:
            # Group by 'assignment_group' and sum 'Incident Count'
            total_group = service_groups.groupby('assignment_group')['Count'].sum().reset_index()
            
        # Check if total_group is empty
        if total_group.empty:
            print("No incidents to report.")
            group_with_max_incidents = None
            group_max_incident_count = 0
        else:
            # Identify the group with the maximum incident count
            max_group = total_group.loc[total_group['Count'].idxmax()]
                
            # Handle ties by checking states
            tied_groups = total_group[total_group['Count'] == max_group['Count']]
            if len(tied_groups) > 1:
                # Check state counts for tied groups
                state_counts = service_groups[service_groups['assignment_group'].isin(service_groups['assignment_group'])]
                state_priority = ['Resolved', 'In Progress', 'New']
                state_counts['state_Priority'] = pd.Categorical(state_counts['state'], categories=state_priority, ordered=True)
                state_counts = state_counts.sort_values(by=['state_Priority', 'Count'], ascending=[True, False])
                
                max_group = state_counts.groupby('assignment_group')['Count'].sum().idxmax()
                
            # Extract the group's name and the incident count
            group_with_max_incidents = max_group if isinstance(max_group, str) else max_group['assignment_group']
            group_max_incident_count = total_group.loc[total_group['assignment_group'] == group_with_max_incidents, 'Count'].values[0]
             
        # Calculate percentage if any incidents are present
        if group_max_incident_count > 0:
            total_group_count = total_group['Count'].sum()
            percentage_group = (group_max_incident_count / total_group_count) * 100
            percentage_group = round(percentage_group)
        else:
            percentage_group = 0
        return group_with_max_incidents, group_max_incident_count, percentage_group
        
    group_with_max_incidents, group_max_incident_count, percentage_group = get_max_group(service_groups, selected_status)
    
    # Creating a function to get totals:
    def total_counts(df, state_list=selected_status):
        if state_list is None:
            # Default list of states to include in the total count
            state_list = ['In Progress', 'New', 'On Hold', 'Canceled',  'Resolved']
    
        # Initialize total_counts to zero
        total_counts = 0
    
        # Loop over each state in the state_list
        for state in state_list:
            # Check if the state exists in the DataFrame
            if state in df['state'].values:
                # Add the count for the existing state
                total_counts += df.loc[df['state'] == state, 'Count'].values[0]
            else:
                # If the state is missing, assume its count is zero
                total_counts += 0
    
        return total_counts
    def get_state_counts(df, selected_states):
        state_counts = {state: {'count': 0, 'percentage': 0.0} for state in selected_states}
    
        # Calculate the total count for all selected states
        total_count = df[df['state'].isin(selected_states)]['Count'].sum()
    
        # Calculate counts for each selected state
        for state in selected_states:
            count = int(df.loc[df['state'] == state, 'Count'].sum())  # Use sum() to handle multiple entries
            state_counts[state]['count'] = count
    
        # Calculate the percentage for each state
        if total_count > 0:
            for state in selected_states:
                state_counts[state]['percentage'] = round(float(round((state_counts[state]['count'] / total_count) * 100, 2)), 3)
    
        # Add the total count to the dictionary
        state_counts['total'] = int(total_count)
    
        return state_counts


    # Assuming filtered_category_totals is your DataFrame and selected_status is your list of states
    state_counts = get_state_counts(filtered_category_totals, selected_status)

    # Safely access the counts and percentages for each selected state
    totals = {state: {
        'total': state_counts.get(state, {}).get('count', 0),
        'percentage': state_counts.get(state, {}).get('percentage', 0.0)
    } for state in selected_status}

    # Example of accessing specific totals
    total_in_progress = int(totals.get('In Progress', {}).get('total', 0))
    percentage_in_progress = f"{float(totals.get('In Progress', {}).get('percentage', 0.0))}%"


    total_cancelled = int(totals.get('Canceled', {}).get('total', 0))
    percentage_cancelled = f"{float(totals.get('Canceled', {}).get('percentage', 0.0))}%"


    total_new = int(totals.get('New', {}).get('total', 0))
    percentage_new = f"{float(totals.get('New', {}).get('percentage', 0.0))}%"

    total_resolved = int(totals.get('Resolved', {}).get('total', 0))
    percentage_resolved = f"{float(totals.get('Resolved', {}).get('percentage', 0.0))}%"

    total_on_hold = int(totals.get('On Hold', {}).get('total', 0))
    percentage_on_hold = f"{float(totals.get('On Hold', {}).get('percentage', 0.0))}%"

    # The total sum of counts for all selected states
    total_count_overall= int(state_counts.get('total', 0))
    percentage_total = f"{sum(totals[state]['percentage'] for state in selected_status)}%"
    

    import streamlit as st
    import os

    svg_icon_path = os.path.join("Images", "account_circle_78dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")

    # Ensure the file exists and read its contents
    if os.path.exists(svg_icon_path):
        with open(svg_icon_path, "r") as file:
            svg_icon = file.read()
    else:
        st.error(f"File not found: {svg_icon_path}")
    
    
    svg_progress_path = os.path.join("Images","pending_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    # Ensure the file exists and read its contents
    if os.path.exists(svg_progress_path):
        with open(svg_progress_path, "r") as file:
            svg_progress = file.read()
    else:
        None
        #st.error(f"File not found: {svg_progress_path}")
    
    # Getting a icon using CSS stle: - Highest
    svg_new_path= os.path.join("Images", "domain_add_64dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    # Ensure the file exists and read its contents
    if os.path.exists(svg_new_path):
        with open(svg_new_path, "r") as file:
            svg_new = file.read()
    else:
        None
        #st.error(f"File not found: {svg_new_path}")


    # In[41]:

    # Getting a icon using CSS style: - Highest:
    svg_resolved_path= os.path.join("Images","editor_choice_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    if os.path.exists(svg_resolved_path):
        with open(svg_resolved_path, "r") as file:
            svg_resolved = file.read()
    else:
        None
        #st.error(f"File not found: {svg_resolved_path}")

    
    # Getting a icon using CSS style: - Highest 
    svg_total_path = os.path.join("Images", "dataset_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    #svg_total = encode_image(svg_total_path)
    if os.path.exists(svg_total_path):
        with open(svg_total_path, "r") as file:
            svg_total = file.read()
    else:
        None


    # Getting a icon using CSS style: - Highest 
    svg_icon_path = os.path.join("Images", "back_hand_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
    #svg_hold = encode_image(svg_icon_path)
    if os.path.exists(svg_icon_path):
        with open(svg_icon_path, "r") as file:
            svg_hold = file.read()
    else:
        None
        #st.error(f"File not found: {svg_icon_path}")



    svg_cancelled_path = os.path.join("Images","delete_forever_40dp_3E6184_FILL0_wght400_GRAD0_opsz40.svg")
    #svg_cancelled = encode_image(svg_cancelled_path)
    if os.path.exists(svg_cancelled_path):
        with open(svg_icon_path, "r") as file:
            svg_cancelled = file.read()

    else:
        None
        #st.error(f"File not found: {svg_cancelled_path}")

    # Creating different color schemes - For my States Donut Chart: 
    color_discrete_map = {
        'Bridge Connect': '#92afcc',
        'BOS Support': '#5d88b3'}

    renaming_mapping = {'SAP interface': 'SAP Interface', 'Master`Data': 'Master Data'}
    sub_categories  = name_category_totals.groupby('u_service_offering_subcategory', as_index=False)['Count'].sum()
    sub_categories['u_service_offering_subcategory'] = sub_categories['u_service_offering_subcategory'].replace(renaming_mapping)

#sub_categories['u_service_offering_subcategory'] = name_category_totals['u_service_offering_subcategory'].replace(renaming_mapping)

    sub_categories_df =  sub_categories.groupby('u_service_offering_subcategory', as_index=False)['Count'].sum()

    sub_categories_sorted = sub_categories_df.sort_values(by="Count", ascending=False)


# In[45]:


    #Main board:  Header Overview:  
    col = st.columns((2, 4, 2), vertical_alignment="top")
    colors = ['#3e6184','#2e4459' ,'#5d88b3', '#92afcc', '#d5e0ec']
    # Custom CSS to set zoom level
    st.markdown(
        """
        <style>
        body {
            zoom: 1;  /* Adjust the zoom level here */
            }
        </style>
        """,
        unsafe_allow_html=True
        )


    with col[0]:
        st.write("#### ITSM Support Indicators:")
        # CSS styling my St.Metric: 
        pmg_him = f"""
        <style>
        @media (prefers-color-scheme: light) {{
            [data-testid="stMetric"] {{
               border-radius: 5px;
               border: 2px solid #000;
               margin: 5px;  /* Reduce space between metrics */
               padding: 10px;
               display: flex;
               flex-direction: row;
               align-items: center;
               justify-content: flex-start;
               height: 100px; /* Adjust height as needed */
               overflow: hidden; /* Ensure content does not overflow */
               }}
        }}
    
        @media (prefers-color-scheme: dark) {{
            [data-testid="stMetric"] {{
                border-radius: 10px;
                border: 2px solid #000;
                margin: 5px;  /* Reduce space between metrics */
                padding: 10px;
                display: flex;
                flex-direction: row;
                align-items: center;
                justify-content: flex-start;
                height: 100px; /* Adjust height as needed */
                overflow: hidden; /* Ensure content does not overflow */
               }}
        }}
        [data-testid="stMetricText"] {{
            display: flex;
            flex-direction: column;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
        }}
        [data-testid="stMetricIcon"] {{
            margin-right: 10px;
            flex-shrink: 0; /* Prevent icon from shrinking */
        }}
        [data-testid="stMetricValue"],
        [data-testid="stMetricDelta"],
        [data-testid="stMetricLabel"] {{
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        [data-testid="stMetricValue"]{{
            font-weight: bold;
            font-size: 1.5em;
        }}
        [data-testid="stMetricDelta"]{{
            font-weight: bold;
            font-size: 1.5em;
        }}
        [data-testid="stMetricLabel"] {{
           font-weight: bold;
           font-size: 1em; 
        }}
        </style>
        """
        st.markdown(pmg_him, unsafe_allow_html=True)
    
        #st.write("### Support Incidents KPIs:")
        with st.container():
           title_person = f'Top System Admin: {max_user}'
           value_person = f'{str(max_incident_count)}'
           delta_person = f'% Contribution YTD:{str(percentage)}%'
        
           #group_with_max_incidents, group_max_incident_count, percentage_group = get_max_group(service_groups, selected_status)
           icon = svg_icon.replace('<svg', '<svg style="width: 40px; height: 40px;"')
           def metric_with_icon(label, value, delta, svg_icon):
              #Resize the SVG icon
              resized_icon = svg_icon.replace('<svg', '<svg style="width: 40px; height: 40px;"')
              html = f"""
              <div style="display: flex; align-items: center; border: 2px solid #000; padding: 10px; border-radius: 5px;">
              <div style="display: flex; align-items: center;">
                  <div style="display: inline-block;">{resized_icon}</div>
                  <div style="display: inline-block; margin-left: 8px;">
                      <div style="font-weight: bold;">{label}</div>
                      <div style="font-size: 2rem;">{value}</div>
                      <div style="color: {'green' if delta.startswith('+') else '#3e6184'};">{delta}</div>
                  </div>
              </div>
              """
              st.markdown(html, unsafe_allow_html=True)
            
           #Top Service Group :
           title_group = f'Top IT Service Group: {group_with_max_incidents}'
           value_group = f'{str(group_max_incident_count)}'
           delta_group = f'% Contribution YTD:{percentage_group}%'

           # Metrics:  
           Progress_id = f'In Progress'
           Resolved_id =  f'Resolved'
           Hold_id = f'On-Hold'
           Cancelled_id = f'Cancelled'
           Workload_id = f'Workload'

           # Display Incident Summary Indicator: 
           metric_with_icon(Progress_id, total_in_progress, percentage_in_progress , svg_progress)
           metric_with_icon(Resolved_id, total_resolved , percentage_resolved, svg_resolved)
           #metric_with_icon(Hold_id, value_Hold ,delta_Hold, svg_hold)
           #metric_with_icon(New_id,value_New ,delta_New, svg_new)
           metric_with_icon(Cancelled_id, total_cancelled ,percentage_cancelled, svg_cancelled)
           metric_with_icon(Workload_id, total_count_overall,percentage_total, svg_new)
        
           #Displing the user:             
           metric_with_icon(title_person, value_person ,delta_person, svg_icon)
           #Displaying Max group:
           metric_with_icon(title_group, value_group ,delta_group, groups_icon)
        
    with col[1]:
        st.write("#### Southern & Eastern Forwarding & Terminals Support Footprint:")
        # Interactive Choropleth: 
        st.plotly_chart(choropleth, use_container_width=True)
        color_map = {
            'ZA - BOS Support': '#5d88b3',  # Color for Group 1
            'ZA - Bridge Connect': '#92afcc'   # Color for Group 2
        }
        # IT Personnel: 
        fig = px.bar(
            name_category_totals,
            x='assigned_to',
            y='Count',
            color='assignment_group',
            color_discrete_map= color_map,
            barmode='group',
            title='IT Incidents Support Totals by IT Personnel',
            labels={'Count': 'Total Incidents', 'Assigned to': 'IT Technician'}
        )
        #fig.update_layout(width=500,height=550)
        st.plotly_chart(fig, use_container_width=True)
    
    with col[2]:
        st.write("#### Top Service Requests:")
        # Function to create a progress bar in HTML
        def get_progress_bar_html(value, max_value=None, color='#3e6184'):
            if max_value is None:
                max_value = max(sub_categories_sorted['Count'])  # Use max incidents from the dataset if not provided
                percentage = (value / max_value) * 100
                return f"""
                <div style="background-color: #f3f3f3; border-radius: 5px; width: 100%; height: 20px; margin: 5px 0;">
                   <div style="background-color: {color}; width: {percentage}%; height: 100%; border-radius: 5px;"></div>
                </div>
                <div style="text-align: right; font-weight: bold;">{value}</div>  <!-- Display the count value -->
                """
        # Function to create HTML representation of the DataFrame
        def create_html_table(df):
            html = '<table style="width: 100%; border-collapse: collapse;">'
            html += '<thead><tr><th style="padding: 8px; text-align: left;">Service Offering Subcategory</th><th style="padding: 8px; text-align: left;">Count</th></tr></thead>'
            html += '<tbody>'
            for _, row in df.iterrows():
                html += f'<tr><td style="padding: 8px; border: 1px solid #ddd;">{row["u_service_offering_subcategory"]}</td>'
                html += f'<td style="padding: 8px; border: 1px solid #ddd;">{get_progress_bar_html(row["Count"])}</td></tr>'
            html += '</tbody></table>'
            return html
        
        html_table = create_html_table(sub_categories_sorted)
        #st.markdown(create_html_table(sub_categories_sorted), unsafe_allow_html=True)
    
        st.markdown(
            """
            <style>
            .scrollable-table {
                max-height: 700px; /* Adjust height as needed */
                overflow-y: auto;
                overflow-x: hidden;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            </style>
            <div class="scrollable-table">
            """ + html_table + """
            </div>
            """,
            unsafe_allow_html=True
        )
    
        # About the Board Type of Information: 
        with st.expander("Dashboard Overview: ", expanded=True):
            st.write('''
               - **Data Source**: ServiceNow Logged Incidents for both BOS & Bridge Connect within the period of 2023, 2024 & 2025.
               - IT Personnel Support Workload [**SLA Compliance Contribuion**]: Indicates contribution of IT agents contribution to the overall support of Bridge Connect & BOS System. 
               - Southern & Eastern African Mapbox [**Regional Analyses**]: Illustrates the support provided by local IT team to the **Regional Offices** (in hundreds)
               ''')

elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')
    #render_auth_css(base64_image)
    #Rendering the CSS style:
    path_image = os.path.join("Images", "download.jpeg")
    base64_image= encode_image(path_image)
    #
    #clear_css()


# Saving config file:
with open('.streamlit/config.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(config, file, default_flow_style=False)
