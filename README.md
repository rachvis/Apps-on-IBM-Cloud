# Building, deploying, and testing apps on IBM Cloud

A developer.ibm.com-style tutorial to build a tiny, funny Gen Z app with:

- **watsonx Code Assistant** for faster coding
- **IBM Cloud Code Engine** for deployment
- **IBM Cloud App Configuration feature flags** for controlled testing

App name: **Vibe & Roast Studio**

- `/api/vibe` returns a random vibe line from a set of 10.
- `/api/roast` returns a random roast line from a set of 10.
- `/` shows a pretty UI with cards that are conditionally visible by feature flags.

## Step 1 — Set up IBM Cloud service instances

### 1.1 Log in and set region/resource group

```bash
ibmcloud login --sso
ibmcloud target -r us-south
ibmcloud resource group-create rg-vibe-roast
ibmcloud target -g rg-vibe-roast
```

### 1.2 Provision watsonx Code Assistant

Create or verify a watsonx Code Assistant instance in IBM Cloud catalog.

### 1.3 Provision App Configuration and create flags

```bash
ibmcloud resource service-instance-create vibe-appconfig app-configuration lite us-south
ibmcloud resource service-key-create vibe-appconfig-key Manager --instance-name vibe-appconfig
ibmcloud resource service-key vibe-appconfig-key
```

From service key JSON, copy:

- `guid`
- `apprapp_url`
- `apikey`

In App Configuration UI:

1. Create environment `dev`
2. Create two Boolean flags:
   - `show_vibe`
   - `show_roast`

### 1.4 Create Code Engine project

```bash
ibmcloud plugin install code-engine -f
ibmcloud ce project create --name vibe-ce-project
ibmcloud ce project select --name vibe-ce-project
```

## Step 2 — Download code and configure credentials

### 2.1 Clone repo

```bash
git clone <your-repo-url>
cd Apps-on-IBM-Cloud
```

### 2.2 Configure environment

```bash
cp .env.example .env
```

Set values in `.env`:

```dotenv
PORT=8080
APP_NAME=VibeCheckAPI
APP_CONFIG_URL=<your_app_config_endpoint>
APP_CONFIG_GUID=<your_app_config_guid>
APP_CONFIG_APIKEY=<your_iam_apikey>
APP_CONFIG_ENVIRONMENT_ID=<your_environment_id>
FLAG_SHOW_VIBE=true
FLAG_SHOW_ROAST=false
```

### 2.3 Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

- UI: `http://localhost:8080/`
- APIs: `http://localhost:8080/api/vibe`, `http://localhost:8080/api/roast`

### 2.4 Use watsonx Code Assistant while building

Prompt examples:

- “Generate tests for Flask endpoints with feature-flag scenarios.”
- “Refactor message selection for readability without changing API contract.”
- “Improve HTML/CSS accessibility and responsiveness for this UI.”

## Step 3 — End-to-end flow execution and demo

### 3.1 Deploy on Code Engine

```bash
ibmcloud ce application create \
  --name vibe-roast-studio \
  --build-source . \
  --port 8080 \
  --cpu 0.25 \
  --memory 0.5G \
  --env-from-file .env
```

Get URL:

```bash
ibmcloud ce application get --name vibe-roast-studio
```

### 3.2 Demo: feature flags drive UI visibility

Set app URL:

```bash
export APP_URL=https://<your-ce-url>
```

#### Case A: `show_vibe=true`, `show_roast=false`

- UI should display Vibe card.
- UI should hide Roast card.
- `/api/roast` returns a friendly “flag is off” message (not 404).

```bash
curl "$APP_URL/api/vibe"
curl "$APP_URL/api/roast"
```

#### Case B: `show_vibe=true`, `show_roast=true`

Enable both flags in App Configuration, then refresh UI.

- Both cards become visible.
- Every refresh shows a different random line for vibe/roast from lists of 10 messages each.

```bash
for i in {1..5}; do curl "$APP_URL/api/vibe"; echo; done
for i in {1..5}; do curl "$APP_URL/api/roast"; echo; done
```

## Cleanup

```bash
ibmcloud ce application delete --name vibe-roast-studio -f
ibmcloud ce project delete --name vibe-ce-project -f
ibmcloud resource service-instance-delete vibe-appconfig -f
```
