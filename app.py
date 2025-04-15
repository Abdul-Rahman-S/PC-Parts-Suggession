# Import necessary libraries
from flask import Flask, render_template, request, jsonify
import pandas as pd

# Initialize the Flask app
app = Flask(__name__)

# Load the dataset containing pre-assembled PC builds
df = pd.read_csv('expanded_pc_components.csv')

# Extract unique component names for populating dropdowns in the UI
def get_unique_components():
    return {
        'cases': sorted(df['case_Model'].unique().tolist()),            # Unique PC cases
        'cpus': sorted(df['cpu_Model'].unique().tolist()),              # Unique CPUs
        'gpus': sorted(df['video-card_Model'].unique().tolist()),       # Unique GPUs
        'memory': sorted(df['memory_Model'].unique().tolist()),         # Unique RAM modules
        'motherboards': sorted(df['motherboard_Model'].unique().tolist()), # Unique motherboards
        'psus': sorted(df['power-supply_Model'].unique().tolist()),     # Unique PSUs
        'hdds': sorted(df['internal-hard-drive_Model'].unique().tolist()) # Unique HDDs
    }

# Home route that renders the main web page (index.html)
@app.route('/')
def home():
    # Renders the homepage and injects the component dropdown values
    return render_template('index.html', **get_unique_components())

# Route to handle build suggestions based on user budget
@app.route('/suggest', methods=['POST'])
def suggest():
    try:
        # Get the budget value from the frontend form
        budget = float(request.form['budget'])
        
        # Filter builds within ±10% of the user’s budget
        filtered = df[(df['Total Price'] >= budget * 0.9) & 
                     (df['Total Price'] <= budget * 1.1)]
        
        # If no builds are found in the ±10% range, suggest the closest 3 builds by price difference
        if len(filtered) == 0:
            df['diff'] = abs(df['Total Price'] - budget)
            filtered = df.nsmallest(3, 'diff')
        
        # Format the build suggestions as JSON to send back to frontend
        suggestions = [{
            'Total Price': round(row['Total Price'], 2),
            'case_Model': row['case_Model'],
            'cpu_Model': row['cpu_Model'],
            'video-card_Model': row['video-card_Model'],
            'memory_Model': row['memory_Model'],
            'motherboard_Model': row['motherboard_Model'],
            'power-supply_Model': row['power-supply_Model'],
            'internal-hard-drive_Model': row['internal-hard-drive_Model']
        } for _, row in filtered.iterrows()]
        
        # Return the list of suggested builds as a JSON response
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        # In case of any error (e.g., bad input), return the error message
        return jsonify({'error': str(e)})

# Run the app in debug mode for development
if __name__ == '__main__':
    app.run(debug=True)
