# GitHub Pages Deployment Guide

This guide explains how to deploy the Fraud Evasion Assessor frontend demo to GitHub Pages.

## Overview

The project includes two deployment options:
1. **Frontend Demo** (this guide) - Static HTML/CSS/JS deployed to GitHub Pages
2. **Backend** - Production Flask app (requires separate hosting)

---

## Method 1: Automated Deployment (Recommended)

### Prerequisites
1. GitHub account
2. Repository with GitHub Actions enabled

### Steps

1. **Push to Main Branch**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Navigate to **Settings** > **Pages**
   - Under "Build and deployment":
     - Source: Select **Deploy from a branch**
     - Branch: Select **gh-pages** (or main, if using workflow)
   - Click **Save**

3. **The Workflow Will:**
   - Trigger on push to main branch
   - Upload the `docs/` directory as an artifact
   - Deploy to GitHub Pages

4. **Access Your Demo**
   - Navigate to: `https://[username].github.io/[repository-name]/`
   - Example: `https://marcocasanova.github.io/fraud-evasion-assessor/`

---

## Method 2: Manual Deployment

### Steps

1. **Create gh-pages Branch**
   ```bash
   git checkout -b gh-pages
   ```

2. **Copy Frontend Files**
   ```bash
   cp -r docs/* .
   ```

3. **Commit and Push**
   ```bash
   git add .
   git commit -m "Deploy frontend demo"
   git push origin gh-pages
   ```

4. **Enable Pages**
   - Go to **Settings** > **Pages**
   - Source: Select **gh-pages branch**
   - Click **Save**

---

## Method 3: Using GitHub Actions (Manual Trigger)

### Triggering the Workflow

1. Go to your repository on GitHub
2. Navigate to **Actions** tab
3. Select **"Deploy GitHub Pages"** workflow
4. Click **"Run workflow"** dropdown
5. Click **"Run workflow"** button

The workflow will deploy the `docs/` directory to GitHub Pages.

---

## Local Preview

Before deploying, you can preview locally:

### Option 1: Direct File Access
```bash
# Open in browser
# file:///path/to/fraud-evasion-assessor/docs/index.html
```

### Option 2: Local HTTP Server
```bash
# Using Python
cd docs
python -m http.server 8000

# Then visit: http://localhost:8000
```

### Option 3: VS Code Live Server
1. Install "Live Server" extension in VS Code
2. Right-click on `docs/index.html`
3. Select "Open with Live Server"

---

## Project Structure for Deployment

```
fraud-evasion-assessor/
├── docs/                    # <- This is deployed to GitHub Pages
│   ├── index.html          # Main page
│   ├── SECURITY.md         # Security documentation
│   └── assets/
│       ├── css/
│       ├── js/
│       ├── img/
│       └── data/
├── backend/                # Not deployed (requires Python server)
├── frontend-demo/          # Source files
├── shared/                 # Shared configuration (not deployed)
└── scripts/                # Build scripts (not deployed)
```

---

## Custom Domain Setup (Optional)

1. **Purchase a Domain** (e.g., `fraud-assessor.example.com`)

2. **Configure DNS**
   - Add A record: `@ -> 185.199.108.153`
   - Add A record: `@ -> 185.199.109.153`
   - Add A record: `@ -> 185.199.110.153`
   - Add A record: `@ -> 185.199.111.153`
   - Add CNAME: `www -> [username].github.io`

3. **Configure GitHub Pages**
   - Go to **Settings** > **Pages**
   - Custom domain: Enter your domain
   - Enable **HTTPS** (required for CSP)

4. **Wait for DNS Propagation** (up to 48 hours)

---

## Troubleshooting

### Page Not Found (404)
- Ensure the file is named `index.html` (lowercase)
- Check the branch selection in Settings > Pages
- Verify the file path: `docs/index.html` (not `docs/docs/index.html`)

### CSS/JS Not Loading
- Check browser console for 404 errors
- Ensure paths in `index.html` are relative (no leading `/`)
- Verify file structure in the deployed branch

### HTTPS Errors
- GitHub Pages provides free HTTPS for custom domains
- Wait a few minutes after enabling HTTPS
- Clear browser cache if certificates don't load

### Workflow Not Running
- Check **Actions** tab for errors
- Verify workflow file exists at `.github/workflows/pages.yml`
- Ensure GitHub Actions is enabled in repository settings

---

## CI/CD Workflow

The project includes an automated workflow (`.github/workflows/pages.yml`):

```yaml
on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'docs/'
      - name: Deploy
        uses: actions/deploy-pages@v4
```

This workflow:
- Triggers on every push to `main`
- Uploads the `docs/` folder as a deployment artifact
- Deploys to GitHub Pages

---

## Environment Variables for CI/CD

No environment variables are required for the frontend demo since it runs entirely client-side.

---

## Next Steps

1. **Deploy Backend** (Optional)
   - Backend requires Python hosting (Heroku, Railway, etc.)
   - See `backend/README.md` for deployment options

2. **Customize Content**
   - Edit `docs/index.html` for branding
   - Modify `docs/assets/js/demo.js` for custom scoring logic

3. **Add Analytics** (Optional)
   - Add Google Analytics to `docs/index.html`
   - Track page views and user interactions

---

## Support

For issues with deployment, check:
1. GitHub Actions logs in the **Actions** tab
2. Browser console for resource loading errors
3. Repository **Settings** > **Pages** configuration

---

**Last Updated:** May 2026
**Version:** 2.0