@echo off
echo ===================================================
echo 🎓 Setting up College Data Agent...
echo ===================================================

echo.
echo 1. Installing Python Dependencies...
pip install -r requirements.txt

echo.
echo 2. Setting up Qdrant Database (Docker)...
docker pull qdrant/qdrant
docker run -d -p 6333:6333 -v "%~dp0qdrant_storage":/qdrant/storage --name local_qdrant qdrant/qdrant

echo.
echo 3. Verifying Setup...
python -c "import qdrant_client; print('✅ Qdrant Client Ready')"
python -c "import sentence_transformers; print('✅ AI Models Ready')"

echo.
echo ===================================================
echo 🎉 Setup Complete! 
echo.
echo To search for a college, run:
echo    .\get_college "College Name"
echo ===================================================
pause
