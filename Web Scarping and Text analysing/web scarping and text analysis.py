import requests
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

# Reading the input Excel file
input_df = pd.read_excel(r"C:\Users\Welcome\Downloads\Input.xlsx")

# Define stop words and positive/negative words lists
stop_words = set(stopwords.words('english'))
stop_words_files = [
    "StopWords_Auditor.txt",
    "StopWords_Currencies.txt",
    "StopWords_DatesandNumbers.txt",
    "StopWords_Generic.txt",
    "StopWords_GenericLong.txt",
    "StopWords_Geographic.txt",
    "StopWords_Names.txt"
]

# Function to read file with a fallback encoding
def read_file_with_fallback(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin1') as f:
            return f.read()

# Load additional stop words from files
for file in stop_words_files:
    try:
        stop_words.update(read_file_with_fallback(file).split())
    except FileNotFoundError:
        print(f"Warning: {file} not found. Make sure the file exists in the correct directory.")

# Load positive and negative words lists
try:
    positive_words = set(read_file_with_fallback("positive-words.txt").split())
    negative_words = set(read_file_with_fallback("negative-words.txt").split())
except FileNotFoundError as e:
    print(f"Error: {e}. Make sure the positive and negative words files exist in the correct directory.")
    raise

# Function to extract article text
def extract_article_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1').get_text()
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text() for p in paragraphs])
    return title + '\n' + text

# Function to clean text
def clean_text(text):
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.lower()
    return text

# Function to perform text analysis
def analyze_text(url_id, url, text):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    words = [word for word in words if word not in stop_words]
    word_count = len(words)
    sentence_count = len(sentences)
    syllable_count = sum([len(re.findall(r'[aeiou]', word)) for word in words])
    complex_word_count = sum([1 for word in words if len(re.findall(r'[aeiou]', word)) > 2])
    personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text))
    
    positive_score = sum([1 for word in words if word in positive_words])
    negative_score = sum([1 for word in words if word in negative_words])
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (word_count + 0.000001)
    
    avg_sentence_length = word_count / sentence_count
    avg_word_length = sum([len(word) for word in words]) / word_count
    percentage_complex_words = complex_word_count / word_count * 100
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    
    return {
        'URL_ID': url_id,
        'URL': url,
        'POSITIVE_SCORE': positive_score,
        'NEGATIVE_SCORE': negative_score,
        'POLARITY_SCORE': polarity_score,
        'SUBJECTIVITY_SCORE': subjectivity_score,
        'AVG_SENTENCE_LENGTH': avg_sentence_length,
        'PERCENTAGE_OF_COMPLEX_WORDS': percentage_complex_words,
        'FOG_INDEX': fog_index,
        'AVG_NUMBER_OF_WORDS_PER_SENTENCE': avg_sentence_length,
        'COMPLEX_WORD_COUNT': complex_word_count,
        'WORD_COUNT': word_count,
        'SYLLABLE_PER_WORD': syllable_count / word_count,
        'PERSONAL_PRONOUNS': personal_pronouns,
        'AVG_WORD_LENGTH': avg_word_length
    }

# Extract text for each URL and analyze it
results = []
for index, row in input_df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    try:
        article_text = extract_article_text(url)
        with open(f"{url_id}.txt", "w", encoding="utf-8") as file:
            file.write(article_text)
        print(f"Extracted text for URL_ID {url_id}")
        
        # Clean and analyze the text
        cleaned_text = clean_text(article_text)
        analysis = analyze_text(url_id, url, cleaned_text)
        results.append(analysis)
        
    except Exception as e:
        print(f"Failed to extract or analyze text for URL {url}: {e}")

# Save results to an Excel file
output_df = pd.DataFrame(results)
output_df.to_excel("Output Data Structure.xlsx", index=False)
print("Assignment completed successfully")
