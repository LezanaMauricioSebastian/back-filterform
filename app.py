import os
from flask import Flask, Response, jsonify, request, send_file
import pandas as pd
import io
from flask_cors import CORS
app = Flask(__name__)

FILE_PATH = '../Downloads/ALL_LEADS.xlsx'
CORS(app)
# Function to read the Excel file
def read_excel_file(file_path):
    return pd.read_excel(file_path)

leads_df = read_excel_file(FILE_PATH)

Roles = leads_df['Role'].dropna().unique().tolist()
industries = leads_df['industry'].dropna().unique().tolist()
countries = leads_df['country'].dropna().unique().tolist()
cnaes = leads_df['CNAE'].dropna().unique().tolist()

def format_options(options):
    return [{'id': option, 'categoryName': option} for option in options]


# Endpoint to get roles
@app.route('/api/roles', methods=['GET'])
def get_roles():
    return jsonify(format_options(Roles))

# Endpoint to get industries
@app.route('/api/industries', methods=['GET'])
def get_industries():
    return jsonify(format_options(industries))

# Endpoint to get countries
@app.route('/api/countries', methods=['GET'])
def get_countries():
    return jsonify(format_options(countries))

# Endpoint to get cnaes
@app.route('/api/cnaes', methods=['GET'])
def get_cnaes():
    return jsonify(format_options(cnaes))

@app.route('/')
def index():
    return 'Welcome to the Lead Filter API'

@app.route('/api/filter-leads', methods=['POST'])
def filter_leads():
    filters = request.json
    try:
        df = read_excel_file(FILE_PATH)

        # Apply filters
        if filters['role']:
            df = df[df['role'] == filters['role']]
        if filters['industry']:
            df = df[df['industry'] == filters['industry']]
        if filters['country']:
            df = df[df['country'] == filters['country']]
        if filters['cnae']:
            df = df[df['CNAE'] == filters['cnae']]

        # Update DownloadCount
        print(df.head())
        if 'DownloadCount' not in df.columns:
            df['DownloadCount'] = 0
        df['DownloadCount'] += 1

        # Save the filtered leads to a CSV
        output = io.BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=filtered_leads.csv"}
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

