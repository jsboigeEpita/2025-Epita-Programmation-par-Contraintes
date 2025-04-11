(cd frontend/ ; npm install ; npm run build)
(cd backend/ ; mvn clean install -DskipTests)
docker compose build
docker compose up