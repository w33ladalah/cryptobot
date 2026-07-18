---
description: How to run frontend E2E tests using Chrome DevTools MCP server
---

# Frontend E2E Testing with Chrome DevTools MCP

## Setup (one-time)

- **Ensure frontend dev server is running**:

```bash
cd frontend
npm run dev
```

- **No additional installation needed** - Chrome DevTools MCP server is already available in your environment

## Login Test Pattern

Use Chrome DevTools MCP tools to perform login:

- **Navigate to the application**:

```bash
mcp0_navigate_page
url: "http://localhost:3000"
```

- **Take a snapshot to see current state**:

```bash
mcp0_take_snapshot
```

- **Click on login/auth button** (find uid from snapshot):

```bash
mcp0_click
uid: "<button-uid-from-snapshot>"
```

- **Fill email field**:

```bash
mcp0_fill
uid: "<email-input-uid>"
value: "hendrothemail@gmail.com"
```

- **Fill password field**:

```bash
mcp0_fill
uid: "<password-input-uid>"
value: "qw3rtyu1"
```

- **Click sign in button**:

```bash
mcp0_click
uid: "<sign-in-button-uid>"
```

- **Verify login success**:

```bash
mcp0_take_snapshot
# Check for user menu/profile button in the snapshot
```

## Testing Features and Pages

After login, use Chrome DevTools MCP tools to test specific features:

### Navigate to a page

```bash
mcp0_navigate_page
url: "http://localhost:3000/generate"
```

### Take snapshot to verify page state

```bash
mcp0_take_snapshot
```

### Interact with elements

```bash
# Click buttons
mcp0_click
uid: "<button-uid>"

# Fill inputs
mcp0_fill
uid: "<input-uid>"
value: "test value"

# Fill forms (multiple fields at once)
mcp0_fill_form
elements:
  - uid: "<field1-uid>"
    value: "value1"
  - uid: "<field2-uid>"
    value: "value2"
```

### Take screenshots for visual verification

```bash
mcp0_take_screenshot
# Optional: specify file path
filePath: "/path/to/screenshot.png"
```

### Wait for specific text to appear

```bash
mcp0_wait_for
text: ["Success", "Completed"]
```

### Check console messages

```bash
mcp0_list_console_messages
```

### Check network requests

```bash
mcp0_list_network_requests
```

## Example Test Flow

Here's a complete example for testing the generate page:

- **Navigate to home page and login**:

```bash
mcp0_navigate_page
url: "http://localhost:3000"
```

```bash
mcp0_take_snapshot
```

```bash
mcp0_click
uid: "<login-button-uid>"
```

```bash
mcp0_fill
uid: "<email-uid>"
value: "hendrothemail@gmail.com"
```

```bash
mcp0_fill
uid: "<password-uid>"
value: "qw3rtyu1"
```

```bash
mcp0_click
uid: "<sign-in-uid>"
```

- **Navigate to generate page**:

```bash
mcp0_navigate_page
url: "http://localhost:3000/generate"
```

- **Verify page loaded**:

```bash
mcp0_take_snapshot
# Check for generate page elements in snapshot
```

- **Test generate functionality** (interact with UI elements as needed):

```bash
mcp0_click
uid: "<generate-button-uid>"
```

- **Wait for completion**:

```bash
mcp0_wait_for
text: ["Generation complete", "Success"]
```

- **Take screenshot for documentation**:

```bash
mcp0_take_screenshot
filePath: "/tmp/generate-test-result.png"
```

## Available Chrome DevTools MCP Tools

Key tools available for testing:

- `mcp0_navigate_page` - Navigate to URLs
- `mcp0_take_snapshot` - Get page structure with element UIDs
- `mcp0_click` - Click elements by UID
- `mcp0_fill` - Fill input fields
- `mcp0_fill_form` - Fill multiple form fields at once
- `mcp0_take_screenshot` - Capture screenshots
- `mcp0_wait_for` - Wait for text to appear
- `mcp0_list_console_messages` - Check console logs
- `mcp0_list_network_requests` - Inspect network activity
- `mcp0_evaluate_script` - Execute JavaScript in the page
- `mcp0_hover` - Hover over elements
- `mcp0_press_key` - Press keyboard shortcuts

## Tips

- Always take a snapshot first to find element UIDs
- Use `mcp0_wait_for` instead of arbitrary sleeps
- Take screenshots at key points for documentation
- Check console messages for errors
- Verify network requests for API calls
- Use `mcp0_evaluate_script` for complex assertions
