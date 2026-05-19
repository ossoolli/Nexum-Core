#!/bin/bash

cd /home/madarmutaz/Mutaz-dev

git pull origin main

source venv/bin/activate

pip install -r requirements.txt

pm2 restart all

echo "NEXUM UPDATED SUCCESSFULLY"
