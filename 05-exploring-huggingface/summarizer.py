from transformers import pipeline

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

text = """
Artificial Intelligence is transforming industries by enabling machines to learn 
from data and perform tasks that typically require human intelligence. It is used 
in healthcare, finance, cybersecurity, and many other domains to improve efficiency 
and decision-making.
"""

summary = summarizer(text, max_length=50, min_length=20, do_sample=False)

print("\nOriginal Text:\n", text)
print("\nSummary:\n", summary[0]['summary_text'])
