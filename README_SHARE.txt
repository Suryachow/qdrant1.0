HOW TO RUN THIS COLLEGE AGENT
===================================================

PREREQUISITES:
1. Python installed (Add to Path checked during installation).
2. Docker Desktop installed and running.

---------------------------------------------------
STEP 1: SETUP (DO THIS ONCE)
---------------------------------------------------
WINDOWS:
Double-click "setup_for_friend.bat".

MAC / LINUX:
Open Terminal, navigate to the folder, and run:
   sh setup_for_friend.sh

---------------------------------------------------
STEP 2: HOW TO USE
---------------------------------------------------
WINDOWS:
Double-click "get_college.bat" 
(or run: .\get_college "College Name")

MAC / LINUX:
Run:
   sh get_college.sh "College Name"

---------------------------------------------------
FILES EXPLAINED:
- main.py: The brain of the agent.
- qdrant_db/: Database logic.
- scraper/: Web scraper logic.
- data.json: Local backup of data.
===================================================
