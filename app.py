import random
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import yaml 

# Change footer
custom_footer = """
<style>
footer{
    visibility:visible;
}
footer:before{
    content: 'Made by Primoz Konda @ pk@business.aau.dk';
    display:block;
    position:relative;
    color:tomato;
}
</style>
"""

# Additional YAML config load
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Define the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

# Define the CSV file and the current DataFrame
csv_file = 'questions_working.csv'

# Load the dataset into questions_df
def load_dataset():
    return pd.read_csv(csv_file, encoding='latin1')

questions_df = load_dataset()

# Function to select a random question from a category
def select_random_question(level):
    unused_questions = questions_df[(questions_df['Level'] == level) & (questions_df['Status'] == 'Not Asked')]
    
    # If no unused questions, reset the status and try again
    if unused_questions.empty:
        # Reset the Status for all questions to 'Not Asked'
        questions_df['Status'] = 'Not Asked'
        questions_df.to_csv(csv_file, index=False) # Update CSV
        unused_questions = questions_df[(questions_df['Level'] == level) & (questions_df['Status'] == 'Not Asked')]

    # Now, we prioritize questions with the least count
    min_count = unused_questions['Count'].min()
    unused_questions_min_count = unused_questions[unused_questions['Count'] == min_count]
    
    selected_question_idx = random.choice(unused_questions_min_count.index)
    selected_question = questions_df.at[selected_question_idx, 'Question']

    # Increment the count for the selected question
    questions_df.at[selected_question_idx, 'Count'] += 1
    questions_df.at[selected_question_idx, 'Status'] = 'Asked'
    questions_df.to_csv(csv_file, index=False) # Update CSV

    # Return both the question and its ID
    return selected_question, questions_df.at[selected_question_idx, 'ID']

# Create the Streamlit app
def main():
    # Display the logo at the top left
    st.sidebar.image("https://yt3.googleusercontent.com/ytc/AOPolaRAsNhgTRqpu-8yuBtkVa3rg1dk7dhm4lz3kRHz=s900-c-k-c0x00ffffff-no-rj", width=150)
    st.title("Applied Quantitative Methods")
    st.header("Exam Question Generator")
    st.markdown(custom_footer, unsafe_allow_html=True)
    
    # Handle authentication
    name, authentication_status, username = authenticator.login('Login', 'sidebar')
    if authentication_status:
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.write(f'Welcome, {name}')
        # Rest of your app logic
        app_logic()
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

def app_logic():
    # Sidebar creation
    st.sidebar.header("Insert a Number")
    student_seed = st.sidebar.text_input("Enter a number between 1 and 100:")
    #number = st.sidebar.number_input('Enter a number between 1 and 100:', min_value=1, max_value=100)
    # Input for student_seed
    #student_seed = st.text_input("Enter a number between 1 and 100:")
    

    # Button to generate questions
    if st.sidebar.button("Pick up Questions"):
        if not student_seed:
            st.warning("Please enter a student seed.")
        else:
            try:
                student_seed = int(student_seed) + random.randint(1, 100)
                generate_question(student_seed)
            except ValueError:
                st.warning("Student seed must be an integer.")
    
    # Space between buttons
    for _ in range(7):
        st.sidebar.text("")


    # Button to reset the dataset
    if st.sidebar.button("Reset dataset"):
        reset_dataset()
        st.success("Dataset has been reset.")

# Function to generate questions
def generate_question(student_seed):
    random.seed(student_seed)  # Set the random seed here with the student_seed

    # Ensure a different random seed for each call
    easy_question_1, id1 = select_random_question('Easy')
    easy_question_2, id2 = select_random_question('Easy')
    very_easy_question, id3 = select_random_question('Very Easy')
    moderate_question, id4 = select_random_question('Moderate')

    if all([easy_question_1, easy_question_2, very_easy_question, moderate_question]):
        # Display questions using Markdown
        st.markdown('---')  # Draw a horizontal line
        st.write("### Easy Questions")
        st.markdown(f"**ID: {id1}** \n\n <span style='font-size:1.3em; font-weight:bold;'>{easy_question_1}</span>", unsafe_allow_html=True)
        st.markdown(f"**ID: {id2}** \n\n <span style='font-size:1.3em; font-weight:bold;'>{easy_question_2}</span>", unsafe_allow_html=True)
        #st.markdown(f"**ID: {id1}** \n\n {easy_question_1}")
        #st.markdown(f"**ID: {id2}** \n\n {easy_question_2}")

    
        st.markdown('---')  # Draw a horizontal line
        st.write("### Mixed Questions")
        st.markdown(f"**ID: {id3}** \n\n <span style='font-size:1.3em; font-weight:bold;'>{very_easy_question}</span>", unsafe_allow_html=True)
        st.markdown(f"**ID: {id4}** \n\n <span style='font-size:1.3em; font-weight:bold;'>{moderate_question}</span>", unsafe_allow_html=True)
        #st.markdown(f"**ID: {id3}** \n\n {very_easy_question}")
        #st.markdown(f"**ID: {id4}** \n\n {moderate_question}")

# Function to reset the dataset
def reset_dataset():
    global questions_df
    questions_df = load_dataset()
    questions_df['Status'] = 'Not Asked'
    questions_df['Count'] = 0
    questions_df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    main()
