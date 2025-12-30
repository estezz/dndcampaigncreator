aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 802379732270.dkr.ecr.us-east-2.amazonaws.com

docker build -t dnd .

docker tag dnd:latest 802379732270.dkr.ecr.us-east-2.amazonaws.com/dnd:latest

docker push 802379732270.dkr.ecr.us-east-2.amazonaws.com/dnd:latest
