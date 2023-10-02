from flask import Flask, render_template, request
import requests
import json
import openai
from metaphor_python import Metaphor

app = Flask(__name__)

# Set your OpenAI and Metaphor API keys here
openai.api_key = ""
metaphor_api_key = ""
metaphor = Metaphor("")


@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    image_prompt = ""

    if request.method == "POST":
        query = request.form.get("query")

        # Perform the Metaphor API request
        url = "https://api.metaphor.systems/search"
        payload = {"query": query, "numResults": 3, "useAutoprompt": True}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": metaphor_api_key
        }

        response = requests.post(url, json=payload, headers=headers)
        jsonResponse = json.loads(response.text)

        ids = []

        for i in range(len(jsonResponse["results"])):
            ids.append(jsonResponse["results"][i]["id"])

        result = ""

        response = metaphor.get_contents(ids)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role":
                "system",
                "content":
                "You are an assistant that helps visualize information, based on the information you receive, describe 1 image in under 20 words. Don't include any personal names in your description, avoid information that is sensitive and could lead to explicit images."
            }, {
                "role": "user",
                "content": str(response)
            }])

        image_prompt = completion.choices[0].message["content"]

        # Generate the image URL using OpenAI
        image = openai.Image.create(prompt=image_prompt, n=1, size="1024x1024")
        image_url = image['data'][0]['url']

    return render_template("index.html",
                           image_url=image_url,
                           image_prompt=image_prompt)


if __name__ == "__main__":
    app.run(debug=True)
