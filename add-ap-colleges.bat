@echo off
echo ========================================
echo  Adding Andhra Pradesh Colleges
echo ========================================
echo.
echo This will scrape and add 10 AP colleges to your database.
echo Each college will be:
echo   1. Scraped from their website
echo   2. Structured using AI (Groq)
echo   3. Saved to data.json
echo   4. Indexed to Qdrant
echo.
echo Press Ctrl+C to cancel, or
pause

python add_ap_colleges.py

echo.
echo ========================================
echo Done! Check your Qdrant dashboard:
echo http://localhost:6333/dashboard
echo ========================================
pause
