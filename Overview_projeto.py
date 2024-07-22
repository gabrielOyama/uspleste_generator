import streamlit as st

# Project Overview
st.title("Project Overview")

st.header("About the Project")
st.markdown("""
Welcome to the Sensor Data Visualization project. This project is designed to help you analyze and visualize data collected from various sensors. 
The main features include:
- Scatter plots to visualize sensor data based on geographical coordinates.
- Line plots to track sensor data over time for specific locations.
- Statistical summaries and metadata for a comprehensive understanding of the data.
""")

st.header("Project Metadata")
metadata = {
    "Project Name": "Sensor Data Visualization",
    "Project Lead": "John Doe",
    "Team Members": ["Alice Smith", "Bob Johnson", "Charlie Lee"],
    "Start Date": "January 1, 2023",
    "End Date": "December 31, 2023",
    "Funding": "$100,000",
    "Organization": "Data Science Corp",
    "Technologies Used": ["Python", "Streamlit", "Pandas", "Plotly"],
    "Contact": "john.doe@example.com"
}

# Display Metadata
for key, value in metadata.items():
    st.markdown(f"**{key}:** {', '.join(value) if isinstance(value, list) else value}")

st.header("Project Goals")
st.markdown("""
The primary goals of this project are:
1. To provide an interactive platform for visualizing sensor data.
2. To enable easy analysis of trends and patterns in the data.
3. To offer statistical summaries and metadata for better data understanding.
""")

st.header("Future Work")
st.markdown("""
Future enhancements for this project include:
- Integration with real-time data sources.
- Advanced statistical analyses and machine learning predictions.
- Improved user interface and experience.
""")

st.header("Acknowledgements")
st.markdown("""
We would like to thank the following individuals and organizations for their support and contributions:
- Data Science Corp for funding the project.
- All team members for their hard work and dedication.
- Users and testers who provided valuable feedback.
""")

# Add an image or logo (optional)
# st.image("path_to_logo.png", width=200)

# Add a button to navigate back to the main visualization page
if st.button("Go to Data Visualization"):
    st.experimental_rerun()