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
    
#Importing the data that is going to be used in this Project: 
#/Data/Anele_data.csv
loc = "/Data/Gomo_data.csv"
data = get_resized_icon(loc, encoding='ISO-8859-1')
    
dataA = "/Data/Myles_data.csv"
dataA = get_resized_icon(dataA, encoding='ISO-8859-1')
    
dataB= "/Data/Stephen_data.csv"
dataB = get_resized_icon(dataB, encoding='ISO-8859-1')
    
dataC = "/Data/Esla_data.csv"
dataC = get_resized_icon(dataC, encoding='ISO-8859-1')
    
dataD = "/Data/Downloads/Anele_data.csv"
dataD = get_resized_icon(dataD, encoding='ISO-8859-1')


#Merging the Dataframes to have concatinated master data: 

df= pd.concat([data,dataA,dataD,dataB,dataC], ignore_index=True)


# In[5]:


#Creating a holding frame for my svg icons: 
def encode_image(image_file):
    with open(image_file, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/svg+xml;base64,{encoded}"
# In[6]:


#Mapping Users by country:
end_list = "/Data/sys_user.csv"
endusers_list=get_resized_icon(end_list, encoding='ISO-8859-1')

#Coercing the date:                      
df['sys_updated_on'] = pd.to_datetime(df['sys_updated_on'], format='%d/%m/%Y')

df['sys_updated_on'].dt.strftime('%m/%d/%Y')

# Split the date column--- timestamps & date separated - the day the incident was opened and closed
df['open_Date'] =  df['sys_updated_on']
df['open_Time'] = df['sys_updated_on_time']
df['Year'] = df['sys_updated_on'].dt.year
df['country'] = df['caller_id'].map(endusers_list.set_index('name')['location'])

#delete all the tickets that are ServiceNow as resolved even though they were recalled by the caller:  Using the Query assignment_groupment
filter = df['short_description'].str.contains('Recall');
clean_df = df[~filter];


# In[7]:


clean_df['Month'] = pd.to_datetime(clean_df['open_Date']).dt.strftime('%B')


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
clean_df["country"] =  clean_df["country"].replace("Tanzania", "United Republic of Tanzania")


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


# In[20]:
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Specify the relative path to the image
image_path = os.path.join("Images", "Download.jpeg")  # Replace with your image name
base64_image = get_base64_image(image_path)

#image_path = "C:/Users/Gomolemo.Kototsi/Downloads/Download.jpeg"  # Replace with your local image path
#base64_image = get_base64_image(image_path)
# Load users from .streamlit/config.toml
try:
    users = st.secrets["users"]  # Accessing users from the secrets
except KeyError as e:
    st.error(f"Error loading configuration: {e}")
    st.stop()

# Hash the passwords
hashed_users = {username: bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') for username, password in users.items()}

# Create a DataFrame
df = pd.DataFrame(list(hashed_users.items()), columns=['Username', 'Password'])

# Save to Excel
excel_path = "credentials.xlsx"  # Relative path for the Excel file
df.to_excel(excel_path, index=False)

# Load the Excel configuration
try:
    df = pd.read_excel(excel_path)  # Read the Excel file
    # Convert the DataFrame to a dictionary for easier access
    passwords = dict(zip(df['Username'], df['Password']))
except Exception as e:
    st.error(f"Error loading configuration: {e}")
    st.stop()

# Function to render CSS based on login state
def render_css(is_logged_in):
    if is_logged_in:
        # CSS without background image for logged-in state
        st.markdown(
            """
            <style>
            [data-testid="stApp"] {
                background-color: white; /* Change to a solid color or leave it white */
            }
            [data-testid="stElementContainer"] {
                width: 400px; 
                height: auto; 
                margin: auto; 
                border: 4px solid #3e6184; 
                border-radius: 10px;
                padding: 20px; 
                background-color: rgba(255, 255, 255, 0.8);
            }
            [data-testid="stForm"] {
                width: 460px;
                margin: auto; 
                border: 2px solid #3e6184; 
                border-radius: 10px; 
                padding: 20px; 
                background-color: rgba(255, 255, 255, 0.8);
                margin-top: 120px;
            }
            [data-testid="stTextInputRootElement"] {
                width: 85%; 
                margin-bottom: 10px; 
            }
            .stButton {
                background-color: #4CAF50; /* Button color */
                color: white; /* Button text color */
                width: 100%; /* Make button full width */
                font-family: 'Arial', sans-serif; /* Same font as input */
                font-size: 16px; /* Font size for button */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # CSS with background image for login state
        st.markdown(
            f"""
            <style>
            [data-testid="stApp"] {{
                background-image: url('data:image/jpeg;base64,{base64_image}');
                background-size: cover; /* Cover the entire area */
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
            [data-testid="stForm"] {{
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
                width: 100%; /* Make button full width */
                font-family: 'Arial', sans-serif; /* Same font as input */
                font-size: 20px; /* Font size for button */
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Check if the user is logged in
is_logged_in = st.session_state.get("password_correct", False)
# Render CSS based on login state
render_css(is_logged_in)

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        username = st.session_state["username"]
        password = st.session_state["password"]

        # Check if the username exists and verify the password
        if username in passwords:
            # Compare the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), passwords[username].encode('utf-8')):
                st.session_state["password_correct"] = True
                del st.session_state["password"]  # Don't store the username or password.
                del st.session_state["username"]
            else:
                st.session_state["password_correct"] = False
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False
    
is_logged_in = check_password()
render_css(is_logged_in)

if not is_logged_in:
    st.stop()
    
st.markdown('</div>', unsafe_allow_html=True)


# In[21]:


import streamlit as st


# In[22]:


# Creating a Sidebar for the New Page: 
with st.sidebar:
    #st.markdown("<h3 style='text-align: left;'>SLA FILTERI</h3>", unsafe_allow_html=True)
    st.image("/Data/logo-c-fc-steinweg2x.png", use_column_width=True) 
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


# In[23]:


filtered_data = clean_df[(clean_df['state'].isin(selected_status)) & (clean_df['Month'].isin(selected_month) & (clean_df["Year"].isin(selected_year)))]


# In[24]:


filtered_category_totals_new = filtered_data.groupby(['state', 'assignment_group'])['number'].count().reset_index(name='Count')

# Step 1: Rename all occurrences of 'A' in the 'Category' column to 'Alpha'
filtered_category_totals_new.loc[filtered_category_totals_new['state'] == 'Closed', 'state'] = 'Resolved'

# Step 2: Group by the 'Category' column and sum the 'Count'
filtered_category_totals = filtered_category_totals_new.groupby(['state','assignment_group'], as_index=False).agg({'Count':'sum'})


# In[25]:


# creating an interactive Country Log Dataframe to be used for the map: 
country_log_testing = filtered_data.groupby(['Month', 'country'])['number'].count().reset_index(name='incidents') 
#right dataframe to use:
country_log = country_log_testing.groupby('country')['incidents'].sum().reset_index()


# In[26]:


tickets_logged = filtered_data.groupby(['Year','Month', 'assignment_group'])['number'].count().reset_index(name='incidents')


# In[27]:


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
    # Reverse the color scale: dark = more, light = less
    #fig.update_traces(colorscale="Viridis", reversescale=True)
    
    return fig
    
choropleth = create_choropleth(country_log, counties, selected_color_theme)


# In[28]:


name_category_totals = filtered_data.groupby(['assignment_group', 'assigned_to','u_service_offering_subcategory'])['number'].count().reset_index(name='Count')


# In[29]:


category_totals = filtered_data.groupby(['assignment_group', 'assigned_to'])['number'].count().reset_index(name='Count')


# In[30]:


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


# In[31]:


# Step 1: Group by 'assignment_group' and sum the 'Count'
grouped_counts = filtered_category_totals.groupby('assignment_group')['Count'].sum().reset_index()

# Step 2: Find the maximum count and the corresponding assignment group
max_assignment_1 = grouped_counts.loc[grouped_counts['Count'].idxmax()]

max_assignment = max_assignment_1.loc['assignment_group']

# Step 3: Calculate the total count of all assignment groups
total_count_groups_count= grouped_counts['Count'].sum()

max_assignement_value = int(max_assignment_1['Count'])
# Step 4: Calculate the percentage of the maximum count relative to the total count
max_percentage = f'{float(round(((max_assignment_1['Count'] / total_count_groups_count) * 100),3))}%'


# In[32]:


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
   
   # Calculate the percentage of incidents handled by the max user
   total_incident_count = total_person['Count'].sum()
   percentage = (max_incident_count / total_incident_count) * 100 if total_incident_count > 0 else 0
   percentage = round(percentage)

   print(f"User with the highest incidents: {max_user} with {max_incident_count} incidents")
   print(f"Percentage of incidents handled by {max_user}: {percentage}%")

   return max_user, max_incident_count, percentage
   
max_user,max_incident_count,percentage = calculate_max_user(name_category_totals)
#country_totals = name_category_totals.groupby(['assigned_to','country'])['Count'].sum().reset_index()
#countries_test=  country_totals.groupby('country')['Count'].sum().reset_index()


# In[33]:
# Specify the relative path to the SVG icon
svg_icon_path = os.path.join("Icons", "icon_name.svg")  # Replace with your SVG icon name
encoded_svg = encode_image(svg_icon_path)
# Path to your local SVG file:
local_svg_path = os.path.join("Images", "family_history_48dp_3E6184_FILL0_wght400_GRAD0_opsz48.sv")
icon_url = encode_image(local_svg_path)
local_icon_url1 = os.path.join("Images","warning.svg")
icon_url1 = encode_image(local_icon_url1)
local_icon_url = os.path.join("Images","account_circle_78dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
icon_url2 = encode_image(local_icon_url)
groups_loc = os.path.join("Images","group_add_61dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
groups_icon = encode_image(groups_loc)


# In[34]:


service_groups = filtered_data.groupby(['assignment_group','state', 'assigned_to'])['number'].count().reset_index(name='Count')


# In[35]:


total_group = service_groups.groupby('assignment_group')['Count'].sum().reset_index()


# In[36]:


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


# In[37]:


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


# In[38]:


def get_state_counts(df, selected_states):
    # Initialize the result dictionary with selected states
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
percentage_in_progress = f'{float(totals.get('In Progress', {}).get('percentage', 0.0))}%'

total_cancelled = int(totals.get('Canceled', {}).get('total', 0))
percentage_cancelled = f'{totals.get('Canceled', {}).get('percentage', 0.0)}%'

total_new = int(totals.get('New', {}).get('total', 0))
percentage_new = f'{totals.get('New', {}).get('percentage', 0.0)}%'

total_resolved = int(totals.get('Resolved', {}).get('total', 0))
percentage_resolved = f'{totals.get('Resolved', {}).get('percentage', 0.0)}%'

total_on_hold = int(totals.get('On Hold', {}).get('total', 0))
percentage_on_hold = f'{totals.get('On Hold', {}).get('percentage', 0.0)}%'

# The total sum of counts for all selected states
total_count_overall= int(state_counts.get('total', 0))
percentage_total = f'{sum(totals[state]['percentage'] for state in selected_status)}%'


# In[39]:

svg_icon_path = os.open("Images", "account_circle_78dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
with open(svg_icon_path, "r") as file:
    svg_icon = file.read()     
    
# Getting a icon using CSS style: - Highest
svg_groups_path = os.open("Images", "group_add_61dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
with open(svg_groups_path, "r") as file:
    groups_icon = file.read()


# In[40]:

# Getting a icon using CSS style: - Highest
svg_progress_path = os.open("Images","pending_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg" )
with open(svg_progress_path, "r") as file:
    svg_progress = file.read()
    
# Getting a icon using CSS style: - Highest
svg_new_path= os.open("Images", "domain_add_64dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
with open(svg_new_path, "r") as file:
    svg_new = file.read()


# In[41]:
# Getting a icon using CSS style: - Highest:
svg_resolved_path= os.open("Images", "editor_choice_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
with open(svg_resolved_path, "r") as file:
    svg_resolved = file.read()
    
# Getting a icon using CSS style: - Highest 
svg_total_path = os.open("Images", "dataset_50dp_3E6184_FILL0_wght400_GRAD0_opsz48")
with open(svg_total_path, "r") as file:
    svg_total = file.read()


# In[42]:


# Getting a icon using CSS style: - Highest 
svg_icon_path = os.open("Images", "back_hand_50dp_3E6184_FILL0_wght400_GRAD0_opsz48.svg")
with open(svg_icon_path, "r") as file:
    svg_hold = file.read()
    
svg_cancelled_path = open.open("Images","delete_forever_40dp_3E6184_FILL0_wght400_GRAD0_opsz40.sv")
with open(svg_cancelled_path, "r") as file:
    svg_cancelled = file.read()


# In[43]:


#Creating different color schemes - For my States Donut Chart: 
color_discrete_map = {
        'Bridge Connect': '#92afcc',
        'BOS Support': '#5d88b3'}


# In[44]:


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
        # Top IT Personnel:
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
            
        #Top Service Group
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


# !streamlit run "C:\Users\Gomolemo.Kototsi\Downloads\Support_Footprint.py"

# In[ ]:





# In[ ]:





# In[ ]:




