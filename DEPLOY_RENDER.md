# Deploying ER Flow Dashboard to Render.com

This guide will walk you through deploying your Hospital Patient Flow Dashboard to Render.com.

## Prerequisites

1. A [Render.com](https://render.com) account (free tier works fine)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Git installed on your computer

## Step 1: Push Your Code to GitHub

If you haven't already, push your code to GitHub:

```bash
cd c:\Users\beren\Desktop\hospital_flow

# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - ER Flow Dashboard"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/hospital-flow.git
git push -u origin main
```

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended - Infrastructure as Code)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com
   - Click "New +" → "Blueprint"

2. **Connect Your Repository**
   - Select "Connect a repository"
   - Authorize Render to access your GitHub account
   - Select your `hospital-flow` repository

3. **Configure Blueprint**
   - Render will automatically detect the `render.yaml` file
   - Review the configuration:
     - Service name: `hospital-flow`
     - Runtime: Python 3.11
     - Build command: `pip install -r backend/requirements.txt`
     - Start command: `cd backend && python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT`

4. **Click "Apply"**
   - Render will start building and deploying your application
   - This usually takes 2-5 minutes

5. **Get Your URL**
   - Once deployed, you'll get a URL like: `https://hospital-flow.onrender.com`
   - Your dashboard will be accessible at this URL!

### Option B: Manual Setup (Alternative)

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect Repository**
   - Select your `hospital-flow` repository

3. **Configure Service**
   - **Name**: `hospital-flow`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn main:socket_app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

4. **Environment Variables** (Optional)
   - Click "Advanced" → "Add Environment Variable"
   - Add `DEMO_MODE` = `true` (if you want demo data on startup)

5. **Click "Create Web Service"**

## Step 3: Verify Deployment

1. **Check Build Logs**
   - Watch the deploy logs in real-time
   - Look for "Application startup complete"

2. **Test Your Application**
   - Visit your Render URL (e.g., `https://hospital-flow.onrender.com`)
   - You should see the ER Triage & Bed Assignment dashboard
   - Try registering a patient
   - Test bed assignment features

## Architecture

Your deployment includes:

- **Backend API** (FastAPI + Socket.IO): Handles REST API endpoints and WebSocket connections
- **Frontend** (Static HTML/CSS/JS): Served directly from the backend
- **Database** (SQLite): Stored in-memory (resets on each deploy in free tier)
- **Demo Data**: Automatically created on startup if DEMO_MODE is enabled

## Important Notes

### Free Tier Limitations

- **Cold Starts**: Free tier spins down after 15 minutes of inactivity. First request after inactivity may take 30-60 seconds.
- **Data Persistence**: SQLite database is stored in ephemeral storage and **will reset** on each deploy or restart.
- **For Production**: Consider upgrading to a paid plan and using PostgreSQL for persistent data.

### Upgrading to Persistent Storage (Optional)

To add persistent database storage:

1. **Create a PostgreSQL Database**
   - In Render dashboard: "New +" → "PostgreSQL"
   - Choose a name and plan

2. **Update Your Code**
   - Replace SQLite with PostgreSQL using SQLAlchemy
   - Update connection string to use `DATABASE_URL` environment variable

3. **Add Environment Variable**
   - In your web service settings, add the PostgreSQL connection URL

## Updating Your Deployment

To push updates:

```bash
# Make your changes locally
git add .
git commit -m "Description of changes"
git push origin main
```

Render will automatically detect the push and redeploy your application.

## Troubleshooting

### Build Fails

**Problem**: Build fails with "pip: command not found" or similar
**Solution**: Check that `requirements.txt` is in the `backend` folder

### Application Won't Start

**Problem**: Application starts but shows errors
**Solution**:
1. Check the logs in Render dashboard
2. Verify environment variables are set correctly
3. Make sure `main.py` is in the `backend` folder

### Frontend Not Loading

**Problem**: API works but frontend shows 404
**Solution**:
1. Verify `frontend` folder exists at project root
2. Check that static files are being mounted in `main.py`

### WebSocket Connection Fails

**Problem**: Real-time updates don't work
**Solution**:
1. Render supports WebSockets on all plans
2. Check browser console for connection errors
3. Verify Socket.IO client is loading (check for `socket.io.min.js` in Network tab)

## Custom Domain (Optional)

To use your own domain:

1. Go to your service settings in Render
2. Click "Custom Domains"
3. Add your domain and follow DNS configuration instructions

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com

## Next Steps

- Set up monitoring and alerts in Render dashboard
- Configure environment-specific settings
- Set up automatic backups for production data
- Consider adding authentication for production use

---

**Your Dashboard is Live!** 🎉

Visit your Render URL to see your ER Flow Dashboard in action.
