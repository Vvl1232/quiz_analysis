import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# API Endpoints for quiz data
CURRENT_QUIZ_ENDPOINT = "https://jsonkeeper.com/b/LLQT"
HISTORICAL_QUIZ_ENDPOINT = "https://jsonkeeper.com/b/LLQT"

# Step 1: Fetch and Validate Data
def fetch_quiz_data(endpoint):
    """
    Fetch data from the given API endpoint.
    """
    try:
        response = requests.get(endpoint, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Unable to fetch data. HTTP Status Code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching data: {str(e)}")
        return None

def validate_quiz_data(data, expected_keys):
    """
    Validate if the required keys exist in the data.
    """
    for key in expected_keys:
        if key not in data or not data[key]:
            print(f"Warning: Missing or empty key - {key}")
        else:
            print(f"Key '{key}' is valid.")

# Fetch data
current_quiz_data = fetch_quiz_data(CURRENT_QUIZ_ENDPOINT)
historical_quiz_data = fetch_quiz_data(HISTORICAL_QUIZ_ENDPOINT)

# Debugging output
print("Debug: Current Quiz Data:", current_quiz_data)
print("Debug: Historical Quiz Data:", historical_quiz_data)

# Validate fetched data
validate_quiz_data(current_quiz_data, ['quiz_submissions'])
validate_quiz_data(historical_quiz_data, ['quiz_history'])

# Convert JSON data to DataFrame
current_df = pd.DataFrame(current_quiz_data.get('quiz_submissions', []))
historical_df = pd.DataFrame(historical_quiz_data.get('quiz_history', []))

# Exit if any dataset is empty
if current_df.empty or historical_df.empty:
    print("Error: One or both datasets are empty. Exiting the program.")
    exit()

# Step 2: Analyze Data
def analyze_performance_data(current_df, historical_df):
    """
    Analyze student performance data based on historical trends.
    """
    # Check if required columns exist in the historical data
    required_cols = {'topic', 'accuracy', 'difficulty', 'score', 'submission_time'}
    if not required_cols.issubset(historical_df.columns):
        print(f"Missing columns in historical data: {required_cols - set(historical_df.columns)}")
        return pd.DataFrame(), pd.DataFrame()

    # Calculate average performance by topic
    topic_stats = historical_df.groupby('topic').agg({
        'accuracy': 'mean',
        'difficulty': 'mean',
        'score': 'mean'
    }).reset_index()

    # Analyze recent trends
    recent_trends = historical_df.sort_values(by='submission_time', ascending=False).head(5)
    recent_trends['submission_time'] = pd.to_datetime(recent_trends['submission_time'], errors='coerce')

    return topic_stats, recent_trends

# Perform data analysis
topic_stats, recent_trends = analyze_performance_data(current_df, historical_df)

# Exit if no valid data for analysis
if topic_stats.empty:
    print("No data available for topic performance analysis.")
    exit()

# Step 3: Generate Insights and Persona
def generate_insight_details(topic_stats, recent_trends):
    """
    Generate insights based on weak areas and improvement trends.
    """
    # Identify weak topics with low accuracy
    weak_topics = topic_stats[topic_stats['accuracy'] < 0.6]

    # Identify trends where accuracy improved
    improvement_trends = recent_trends[recent_trends['accuracy'].diff() > 0]

    return weak_topics, improvement_trends

def identify_student_persona(historical_df):
    """
    Identify strengths and consistency in a student's performance.
    """
    if historical_df.empty or 'accuracy' not in historical_df.columns:
        return "Insufficient data to analyze student persona."

    # Topics with least variation and highest accuracy
    consistent_topic = historical_df.groupby('topic').std()['accuracy'].idxmin()
    top_topic = historical_df.groupby('topic').mean()['accuracy'].idxmax()

    return {
        "Consistent Topic": consistent_topic,
        "Top Performing Topic": top_topic
    }

# Generate insights and persona analysis
weak_topics, improvement_trends = generate_insight_details(topic_stats, recent_trends)
student_persona = identify_student_persona(historical_df)

# Step 4: Visualization
def plot_performance_data(topic_stats, recent_trends):
    """
    Plot topic-wise performance and recent trends.
    """
    if not topic_stats.empty:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=topic_stats, x='topic', y='accuracy', palette='viridis')
        plt.title('Average Accuracy by Topic')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    if not recent_trends.empty:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=recent_trends, x='submission_time', y='accuracy', marker='o', color='blue')
        plt.title('Recent Accuracy Trends')
        plt.tight_layout()
        plt.show()

# Visualize performance
plot_performance_data(topic_stats, recent_trends)

# Step 5: Generate Recommendations
def generate_recommendations(weak_topics, student_persona):
    """
    Generate actionable recommendations for students.
    """
    recommendations = []

    # Recommendations for weak topics
    if weak_topics.empty:
        recommendations.append("No weak topics identified. Keep up the good work!")
    else:
        for _, row in weak_topics.iterrows():
            recommendations.append(f"Focus on the topic '{row['topic']}' with an accuracy of {row['accuracy']:.2f}.")

    # Recommendations based on persona analysis
    if isinstance(student_persona, dict):
        recommendations.append(f"Leverage your strength in '{student_persona['Top Performing Topic']}' to build confidence.")
        recommendations.append(f"Maintain consistency in '{student_persona['Consistent Topic']}'.")
    else:
        recommendations.append("Unable to analyze persona due to insufficient data.")

    return recommendations

# Get recommendations
recommendations = generate_recommendations(weak_topics, student_persona)

# Display recommendations
print("\nPersonalized Recommendations:")
for rec in recommendations:
    print(f"- {rec}")
