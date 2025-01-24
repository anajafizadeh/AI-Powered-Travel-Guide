from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from markdown2 import markdown
import openai
from openai import OpenAI
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

client = OpenAI(api_key='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')

app = Flask(__name__)

def format_itinerary(itinerary_text):
    # Convert Markdown-like syntax to HTML
    html_content = markdown(itinerary_text)
    return html_content

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    destination = request.form['destination']
    days = int(request.form['days'])
    preferences = request.form['preferences']

    # Scrape data
    attractions = scrape_attractions(destination)

    # Generate itinerary
    raw_itinerary = generate_itinerary(destination, days, preferences, attractions)
    formatted_itinerary = format_itinerary(raw_itinerary)

    return render_template('result.html', destination=destination, itinerary=formatted_itinerary)

def scrape_attractions(destination):
    url = f"https://en.wikipedia.org/wiki/{destination.replace(' ', '_')}"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract notable landmarks or attractions from a specific section
    attractions_section = soup.find('span', id='Tourism')
    if attractions_section:
        attractions_list = attractions_section.find_next('ul')
        attractions = [item.text for item in attractions_list.find_all('li')[:5]]
    else:
        attractions = ["No specific attractions found."]
    if not attractions or attractions == ["No specific attractions found."]:
        attractions = ["local markets", "popular restaurants", "parks"]

    return attractions

def generate_itinerary(destination, days, preferences, attractions):
    # # Load the model and tokenizer
    # model_name = "EleutherAI/gpt-neo-125M"
    # tokenizer = AutoTokenizer.from_pretrained(model_name)
    # model = AutoModelForCausalLM.from_pretrained(model_name)

    # # Create the pipeline
    # generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

    # # Generate the itinerary
    # prompt = (
    #     f"Plan a {days}-day trip to {destination} with a focus on {preferences}. "
    #     f"Include these attractions in the itinerary: {', '.join(attractions)}. "
    #     "Provide a daily breakdown of activities."
    # )
    # result = generator(prompt, max_length=150, num_return_sequences=1, truncation=True)
    # return result[0]['generated_text']
    prompt = (
        f"Plan a {days}-day trip to {destination} with a focus on {preferences}. "
        f"Include these attractions in the itinerary: {', '.join(attractions)}. "
        "Provide a daily breakdown of activities."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {"role": "system", "content": "You are a travel itinerary generator."},
            {"role": "user", "content": prompt}
        ],
        )
        return response.choices[0].message.content.strip()
    except openai.OpenAIError as e:
        return f"Error generating itinerary: {e}"

if __name__ == '__main__':
    app.run(debug=True)
