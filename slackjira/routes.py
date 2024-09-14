from slackjira import app
from flask import Flask, request, jsonify
import logging
import json
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]  # Output logs to stdout for Render
)

@app.route('/slack/events', methods=['POST'])
def handle_slack_event():
    data = request.json
    
    # Handle Slack's challenge request (used for verifying the endpoint)
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    # Handle message events
    if 'event' in data:
        event = data['event']
        
        if event.get('type') == 'message' and 'subtype' not in event:
            # Extract message text and other details
            message_text = event.get('text')
            user_id = event.get('user')
            channel_id = event.get('channel')
            
            # Create a response dictionary
            response = {
                'user': user_id,
                'channel': channel_id,
                'message': message_text
            }
            logging.info("Response: %s", json.dumps(response, indent=4))
            return jsonify(response), 200
    
    return jsonify({"error": "No valid event"}), 400
