# Building, deploying, and testing apps on IBM Cloud (with watsonx Code Assistant, Code Engine, and Feature Flags)

> **Tutorial goal:** Build a tiny Gen Z-friendly app, deploy it to **IBM Cloud Code Engine**, and test it with **two feature flags** using **IBM Cloud App Configuration (Feature Flags)**.

## What you'll build

You will create and deploy a tiny Flask app called **Vibe Check API**:

- `GET /` → app status
- `GET /vibe` → returns a witty message
- `GET /roast` → returns a playful roast (**feature-flagged**)

Two feature flags control behavior:

1. `enable_daily_roast` – enables/disables the `/roast` endpoint.
2. `enable_chaos_mode` – makes `/vibe` extra chaotic and random.

You will also use **watsonx Code Assistant** to speed up coding, tests, and refactoring.

---

## Architecture

- **watsonx Code Assistant**: helps generate/modernize code, add tests, and improve docs.
- **IBM Cloud App Configuration**: hosts feature flags.
- **Flask app**: fetches flags and changes runtime behavior.
- **IBM Cloud Code Engine**: container build + deployment + routing.

---

## Prerequisites

- IBM Cloud account with access to:
  - watsonx Code Assistant
  - Code Engine
  - App Configuration (Feature Flags)
- Local tools:
  - [IBM Cloud CLI](https://cloud.ibm.com/docs/cli)
  - Docker (optional for local container build)
  - Python 3.11+
  - Git

---

## Step 1: Set up IBM Cloud service instances

### 1.1 Log in and target your account

```bash
ibmcloud login --sso
ibmcloud target -r us-south
```

> Use your preferred region if different.

### 1.2 Create a resource group (optional but recommended)

```bash
ibmcloud resource group-create rg-vibe-tutorial
ibmcloud target -g rg-vibe-tutorial
```

### 1.3 Create (or verify) service instances

#### watsonx Code Assistant
Create it from the IBM Cloud catalog in the console if your account does not already have one.

#### App Configuration (Feature Flags)

```bash
ibmcloud resource service-instance-create vibe-appconfig app-configuration lite us-south
ibmcloud resource service-key-create vibe-appconfig-key Manager --instance-name vibe-appconfig
ibmcloud resource service-key vibe-appconfig-key
```

Capture these values from the credentials JSON:

- `guid` (App Configuration GUID)
- `apprapp_url` or endpoint URL (region-dependent)
- `apikey`

Then in App Configuration dashboard:

1. Create an environment (for example: `dev`).
2. Create two feature flags:
   - `enable_daily_roast` (default: `false`)
   - `enable_chaos_mode` (default: `false`)

#### Code Engine project

```bash
ibmcloud plugin install code-engine -f
ibmcloud ce project create --name vibe-ce-project
ibmcloud ce project select --name vibe-ce-project
```

---

## Step 2: Download code and configure credentials

### 2.1 Clone this repository

```bash
git clone <your-repo-url>
cd Apps-on-IBM-Cloud
```

### 2.2 Create local environment file

```bash
cp .env.example .env
```

Update `.env`:

```dotenv
PORT=8080
APP_NAME=VibeCheckAPI

# App Configuration credentials
APP_CONFIG_URL=<your_app_config_endpoint>
APP_CONFIG_GUID=<your_app_config_guid>
APP_CONFIG_APIKEY=<your_iam_apikey>
APP_CONFIG_ENVIRONMENT_ID=<your_environment_id>

# Fallback local flags (used if remote fetch fails)
FLAG_ENABLE_DAILY_ROAST=false
FLAG_ENABLE_CHAOS_MODE=false
```

> Tip: You can get `APP_CONFIG_ENVIRONMENT_ID` from the App Configuration environment settings.

### 2.3 Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Test endpoints:

```bash
curl http://localhost:8080/
curl http://localhost:8080/vibe
curl http://localhost:8080/roast
```

If `enable_daily_roast` is `false`, `/roast` returns 404 with a feature-disabled message.

### 2.4 Use watsonx Code Assistant during development

In VS Code or JetBrains with the watsonx extension enabled, try prompts like:

- “Generate pytest tests for `feature_flags.py`, including fallback behavior when API fails.”
- “Refactor `app.py` to improve endpoint readability but keep API behavior unchanged.”
- “Add docstrings and type hints to all functions.”

This is where watsonx Code Assistant accelerates your build phase.

---

## Step 3: End-to-end execution, deployment, and demo

### 3.1 Deploy to Code Engine from source

From repo root:

```bash
ibmcloud ce application create \
  --name vibe-check-api \
  --build-source . \
  --port 8080 \
  --cpu 0.25 \
  --memory 0.5G \
  --env-from-file .env
```

Get app URL:

```bash
ibmcloud ce application get --name vibe-check-api
```

Copy the URL output (for example `https://vibe-check-api.<hash>.us-south.codeengine.appdomain.cloud`).

### 3.2 Demo flow: test flags live

Assume:

```bash
export APP_URL=https://<your-ce-app-url>
```

#### Baseline (both flags false)

```bash
curl "$APP_URL/vibe"
curl -i "$APP_URL/roast"
```

Expected:

- `/vibe` returns normal witty response.
- `/roast` is disabled (404).

#### Toggle `enable_daily_roast=true`

In App Configuration UI:

1. Open `enable_daily_roast`
2. Enable for `dev`
3. Save/publish changes

Re-test:

```bash
curl "$APP_URL/roast"
```

Expected: roast endpoint now returns a playful roast message.

#### Toggle `enable_chaos_mode=true`

In App Configuration UI:

1. Open `enable_chaos_mode`
2. Enable for `dev`
3. Save/publish changes

Re-test multiple times:

```bash
for i in {1..5}; do curl "$APP_URL/vibe"; echo; done
```

Expected: increasingly chaotic/funny responses.

---

## Cleanup

```bash
ibmcloud ce application delete --name vibe-check-api -f
ibmcloud ce project delete --name vibe-ce-project -f
ibmcloud resource service-instance-delete vibe-appconfig -f
```

---

## Troubleshooting

- **App always uses fallback flags**
  - Verify `APP_CONFIG_URL`, `APP_CONFIG_GUID`, `APP_CONFIG_APIKEY`, and `APP_CONFIG_ENVIRONMENT_ID`.
  - Check app logs in Code Engine:
    ```bash
    ibmcloud ce application logs --name vibe-check-api --follow
    ```
- **`/roast` still disabled after enabling flag**
  - Wait for config propagation and retry.
  - Confirm correct environment in App Configuration.
- **Build fails on Code Engine**
  - Ensure `requirements.txt` and `Dockerfile` are in repo root.

---

## Why this pattern works

- **Fast build loop** with watsonx Code Assistant.
- **Safe progressive delivery** with feature flags.
- **Simple serverless deployment** via Code Engine.

Your app ships faster, with less chaos in production (unless you intentionally turn on `enable_chaos_mode`, then chaos is the product 😉).
