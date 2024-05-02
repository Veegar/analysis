from flask import Flask, send_file, render_template
import time
import threading
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Function to fetch data from the API
def fetch_data_from_api():
    url = "http://soignee.pythonanywhere.com/students"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data from the API")
        return None

# Function to perform data analysis
def perform_data_analysis(data):
    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Task 1: Count the number of students in the school
    total_students = len(df)
    print("Total number of students in the school:", total_students)

    # Task 2: Pie chart of genders
    gender_counts = df['Gender'].value_counts()
    plt.figure(figsize=(8, 6))
    plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%')
    plt.title('Distribution of Genders')
    plt.savefig('static/gender_pie_chart.png')
    plt.close()

    # Task 3: Graph of the number of students from form 1 - 4
    form_counts = df['form'].value_counts().sort_index()
    plt.figure(figsize=(8, 6))
    plt.bar(form_counts.index, form_counts.values)
    plt.xlabel('Form')
    plt.ylabel('Number of Students')
    plt.title('Number of Students from Form 1 - 4')
    plt.xticks(range(1, 5))
    plt.savefig('static/form_bar_chart.png')
    plt.close()

    # Task 4: Age graph
    plt.figure(figsize=(8, 6))
    plt.hist(df['age'], bins=10, edgecolor='black')
    plt.xlabel('Age')
    plt.ylabel('Number of Students')
    plt.title('Age Distribution of Students')
    plt.savefig('static/age_histogram.png')
    plt.close()

    # Return the total number of students
    return total_students

# Function to continuously fetch data and perform analysis
def analyze_data():
    while True:
        # Fetch data from the API
        data = fetch_data_from_api()
        if data:
            # Perform data analysis and get the total number of students
            total_students = perform_data_analysis(data)

            # Update the total number of students in the HTML template
            with app.app_context():
                app.total_students = total_students

        # Add delay before fetching data again (adjust as needed)
        time.sleep(60)  # Fetch data every 60 seconds

# Start a separate thread to continuously analyze data
@app.before_request
def start_analyzer():
    thread = threading.Thread(target=analyze_data)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    return render_template('analysis.html', total_students=app.total_students)

@app.route('/graph/<graph_name>')
def get_graph(graph_name):
    return send_file(f'static/{graph_name}', mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True, port=3000)
