'''from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Verify the connection
db = client.test_database
collection = db.test_collection
print("Connected to MongoDB successfully!")


client.close()
'''

# Imports
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import os
import uvicorn

# Load environment variables from .env file
load_dotenv()

# Example: Accessing an environment variable
mongo_connection_string = os.getenv("MONGODB_URI")

#print(os.getenv("MONGODB_URI"))

if mongo_connection_string is None:
    print("Failed to load environment variables")
else:
    pass
    #print("Environment variables loaded successfully")
    # Proceed with MongoDB connection using the loaded environment variable




# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["finance_manager"]

try:
    # Attempt to list database names to check connection
    client.list_database_names()
    # If the above line doesn't raise an error, the client is connected
    pass
except Exception as e:
    # Handle the case where the client is not connected
    print("Client is not connected. Error:", e)
    

# FastAPI app
app = FastAPI()

# Models
class Income(BaseModel):
    # Income model: Represents a single income entry
    amount: float
    source: str
    date: datetime

class Expense(BaseModel):
    # Expense model: Represents a single expense entry
    amount: float
    category: str
    date: datetime

class Loan(BaseModel):
    # Loan model: Represents a loan or debt
    amount: float
    interest_rate: float
    lender: str
    start_date: datetime
    end_date: datetime

class Investment(BaseModel):
    # Investment model: Represents an investment or deposit
    amount: float
    return_rate: float
    name: str
    start_date: datetime
    end_date: Optional[datetime]

class User(BaseModel):
    # User model: Represents a user of the finance manager
    username: str
    email: str
    password: str  # In a real app, ensure this is hashed

# Database operations
class DatabaseOperations:
    @staticmethod
    def add_income(user_id: str, income: Income):
        # Add a new income entry to the database
        db.incomes.insert_one({"user_id": user_id, **income.model_dump()})

    @staticmethod
    def add_expense(user_id: str, expense: Expense):
        # Add a new expense entry to the database
        db.expenses.insert_one({"user_id": user_id, **expense.model_dump()})

    @staticmethod
    def add_loan(user_id: str, loan: Loan):
        # Add a new loan entry to the database
        db.loans.insert_one({"user_id": user_id, **loan.model_dump()})

    @staticmethod
    def add_investment(user_id: str, investment: Investment):
        # Add a new investment entry to the database
        db.investments.insert_one({"user_id": user_id, **investment.model_dump()})

    @staticmethod
    def get_monthly_income(user_id: str, month: int, year: int):
        # Retrieve total income for a specific month and year
        pipeline = [
            {
            "$match": {
                "user_id": user_id,
                "date": {
                "$gte": datetime(year, month, 1),
                "$lt": datetime(year, month + 1, 1)
                }
            }
            },
            {
            "$group": {
                "_id": None,
                "total_income": {
                "$sum": "$amount"
                }
            }
            }
        ]
        result = db.incomes.aggregate(pipeline)
        total_income = result.next()["total_income"]
        return total_income

    @staticmethod
    def get_monthly_expenses(user_id: str, month: int, year: int):
        pipeline = [
            {
            "$match": {
                "user_id": user_id,
                "date": {
                "$gte": datetime(year, month, 1),
                "$lt": datetime(year, month + 1, 1)
                }
            }
            },
            {
            "$group": {
                "_id": None,
                "total_expenses": {
                "$sum": "$amount"
                }
            }
            }
        ]
        result = db.expenses.aggregate(pipeline)
        total_expenses = result.next()["total_expenses"]
        return total_expenses

    @staticmethod
    def get_loans(user_id: str):
        # Retrieve all active loans for a user
        active_loans = db.loans.find({"user_id": user_id, "end_date": {"$gte": datetime.now()}})
        return list(active_loans)

    @staticmethod
    def get_investments(user_id: str):
        active_investments = db.investments.find({"user_id": user_id, "end_date": {"$gte": datetime.now()}})
        return list(active_investments)

# Financial calculations
class FinancialCalculations:
    @staticmethod
    def calculate_net_return(income: float, expenses: float, loan_payments: float, investment_returns: float):
        # Calculate net return: income - expenses + investment returns - loan payments
        return_rate = Investment.return_rate
        interest_rate = Loan.interest_rate
        # Replace with the actual return rate from the investment object
        return income - expenses + (investment_returns * (1 + return_rate)) - (loan_payments * (1 + interest_rate))

    @staticmethod
    def project_yearly_trend(monthly_net_return: float):
        # Project yearly trend based on current monthly net return
        return monthly_net_return * 12

    @staticmethod
    def calculate_min_profit_to_avoid_loss(yearly_expenses: float):
        # Calculate minimum monthly profit needed to avoid a yearly loss
        return yearly_expenses / 12

    @staticmethod
    def categorize_expenses(expenses: List[Expense]):
        # Categorize expenses and calculate totals for each category
        expense_categories = {}
        for expense in expenses:
            category = expense.category
            if category in expense_categories:
                expense_categories[category] += expense.amount
            else:
                expense_categories[category] = expense.amount
        return expense_categories

# API Routes
@app.post("/user/create")
async def create_user(user: User):
    # Create a new user account
    db.users.insert_one(user.model_dump())
    return {"message": "User created successfully"}

@app.post("/income/add")
async def add_income(income: Income, user_id: str):
    # Add a new income entry for a user
    DatabaseOperations.add_income(user_id, income)
    return {"message": "Income added successfully"}

@app.post("/expense/add")
async def add_expense(expense: Expense, user_id: str):
    # Add a new expense entry for a user
    DatabaseOperations.add_expense(user_id, expense)
    return {"message": "Expense added successfully"}

@app.post("/loan/add")
async def add_loan(loan: Loan, user_id: str):
    # Add a new loan entry for a user
    DatabaseOperations.add_loan(user_id, loan)
    return {"message": "Loan added successfully"}

@app.post("/investment/add")
async def add_investment(investment: Investment, user_id: str):
    # Add a new investment entry for a user
    DatabaseOperations.add_investment(user_id, investment)
    return {"message": "Investment added successfully"}

@app.get("/financial-summary")
async def get_financial_summary(user_id: str, month: int, year: int):
    # Generate a financial summary for a specific month and year
    income = DatabaseOperations.get_monthly_income(user_id, month, year)
    expenses = DatabaseOperations.get_monthly_expenses(user_id, month, year)
    loans = DatabaseOperations.get_loans(user_id)
    investments = DatabaseOperations.get_investments(user_id)

    # Perform calculations
    net_return = FinancialCalculations.calculate_net_return(income, expenses, loans, investments, Investment.return_rate, Loan.interest_rate, Investment)
    yearly_projection = FinancialCalculations.project_yearly_trend(net_return)
    min_profit = FinancialCalculations.calculate_min_profit_to_avoid_loss(expenses * 12)
    expense_categories = FinancialCalculations.categorize_expenses(expenses)

    return {
        "net_return": net_return,
        "yearly_projection": yearly_projection,
        "min_profit_to_avoid_loss": min_profit,
        "expense_categories": expense_categories
    }


'''


# Additional suggested features:
# 1. Savings goal tracker
@app.post("/savings-goal")
async def set_savings_goal(user_id: str, goal_amount: float, target_date: datetime):
    # Set a savings goal for a user with a target amount and date
    pass

# 2. Budget alerts
@app.get("/budget-alerts")
async def get_budget_alerts(user_id: str):
    # Check if user is over budget in any category and return alerts
    pass

# 3. Financial health score
@app.get("/financial-health-score")
async def get_financial_health_score(user_id: str):
    # Calculate a financial health score based on income, expenses, debts, and savings
    pass

# 4. Investment performance tracker
@app.get("/investment-performance")
async def get_investment_performance(user_id: str):
    # Track and display the performance of user's investments over time
    pass

# 5. Debt repayment strategy
@app.get("/debt-repayment-strategy")
async def get_debt_repayment_strategy(user_id: str):
    # Suggest an optimal strategy for paying off debts, e.g., snowball or avalanche method
    pass
    

'''