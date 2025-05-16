from flask import Blueprint, render_template, request
import requests

market_bp = Blueprint('market', __name__)

@market_bp.route('/career_market', methods=['GET'])
def career_market():
    job_title = request.args.get('job_title', '')
    location = request.args.get('location', '')

    if job_title and location:
        query = f"{job_title} jobs in {location}"
    elif job_title:
        query = f"{job_title} jobs"
    elif location:
        query = f"jobs in {location}"
    else:
        query = "developer jobs"

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "all",
        "country": "us",
        "language": "en"
    }

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "x-rapidapi-key": "4797b66196msh6bc26e180733e9ap1277d3jsn7f80a962b427",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        jobs = response.json().get("data", [])
    except Exception as e:
        jobs = []
        print(f"Error fetching job data: {e}")

    return render_template("career_market.html", jobs=jobs, job_title=job_title, location=location)
