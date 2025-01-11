# # app.py
# from flask import Flask, render_template, request, jsonify
# import google.generativeai as genai
# import os
# from werkzeug.utils import secure_filename

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key-here'
# app.config['UPLOAD_FOLDER'] = 'uploads'

# # Ensure upload folder exists
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# # Initialize Gemini
# GOOGLE_API_KEY = "AIzaSyDTYvKY2RFaAZlCxwPPIcXit15DNLxZlnY"
# genai.configure(api_key=GOOGLE_API_KEY)


# def get_model():
#     return genai.GenerativeModel('gemini-pro')



# def get_vision_model():
#     return genai.GenerativeModel('gemini-pro-vision')


# @app.route('/')
# def index():
#     return render_template('index.html')



# @app.route('/personal')
# def personal():
#     return render_template('personal.html')



# @app.route('/login')
# def login():
#     return render_template('login.html')

# @app.route('/about')
# def about():
#     return render_template("about.html")

# @app.route('/generate_text', methods=['POST'])
# def generate_text():
#     try:
#         prompt = request.json.get('prompt')
#         model = get_model()
#         response = model.generate_content(prompt)
#         return jsonify({'response': response.text})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    


# @app.route('/chat', methods=['POST'])
# def chat():
#     try:
#         message = request.json.get('message')
#         model = get_model()
#         chat = model.start_chat()
#         response = chat.send_message(message)
#         return jsonify({'response': response.text})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    


# @app.route('/process_image', methods=['POST'])
# def process_image():
#     try:
#         if 'image' not in request.files:
#             return jsonify({'error': 'No image provided'}), 400
        
#         image = request.files['image']
#         prompt = request.form.get('prompt', 'Describe this image')
        
#         if image.filename == '':
#             return jsonify({'error': 'No selected file'}), 400
        
#         filename = secure_filename(image.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         image.save(filepath)
        
#         model = get_vision_model()
#         image_data = genai.Image.from_file(filepath)
#         response = model.generate_content([prompt, image_data])
        


#         # Clean up uploaded file
#         os.remove(filepath)
        

#         return jsonify({'response': response.text})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500



# if __name__ == '__main__':
#     app.run(debug=True)
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename
from newsapi import NewsApiClient
from random import shuffle
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize Gemini
GOOGLE_API_KEY = "AIzaSyDTYvKY2RFaAZlCxwPPIcXit15DNLxZlnY"
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize NewsAPI
NEWS_API_KEY = 'e2917836a68244b8b0751009a26ebaef'
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

def get_model():
    return genai.GenerativeModel('gemini-pro')

def get_vision_model():
    return genai.GenerativeModel('gemini-pro-vision')

def get_tech_and_job_news():
    try:
        # Get current date and date 7 days ago
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get technology news
        tech_news = newsapi.get_everything(
            q='technology OR tech OR innovation',
            language='en',
            sort_by='publishedAt',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            page_size=15
        )

        # Get job-related news
        job_news = newsapi.get_everything(
            q='jobs OR career OR employment OR hiring',
            language='en',
            sort_by='publishedAt',
            from_param=start_date.strftime('%Y-%m-%d'),
            to=end_date.strftime('%Y-%m-%d'),
            page_size=15
        )

        # Combine and process the news
        tech_articles = tech_news.get('articles', [])
        job_articles = job_news.get('articles', [])

        # Add category labels to articles
        for article in tech_articles:
            article['category'] = 'Technology'
        for article in job_articles:
            article['category'] = 'Jobs & Careers'

        # Combine all articles
        all_articles = tech_articles + job_articles
        
        # Shuffle articles to mix categories
        shuffle(all_articles)
        
        return all_articles, None

    except Exception as e:
        return None, str(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/personal')
def personal():
    return render_template('personal.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/realtime', methods=['GET', 'POST'])
def realtime():
    articles, error = get_tech_and_job_news()
    return render_template('realtime.html', articles=articles, error=error)

@app.route('/news_search', methods=['GET', 'POST'])
def news_search():
    try:
        if request.method == "POST":
            keyword = request.form["keyword"]
            search_results = newsapi.get_everything(
                q=keyword,
                language='en',
                sort_by='relevancy',
                page_size=30
            )
            return render_template(
                "realtime.html", 
                search_articles=search_results['articles'],
                keyword=keyword
            )
    except Exception as e:
        articles, error = get_tech_and_job_news()
        return render_template("realtime.html", articles=articles, error=str(e))
    
    # For GET requests, show tech and job news
    articles, error = get_tech_and_job_news()
    return render_template("realtime.html", articles=articles, error=error)

@app.route('/generate_text', methods=['POST'])
def generate_text():
    try:
        prompt = request.json.get('prompt')
        model = get_model()
        response = model.generate_content(prompt)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    try:
        message = request.json.get('message')
        model = get_model()
        chat = model.start_chat()
        response = chat.send_message(message)
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_image', methods=['POST'])
def process_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image = request.files['image']
        prompt = request.form.get('prompt', 'Describe this image')
        
        if image.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = secure_filename(image.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        model = get_vision_model()
        image_data = genai.Image.from_file(filepath)
        response = model.generate_content([prompt, image_data])
        
        # Clean up uploaded file
        os.remove(filepath)
        
        return jsonify({'response': response.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)