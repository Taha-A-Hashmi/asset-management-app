# Asset Management Application

A modern asset management system built with React and Flask, deployed as a monorepo on Vercel.

## Tech Stack

**Frontend:**

- React 18
- Vite (build tool)
- Tailwind CSS (styling)
- React Router v6 (routing)
- react-hot-toast (notifications)
- Chart.js + react-chartjs-2 (data visualization)
- Axios (HTTP client)

**Backend:**

- Flask 3.0.0 (Python web framework)
- MongoDB (database)
- Flask-CORS (CORS support)

## Project Structure

````
asset-management-app/
├── api/                    # Flask REST API
│   ├── __init__.py
│   └── app.py             # API routes and logic
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page components (Dashboard, Settings, etc.)
│   │   ├── services/      # API service layer
│   │   ├── App.jsx        # Router configuration
│   │   └── main.jsx       # Entry point
│   ├── package.json
│   ├── vite.config.js     # Vite configuration
│   └── tailwind.config.js # Tailwind CSS configuration
├── .env                   # Environment variables (not in git)
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── vercel.json           # Vercel deployment configuration

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (or local MongoDB)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd asset-management-app
````

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your MongoDB connection string:

   ```
   MONGO_URI=your_mongodb_connection_string
   MONGO_DB_NAME=hospital_crm_db
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Node dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

You need to run **two terminals simultaneously**:

**Terminal 1 - Flask API (Backend):**

```bash
$env:FLASK_ENV="development"
python api/app.py
```

The API will run on `http://localhost:5000`

**Terminal 2 - React Dev Server (Frontend):**

```bash
cd frontend
npm run dev
```

The React app will run on `http://localhost:5173`

Open your browser to `http://localhost:5173` to see the application.

The Vite dev server automatically proxies API calls from `/api/*` to `http://localhost:5000/api/*`.

## Features

- **Dashboard**: View asset statistics and inventory
- **Add Assets**: Create new assets with description and serial number
- **Check-in/Check-out**: Track asset location and status
- **Delete Assets**: Remove assets with confirmation
- **Real-time Charts**: Visualize asset distribution (In Stock vs On Demo)
- **Toast Notifications**: User feedback for all actions
- **Responsive Design**: Works on desktop and mobile
- **Client-side Routing**: Fast navigation with React Router

## API Endpoints

- `GET /api/assets` - Get all assets with statistics
- `POST /api/assets` - Create a new asset
- `PUT /api/assets/<id>` - Update asset status/location
- `DELETE /api/assets/<id>` - Delete an asset

## Deployment to Vercel

### Prerequisites

- Vercel account
- GitHub repository (optional but recommended)

### Steps

1. **Push your code to GitHub** (recommended)

2. **Import project to Vercel**

   - Go to https://vercel.com
   - Click "Add New Project"
   - Import your GitHub repository

3. **Configure Environment Variables**

   - In Vercel dashboard, go to Project Settings → Environment Variables
   - Add the following:
     - `MONGO_URI`: Your MongoDB connection string
     - `MONGO_DB_NAME`: `hospital_crm_db`

4. **Deploy**

   - Vercel will automatically build and deploy your application
   - Build command: `cd frontend && npm install && npm run build`
   - Output directory: `frontend/dist`

5. **Test your deployment**
   - Visit your Vercel URL (e.g., `https://your-app.vercel.app`)
   - All routes should work, including direct URL access and refresh

## Build for Production

```bash
cd frontend
npm run build
```

The production build will be output to `frontend/dist/`.

## Future Enhancements

- **Settings Page**: User preferences, configurations
- **Reports Page**: Advanced analytics and reports
- **Asset Detail Pages**: Individual asset history and details
- **User Authentication**: Multi-user support with login
- **Audit Log**: Track all changes to assets
- **Export Data**: Export assets to CSV/Excel
- **Search & Filter**: Advanced search and filtering capabilities

## Troubleshooting

### MongoDB Connection Issues

- Ensure your MongoDB URI is correct in `.env`
- Check that your IP address is whitelisted in MongoDB Atlas
- Verify network connectivity

### CORS Errors in Development

- Make sure both servers are running
- Verify Vite proxy configuration in `vite.config.js`
- Check that `FLASK_ENV=development` is set for Flask

### Module Not Found Errors

- Frontend: Run `cd frontend && npm install`
- Backend: Run `pip install -r requirements.txt`

### Port Already in Use

- Backend: Change port in `api/app.py` (line: `app.run(debug=True, port=5000)`)
- Frontend: Change port in `vite.config.js` (server.port)
