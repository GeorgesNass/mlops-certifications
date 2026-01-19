echo "--------------------------------------------"
echo " Building Docker images"
echo "--------------------------------------------"
docker-compose build

echo ""
echo ""

echo "--------------------------------------------"
echo " Running tests"
echo "--------------------------------------------"
docker-compose up --abort-on-container-exit

echo ""
echo ""

echo "--------------------------------------------"
echo " Copying logs"
echo "--------------------------------------------"

## On creer les logs si ils n'existent pas
mkdir -p logs

## Copier les logs generes vers un log propre
cp logs/api_test.log log.txt

echo ""
echo ""
echo "--------------------------------------------"
echo " Logs available in log.txt"
echo "--------------------------------------------"

## Une fois que tous les tests sont effectues par les conteneurs, on les arretent
docker-compose down

