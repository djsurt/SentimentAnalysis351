import pandas as pd
import re

def preprocess_text(text):
    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    # Remove mentions
    text = re.sub(r'@\w+', '', text)

    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text

# Load the dataset
data = pd.read_csv("impermium_verification_labels.csv")

# Preprocess and label the data
data['Comment'] = data['Comment'].apply(preprocess_text)
data['Label'] = data['Insult']  # Rename the 'Insult' column to 'Label'
data.drop('Insult', axis=1, inplace=True)

# Save the preprocessed and labeled data to a new CSV file
data.to_csv("preprocessed_insults_dataset.csv", index=False)
