# Quick Start Guide

Get X-Ray up and running in 3 steps!

## Step 1: Install Dependencies

### Backend
```bash
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
cd ..
```

## Step 2: Start Services

### Terminal 1 - Backend
```bash
python run_backend.py
```
Backend runs on `http://localhost:8000`

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:3000`

## Step 3: Run Example

### Terminal 3 - Example Code
```bash
python examples/example_usage.py
```

## View Results

Open your browser to `http://localhost:3000` and you should see:
- The execution "candidate_ranking_run" in the list
- Click it to see the detailed timeline
- Explore the 4 steps: Keyword Generation, Candidate Fetch, Filter, and Ranking
- View evaluations, inputs, outputs, and rules

## Next Steps

1. Integrate the SDK into your own code:
   ```python
   from sdk.xray import XRay
   
   xray = XRay("my_execution")
   xray.start_execution()
   # ... your code ...
   ```

2. Customize the UI by editing components in `frontend/src/components/`

3. Replace in-memory storage with a database in `backend/storage.py`

Happy debugging! 🚀

