from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from waitress import serve
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/send-email": {"origins": "https://chatbot-lead-qualification-flow.vercel.app/"}})  # Replace with your front-end domain

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.json
    if not data:
        return jsonify({'status': 'error', 'error': 'No data provided'}), 400

    # Extract data with defaults
    contact = data.get('contact', {})
    name = contact.get('name', 'Client')
    email = contact.get('email', 'N/A')
    phone = contact.get('phone', 'N/A')
    country = data.get('countries', {}).get('base', 'N/A')
    expansion = ', '.join(data.get('countries', {}).get('expansion', [])) or 'None'
    services = ', '.join(data.get('services', [])) or 'None'
    addons = ', '.join(data.get('addons', [])) or 'None'
    total = data.get('finalTotal', 0)
    timeline = data.get('timeline', 'N/A')
    stage = data.get('businessStage', 'N/A')
    plan = data.get('plan', 'eBranch')
    branch_total_standalone = data.get('branch_total_standalone', 'TBD')
    branch_processing_time = data.get('branch_processing_time', 'TBD')
    ltd_registration_fee = data.get('ltd_registration_fee', 'TBD')
    tax_id_registration_fee = data.get('tax_id_registration_fee', 'TBD')
    entity_type = data.get('entity_type', 'N/A')
    lead_phase_cta = data.get('lead_phase_cta', 'Reply to this email to schedule your consultation today!')
    agent_name = data.get('agent_name', 'YourCompanyName Team')
    agent_position = data.get('agent_position', 'Customer Success Manager')
    agent_phone = data.get('agent_phone', '+123-456-7890')
    agent_email = data.get('agent_email', 'support@houseofcompanies.io')

    # Validate required fields
    if not email or not name:
        logger.error(f"Missing required fields: email={email}, name={name}")
        return jsonify({'status': 'error', 'error': 'Missing required fields: name and email'}), 400

    # Lead Email Template
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border: 1px solid #ddd; border-radius: 10px;">
          <h2 style="color: #007BFF;">Your {country} Business Expansion: Compliance-to-Scale Solutions</h2>
          <p>Dear {name},</p>
          <p>Thank you for your interest in establishing a business presence in {country}. As entrepreneurs ourselves, we understand that navigating foreign compliance requirements can be challenging, which is why we’ve created our Compliance-to-Scale solutions to simplify the process.</p>
          <h3>Our {plan} Plan: €1,995/year (or €199/month)</h3>
          <p>The {plan} Plan provides entrepreneurs with everything needed to maintain a fully compliant {country} business presence:</p>
          <ul>
            <li>Professional {country} business address with mail handling</li>
            <li>Complete branch/entity management and compliance monitoring</li>
            <li>Tax registration and ongoing compliance handling</li>
            <li>Financial reporting and document processing systems</li>
            <li>All preparation and filing of required documentation</li>
          </ul>
          <p>Through our specialized portal, you’ll have instant access to your compliance calendar, document vault, and real-time status tracking for all filings.</p>
          <h3>Optional Services</h3>
          <p>Based on your specific needs, you may require these additional services:</p>
          <ul>
            <li><strong>{country} Branch Registration</strong>: €{branch_total_standalone} (One-time, {branch_processing_time})</li>
            <li><strong>{entity_type} Company Formation</strong>: €{ltd_registration_fee}</li>
            <li><strong>{country} Tax ID Registration</strong>: €{tax_id_registration_fee}</li>
          </ul>
          <h3>Your Selections</h3>
          <table style="width: 100%; border-collapse: separate; border-spacing: 10px;">
            <tr><td><strong>💼 Business Stage:</strong></td><td>{stage}</td></tr>
            <tr><td><strong>🌍 Country:</strong></td><td>{country}</td></tr>
            <tr><td><strong>🌐 Expansion Regions:</strong></td><td>{expansion}</td></tr>
            <tr><td><strong>⏱ Timeline:</strong></td><td>{timeline}</td></tr>
            <tr><td><strong>🛠 Services:</strong></td><td>{services}</td></tr>
            <tr><td><strong>➕ Add-ons:</strong></td><td>{addons}</td></tr>
            <tr><td style="color: #28a745;"><strong>💶 Total Estimated Cost:</strong></td><td style="color: #28a745;"><strong>€{total}</strong></td></tr>
          </table>
          <h3>Next Steps</h3>
          <p>How does an entrepreneur move forward from here?</p>
          <ol>
            <li><strong>Schedule a Consultation</strong>: Book a 15-minute call to discuss your specific requirements.</li>
            <li><strong>Receive Your Personalized Plan</strong>: We’ll outline exactly which services you need based on your business model.</li>
            <li><strong>Begin Your {country} Expansion</strong>: We’ll handle all the complex compliance while you focus on business growth.</li>
          </ol>
          <p><strong>Call to Action</strong>: {lead_phase_cta}</p>
          <p><strong>Contact Information</strong></p>
          <p>Best regards,<br>
             {agent_name}<br>
             {agent_position}<br>
             House of Companies<br>
             Tel: {agent_phone}<br>
             Email: <a href="mailto:{agent_email}">{agent_email}</a><br>
             Website: <a href="https://www.houseofcompanies.io">www.houseofcompanies.io</a>
          </p>
          <p style="font-size: 12px; color: #888; border-top: 1px solid #ddd; margin-top: 30px; padding-top: 10px;">
            This message was generated by House of Companies. If you didn’t request this, please ignore.
          </p>
        </div>
      </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg['Subject'] = f"Your {country} Business Expansion: Compliance-to-Scale Solutions"
    msg['From'] = os.environ.get('EMAIL_ADDRESS', 'pardhasaradhi52609@gmail.com')
    msg['To'] = email
    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(
            os.environ.get('EMAIL_ADDRESS', 'pardhasaradhi52609@gmail.com'),
            os.environ.get('EMAIL_PASSWORD', 'bkla cbbn svoe nfyj')
        )
        server.send_message(msg)
        server.quit()
        logger.info(f"Email sent successfully to {email}")
        return jsonify({'status': 'success'})
    except smtplib.SMTPAuthenticationError:
        logger.error(f"Authentication failed for {email}")
        return jsonify({'status': 'error', 'error': 'Authentication failed'}), 500
    except Exception as e:
        logger.error(f"Failed to send email to {email}: {str(e)}")
        return jsonify({'status': 'error', 'error': str(e)}), 500

@app.route('/')
def health():
    return "Backend is alive!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    serve(app, host='0.0.0.0', port=port)