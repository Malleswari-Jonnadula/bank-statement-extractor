from google import genai

# Create a client
client = genai.Client(api_key="AIzaSyDN6TQXZEeFEbJD1fTrDgMlYY_WpCj9tGA")  # <-- replace with your API key

# Make a request to Gemini
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Hello! Can you tell me a fun fact about AI?"
)

# Print the text from the first candidate
print("Gemini says:", response.candidates[0].content.parts[0].text)
