#!/bin/bash
echo "==================================================="
echo "🎓 Setting up College Data Agent (Mac/Linux)..."
echo "==================================================="

echo ""
echo "1. Installing Python Dependencies..."
pip3 install -r requirements.txt

echo ""
echo "2. Setting up Qdrant Database (Docker)..."
docker pull qdrant/qdrant
# Note: $(pwd) gets the current directory on Mac
docker run -d -p 6333:6333 -v "$(pwd)/qdrant_storage":/qdrant/storage --name local_qdrant qdrant/qdrant

echo ""
echo "3. Verifying Setup..."
python3 -c "import qdrant_client; print('✅ Qdrant Client Ready')"
python3 -c "import sentence_transformers; print('✅ AI Models Ready')"

echo ""
echo "4. Populating Database from your data..."
python3 restore_data.py

echo ""
echo "==================================================="
echo "🎉 Setup Complete!"
echo ""
echo "To search for a college, run:"
echo "   ./get_college.sh \"College Name\""
echo "==================================================="
