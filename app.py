from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from waitress import serve
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/send-email": {"origins": "*"}})  # Replace with your front-end domain

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_html(text):
    """Basic HTML sanitization to prevent injection"""
    if not text:
        return 'N/A'
    # Convert to string and strip dangerous characters
    text = str(text).replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
    return text

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        if not data:
            logger.error("No JSON data provided in request")
            return jsonify({'status': 'error', 'error': 'No data provided'}), 400

        # Extract and sanitize data with proper defaults
        contact = data.get('contact', {})
        name = sanitize_html(contact.get('name', ''))
        email = contact.get('email', '').strip().lower()
        phone = sanitize_html(contact.get('phone', 'N/A'))
        
        # Handle countries properly - it might be a string or dict
        countries_data = data.get('countries', {})
        if isinstance(countries_data, str):
            country = sanitize_html(countries_data)
            expansion = 'None'
        else:
            country = sanitize_html(countries_data.get('base', 'N/A'))
            expansion_list = countries_data.get('expansion', [])
            expansion = ', '.join([sanitize_html(exp) for exp in expansion_list]) if expansion_list else 'None'
        
        # Handle services and addons
        services_list = data.get('services', [])
        services = ', '.join([sanitize_html(service) for service in services_list]) if services_list else 'None'
        
        addons_list = data.get('addons', [])
        addons = ', '.join([sanitize_html(addon) for addon in addons_list]) if addons_list else 'None'
        
        # Handle numeric values safely
        try:
            total = float(data.get('finalTotal', 0))
        except (ValueError, TypeError):
            total = 0
        
        timeline = sanitize_html(data.get('timeline', 'N/A'))
        stage = sanitize_html(data.get('businessStage', 'N/A'))
        plan = sanitize_html(data.get('plan', 'eBranch'))
        entity_type = sanitize_html(data.get('entity_type', 'N/A'))
        
        # Agent information with sanitization
        lead_phase_cta = sanitize_html(data.get('lead_phase_cta', 'Reply to this email to schedule your consultation today!'))
        agent_name = sanitize_html(data.get('agent_name', 'Dr. Krishna Kishore'))
        agent_position = sanitize_html(data.get('agent_position', 'Director'))
        agent_phone = sanitize_html(data.get('agent_phone', '+91 7893525665'))
        agent_email = data.get('agent_email', 'support@houseofcompanies.io').strip().lower()

        # Validate required fields
        if not name or not email:
            logger.error(f"Missing required fields: email='{email}', name='{name}'")
            return jsonify({'status': 'error', 'error': 'Missing required fields: name and email'}), 400

        # Validate email format
        if not is_valid_email(email):
            logger.error(f"Invalid email format: {email}")
            return jsonify({'status': 'error', 'error': 'Invalid email format'}), 400

        # Email configuration
        smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', 465))
        email_address = os.environ.get('EMAIL_ADDRESS')
        email_password = os.environ.get('EMAIL_PASSWORD')

        # Check for required environment variables
        if not email_address or not email_password:
            logger.error("Missing email credentials in environment variables")
            return jsonify({'status': 'error', 'error': 'Email service not configured'}), 500

        # Lead Email Template
        html = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="UTF-8">
            <title>Your {country} Business Expansion</title>
          </head>
          <body style="font-family: Arial, sans-serif; background-color: #f9f9f9; padding: 20px; margin: 0;">
            <div style="max-width: 600px; margin: auto; background-color: #fff; padding: 30px; border: 1px solid #ddd; border-radius: 10px;">
              <h2 style="color: #007BFF; margin-top: 0;">Your {country} Business Expansion: Compliance-to-Scale Solutions</h2>
              <p>Dear {name},</p>
              <p>Thank you for your interest in establishing a business presence in {country}. As entrepreneurs ourselves, we understand that navigating foreign compliance requirements can be challenging, which is why we've created our Compliance-to-Scale solutions to simplify the process.</p>
              
              <h3 style="color: #333;">Our {plan} Plan: €1,995/year (or €199/month)</h3>
              <p>The {plan} Plan provides entrepreneurs with everything needed to maintain a fully compliant {country} business presence:</p>
              <ul style="padding-left: 20px;">
                <li>Professional {country} business address with mail handling</li>
                <li>Complete branch/entity management and compliance monitoring</li>
                <li>Tax registration and ongoing compliance handling</li>
                <li>Financial reporting and document processing systems</li>
                <li>All preparation and filing of required documentation</li>
              </ul>
              
              <p>Through our specialized portal, you'll have instant access to your compliance calendar, document vault, and real-time status tracking for all filings.</p>
              
              <h3 style="color: #333;">Optional Services</h3>
              <p>Based on your specific needs, you may require these additional services:</p>
              <ul style="padding-left: 20px;">
                <li><strong>{country} Branch Registration</strong></li>
                <li><strong>Company Formation</strong></li>
                <li><strong>{country} Tax ID Registration</strong></li>
              </ul>
              
              <h3 style="color: #333;">Your Selections</h3>
              <table style="width: 100%; border-collapse: separate; border-spacing: 10px; margin: 20px 0;">
                <tr><td><strong>💼 Business Stage:</strong></td><td>{stage}</td></tr>
                <tr><td><strong>🌍 Country:</strong></td><td>{country}</td></tr>
                <tr><td><strong>🌐 Expansion Regions:</strong></td><td>{expansion}</td></tr>
                <tr><td><strong>⏱ Timeline:</strong></td><td>{timeline}</td></tr>
                <tr><td><strong>🛠 Services:</strong></td><td>{services}</td></tr>
                <tr><td><strong>➕ Add-ons:</strong></td><td>{addons}</td></tr>
                <tr><td style="color: #28a745;"><strong>💶 Total Estimated Cost:</strong></td><td style="color: #28a745;"><strong>€{total:,.2f}</strong></td></tr>
              </table>
              
              <h3 style="color: #333;">Next Steps</h3>
              <p>How does an entrepreneur move forward from here?</p>
              <ol style="padding-left: 20px;">
                <li><strong>Schedule a Consultation</strong>: Book a 15-minute call to discuss your specific requirements.</li>
                <li><strong>Receive Your Personalized Plan</strong>: We'll outline exactly which services you need based on your business model.</li>
                <li><strong>Begin Your {country} Expansion</strong>: We'll handle all the complex compliance while you focus on business growth.</li>
              </ol>
              
              <p><strong>Call to Action</strong>: {lead_phase_cta}</p>
              
              <div style="margin-top: 30px;">
                <p><strong>Contact Information</strong></p>
                <p>Best regards,<br>
                   {agent_name}<br>
                   {agent_position}<br>
                   House of Companies<br>
                   Tel: {agent_phone}<br>
                   Email: <a href="mailto:{agent_email}">{agent_email}</a><br>
                   Website: <a href="https://www.houseofcompanies.io">www.houseofcompanies.io</a>
                </p>
              </div>
              
              <p style="font-size: 12px; color: #888; border-top: 1px solid #ddd; margin-top: 30px; padding-top: 10px;">
                This message was generated by House of Companies. If you didn't request this, please ignore.
              </p>
            </div>
          </body>
        </html>
        """

        # Create email message
        msg = MIMEMultipart("alternative")
        msg['Subject'] = f"Your {country} Business Expansion: Compliance-to-Scale Solutions"
        msg['From'] = email_address
        msg['To'] = email
        msg.attach(MIMEText(html, "html"))

        # Send email
        server = None
        try:
            if smtp_port == 587:
                # Use STARTTLS
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
            else:
                # Use SSL (port 465)
                server = smtplib.SMTP_SSL(smtp_host, smtp_port)
            
            server.login(email_address, email_password)
            server.send_message(msg)
            logger.info(f"Email sent successfully to {email}")
            return jsonify({'status': 'success', 'message': 'Email sent successfully'})

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed for {email}: {str(e)}")
            return jsonify({'status': 'error', 'error': 'Email authentication failed'}), 500
        except smtplib.SMTPRecipientsRefused as e:
            logger.error(f"Invalid recipient {email}: {str(e)}")
            return jsonify({'status': 'error', 'error': 'Invalid recipient email'}), 400
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error for {email}: {str(e)}")
            return jsonify({'status': 'error', 'error': 'Email service error'}), 500
        except Exception as e:
            logger.error(f"Unexpected error sending email to {email}: {str(e)}")
            return jsonify({'status': 'error', 'error': 'Failed to send email'}), 500
        finally:
            if server:
                try:
                    server.quit()
                except:
                    pass

    except Exception as e:
        logger.error(f"Unexpected error in send_email endpoint: {str(e)}")
        return jsonify({'status': 'error', 'error': 'Internal server error'}), 500

@app.route('/')
def health():
    return jsonify({'status': 'healthy', 'message': 'Backend is alive!'})

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'House of Companies Email Service',
        'timestamp': logging.Formatter().formatTime(logging.LogRecord('', 0, '', 0, '', (), None))
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'status': 'error', 'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'status': 'error', 'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'status': 'error', 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    serve(app, host='0.0.0.0', port=port)
    
