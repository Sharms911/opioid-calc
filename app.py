from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Opioid conversion factors to MME (Morphine Milligram Equivalents)
# Based on CDC guidelines and clinical practice
OPIOID_CONVERSIONS = {
    'morphine': {'factor': 1.0, 'routes': ['oral', 'iv', 'im', 'sc']},
    'oxycodone': {'factor': 1.5, 'routes': ['oral']},
    'hydrocodone': {'factor': 1.0, 'routes': ['oral']},
    'codeine': {'factor': 0.15, 'routes': ['oral']},
    'tramadol': {'factor': 0.1, 'routes': ['oral']},
    'fentanyl_patch': {'factor': 2.4, 'routes': ['transdermal']},  # mcg/hr to MME
    'oxymorphone': {'factor': 3.0, 'routes': ['oral']},
    'hydromorphone': {'factor': 4.0, 'routes': ['oral']},
    'methadone_1_20': {'factor': 4.0, 'routes': ['oral']},  # 1-20mg/day
    'methadone_21_40': {'factor': 8.0, 'routes': ['oral']},  # 21-40mg/day
    'methadone_41_60': {'factor': 10.0, 'routes': ['oral']},  # 41-60mg/day
    'methadone_61_plus': {'factor': 12.0, 'routes': ['oral']},  # >60mg/day
    'buprenorphine': {'factor': 30.0, 'routes': ['sl', 'patch']},
    'tapentadol': {'factor': 0.4, 'routes': ['oral']}
}

# Safety thresholds based on CDC guidelines
MME_THRESHOLDS = {
    'caution': 50,  # Increased caution
    'high_risk': 90,  # High risk threshold
    'dangerous': 120  # Extremely dangerous
}

@app.route('/')
def index():
    """Main calculator page"""
    return render_template('index.html', opioids=OPIOID_CONVERSIONS)

@app.route('/calculate', methods=['POST'])
def calculate_mme():
    """Calculate MME and provide safety warnings"""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        
        total_mme = 0
        calculations = []
        
        for med in medications:
            opioid = med.get('opioid')
            dose = float(med.get('dose', 0))
            frequency = int(med.get('frequency', 1))
            
            if opioid in OPIOID_CONVERSIONS:
                conversion_factor = OPIOID_CONVERSIONS[opioid]['factor']
                daily_mme = dose * frequency * conversion_factor
                total_mme += daily_mme
                
                calculations.append({
                    'medication': opioid.replace('_', ' ').title(),
                    'dose': dose,
                    'frequency': frequency,
                    'factor': conversion_factor,
                    'daily_mme': round(daily_mme, 2)
                })
        
        # Determine risk level and warnings
        risk_level, warnings = get_safety_warnings(total_mme)
        
        return jsonify({
            'success': True,
            'total_mme': round(total_mme, 2),
            'calculations': calculations,
            'risk_level': risk_level,
            'warnings': warnings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def get_safety_warnings(mme):
    """Generate safety warnings based on MME total"""
    warnings = []
    
    if mme < MME_THRESHOLDS['caution']:
        risk_level = 'low'
        warnings.append('Total MME is within normal range.')
    elif mme < MME_THRESHOLDS['high_risk']:
        risk_level = 'moderate'
        warnings.extend([
            'CAUTION: MME ≥50 increases overdose risk.',
            'Consider non-opioid alternatives.',
            'Discuss risks and benefits with patient.',
            'Consider more frequent monitoring.'
        ])
    elif mme < MME_THRESHOLDS['dangerous']:
        risk_level = 'high'
        warnings.extend([
            'HIGH RISK: MME ≥90 significantly increases overdose risk.',
            'Strongly consider alternatives to opioids.',
            'If continuing, arrange frequent follow-up.',
            'Consider naloxone prescription.',
            'Evaluate for opioid use disorder.'
        ])
    else:
        risk_level = 'critical'
        warnings.extend([
            'CRITICAL RISK: MME ≥120 is extremely dangerous.',
            'Immediate review required.',
            'Strong recommendation to taper or discontinue.',
            'Prescribe naloxone immediately.',
            'Consider immediate referral to pain specialist.',
            'Screen for opioid use disorder.'
        ])
    
    return risk_level, warnings

@app.route('/conversion')
def conversion_tool():
    """Opioid conversion calculator page"""
    return render_template('conversion.html', opioids=OPIOID_CONVERSIONS)

@app.route('/convert', methods=['POST'])
def convert_opioid():
    """Convert from one opioid to another"""
    try:
        data = request.get_json()
        from_opioid = data.get('from_opioid')
        to_opioid = data.get('to_opioid')
        dose = float(data.get('dose', 0))
        
        if from_opioid not in OPIOID_CONVERSIONS or to_opioid not in OPIOID_CONVERSIONS:
            return jsonify({'success': False, 'error': 'Invalid opioid selection'}), 400
        
        # Convert to MME first, then to target opioid
        from_factor = OPIOID_CONVERSIONS[from_opioid]['factor']
        to_factor = OPIOID_CONVERSIONS[to_opioid]['factor']
        
        mme = dose * from_factor
        converted_dose = mme / to_factor
        
        # Apply safety reduction factor (typically 25-50% reduction for cross-tolerance)
        safe_dose = converted_dose * 0.75  # 25% reduction
        
        return jsonify({
            'success': True,
            'original_dose': dose,
            'mme_equivalent': round(mme, 2),
            'converted_dose': round(converted_dose, 2),
            'safe_starting_dose': round(safe_dose, 2),
            'warning': 'Start with 25-50% dose reduction due to incomplete cross-tolerance'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files including PWA files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    # Use environment port if available (for deployment)
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
