# Face_mongodb_project

This repository contains three files.
FINANCE_MANAGER.py is the pure backend, working version of the basic finance manager application.
It uses MongoDB to store data and uses python for calculations.
Features include calculating monthly net savings, yearly projections and generation of a monthly spending cap to avoid losses.


FinanceManager.py and main.py are part of the web application with an attempt to build a user interface using fastapi and it's swagger UI templates.


Use mongodb://localhost:27017/ to connect to MongoDB (replace 'MONGODB_URI' with this if needed)
The swaggerUI implementation can be viewed at http://localhost:8000/docs after downloading FinanceManager.py and main.py, and running the file main.py

Requirements:
Python and MongoDB to be installed along with all the necessary modules
