from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

OPIOID_CONVERSIONS = {
    'morphine': {'factor': 1.0},
    'oxycodone': {'factor': 1.5},
    'hydrocodone': {'factor': 1.0},
    'codeine': {'factor': 0.15},
    'tramadol': {'factor': 0.1},
    'fentanyl_patch': {'factor': 2.4},
    'oxymorphone': {'factor': 3.0},
    'hydromorphone': {'factor': 4.0},
    'methadone_1_20': {'factor': 4.0},
    'methadone_21_40': {'factor': 8.0},
    'methadone_41_60': {'factor': 10.0},
    'methadone_61_plus': {'factor': 12.0},
    'buprenorphine': {'factor': 30.0},
    'tapentadol': {'factor': 0.4}
}

@app.route('/')
def index():
    return render_template('index.html', opioids=OPIOID_CONVERSIONS)

@app.route('/calculate', methods=['POST'])
def calculate_mme():
    try:
        data = request.get_json()
        opioid = data.get('opioid')
        dose = float(data.get('dose', 0))
        frequency = int(data.get('frequency', 1))

        if opioid in OPIOID_CONVERSIONS:
            factor = OPIOID_CONVERSIONS[opioid]['factor']
            total_mme = dose * frequency * factor
            return jsonify({
                'success': True,
                'total_mme': round(total_mme, 2),
                'opioid': opioid,
                'dose': dose,
                'frequency': frequency,
                'factor': factor
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid opioid'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/conversion')
def conversion_tool():
    return render_template('conversion.html', opioids=OPIOID_CONVERSIONS)

@app.route('/convert', methods=['POST'])
def convert_opioid():
    try:
        data = request.get_json()
        from_opioid = data.get('from_opioid')
        to_opioid = data.get('to_opioid')
        dose = float(data.get('dose', 0))

        if from_opioid not in OPIOID_CONVERSIONS or to_opioid not in OPIOID_CONVERSIONS:
            return jsonify({'success': False, 'error': 'Invalid opioid selection'}), 400

        from_factor = OPIOID_CONVERSIONS[from_opioid]['factor']
        to_factor = OPIOID_CONVERSIONS[to_opioid]['factor']

        mme = dose * from_factor
        converted_dose = mme / to_factor
        safe_dose = converted_dose * 0.75  # 25% reduction

        return jsonify({
            'success': True,
            'original_dose': dose,
            'mme_equivalent': round(mme, 2),
            'converted_dose': round(converted_dose, 2),
            'safe_starting_dose': round(safe_dose, 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
