Write a plain JavaScript module (no framework or external dependencies) that runs in the browser. It should manage user session lifecycle using the following behavior:

On Page Load:
  • Automatically send a POST request to the endpoint / _session/start including browser cookies.
  • The response will contain a CSRF token and a tracking ID that should be stored in-memory for later use.

Heartbeat:
  • Every 5 minutes, send a POST request to / _session/heartbeat using the same cookies and previously received CSRF token and tracking ID.

On Browser Close (Last Tab Only):
  • Detect if the user is closing the last open tab of the browser session.
  • If true, send a POST request to / _session/stop.
  • Also delete the related session cookies.

Cross-Platform:
  • The implementation must work reliably on both desktop and mobile browsers.

Additional Notes:
• Use modern JavaScript (ES6+).
• Ensure error handling for all network requests.
• Avoid use of global variables.
• Use only native browser APIs.
