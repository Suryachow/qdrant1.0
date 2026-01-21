HOW TO RUN THIS COLLEGE AGENT
===================================================

PREREQUISITES:
1. Python installed (Add to Path checked during installation).
2. Docker Desktop installed and running.

---------------------------------------------------
STEP 1: SETUP (DO THIS ONCE)
---------------------------------------------------
Double-click on "setup_for_friend.bat".
- It will install all necessary libraries.
- It will download and start the Qdrant database.

---------------------------------------------------
STEP 2: HOW TO USE
---------------------------------------------------
To find or add a college, just double-click "get_college.bat" 
(or run it from command line like: .\get_college "IIT Bombay")

---------------------------------------------------
FILES EXPLAINED:
- main.py: The brain of the agent.
- qdrant_db/: Database logic.
- scraper/: Web scraper logic.
- data.json: Local backup of data.
===================================================
