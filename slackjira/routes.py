from slackjira import app
from flask import Flask, request, jsonify
import logging
import json
import sys
import os
import requests

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Output logs to stdout for Render
)

@app.route('/slack/events', methods=['POST'])
def handle_slack_event():
    data = request.json
    
    # Log the full incoming request data for debugging
    logging.info("Received event: %s", json.dumps(data, indent=4))
    
    # Handle Slack's challenge request (used for verifying the endpoint)
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    # Handle message events
    if 'event' in data:
        event = data['event']
        
        # Handle regular message events
        if event.get('type') == 'message' and 'subtype' not in event:
            # Extract message text and other details
            message_text = event.get('text')
            user_id = event.get('user')
            channel_id = event.get('channel')

            # Check for attachments (files) in the message event
            if 'files' in event:
                files = event['files']
                file_info = []
                
                for file in files:
                    # Log and extract necessary file details (e.g., download URL, file type)
                    file_info.append({
                        "name": file.get('name'),
                        "filetype": file.get('filetype'),
                        "url_private": file.get('url_private')
                    })
                
                # Log file information
                logging.info(f"Files attached: {json.dumps(file_info, indent=4)}")

                # Optionally: Download the file(s) using the `url_private` (requires authorization)
                for file in file_info:
                    download_file_from_slack(file['url_private'])
            
            # Create a response dictionary
            response = {
                'user': user_id,
                'channel': channel_id,
                'message': message_text,
                'files': file_info if 'files' in event else None
            }
            
            logging.info("Response: %s", json.dumps(response, indent=4))
            return jsonify(response), 200
        
        # Handle file_shared events
        if event.get('type') == 'file_shared':
            file_id = event['file_id']
            logging.info(f"File shared with ID: {file_id}")
            # Fetch file details or process as needed
    
    logging.error("Invalid event received or missing fields")
    return jsonify({"error": "No valid event"}), 400

def download_file_from_slack(file_url):
    """Download the file from Slack using the private URL."""
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    response = requests.get(file_url, headers=headers)
    
    if response.status_code == 200:
        # Save or process the file here
        logging.info(f"File downloaded: {file_url}")
    else:
        logging.error(f"Failed to download file: {file_url}")