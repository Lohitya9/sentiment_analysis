# Import necessary libraries
from flask import Flask, render_template, request
import joblib
import psycopg2

# Load the trained SVM model
svm_model = joblib.load("svm_sentiment_model.pkl")

# Database connection information
db_host = 'your_rds_endpoint'  # Replace with your RDS endpoint
db_name = 'your_database_name'  # Replace with your RDS database name
db_user = 'your_database_user'  # Replace with your RDS master username
db_password = 'your_database_password'  # Replace with your RDS master password

# Function to save reviews and sentiment results to the database
def save_review_and_sentiment(review, sentiment):
    try:
        connection = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)
        cursor = connection.cursor()

        # Create a table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews_sentiments (
                id SERIAL PRIMARY KEY,
                review TEXT,
                sentiment TEXT
            )
        """)

        # Insert review and sentiment into the table
        cursor.execute("INSERT INTO reviews_sentiments (review, sentiment) VALUES (%s, %s)", (review, sentiment))

        connection.commit()
        cursor.close()

    except (Exception, psycopg2.Error) as error:
        print("Error saving review and sentiment:", error)

    finally:
        if connection:
            connection.close()

# Update the home route to save reviews and sentiments to the database
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # Get the user's input (product review)
        review = request.form['review']

        # Preprocess the review text
        processed_review = preprocess_text(review)

        # Convert processed review to a format suitable for the model
        review_vector = ' '.join(processed_review)

        # Predict the sentiment using the SVM model
        sentiment = svm_model.predict([review_vector])[0]

        # Save review and sentiment to the database
        save_review_and_sentiment(review, sentiment)

        return render_template('result.html', review=review, sentiment=sentiment)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)