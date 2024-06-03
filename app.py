from flask import Flask, render_template, request, jsonify
import json
import csv
import os

app = Flask(__name__)

# Load data from JSON file
with open('teams.json') as f:
    data = json.load(f)

def tooltip(score):
    if score <= 2:
        return "Needs Attention"
    elif score <= 5:
        return "Average"
    elif score <= 8:
        return "Good"
    else:
        return "Excellent"

app.jinja_env.globals.update(tooltip=tooltip)

@app.route('/')
def index():
    departments = data.keys()
    return render_template('index.html', departments=departments)

@app.route('/get_teams', methods=['POST'])
def get_teams():
    department = request.form['department']
    teams = data.get(department, {}).keys()
    return jsonify(list(teams))

@app.route('/get_team_members', methods=['POST'])
def get_team_members():
    department = request.form['department']
    team_name = request.form['team_name']
    team_members = data.get(department, {}).get(team_name, [])
    return jsonify(team_members)

@app.route('/nps_form', methods=['POST'])
def nps_form():
    team_name = request.form['team_name']
    team_members = request.form['team_members'].split(', ')
    return render_template('nps_form.html', team_name=team_name, team_members=team_members)

@app.route('/submit_nps', methods=['POST'])
def submit_nps():
    team_name = request.form['team_name']
    given_by = request.form['given_by']
    given_by_email = request.form['given_by_email']
    scores = {}
    for key, value in request.form.items():
        if key.startswith('score_'):
            member = key[len('score_'):]
            scores[member] = value

    # Save scores to CSV
    csv_file = 'nps_scores.csv'
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Team Name', 'Team Member', 'NPS Score', 'Given By', 'Given By Official Mail ID'])
        for member, score in scores.items():
            writer.writerow([team_name, member, score, given_by, given_by_email])

    return 'NPS scores submitted successfully!'

if __name__ == '__main__':
    app.run(debug=True)
