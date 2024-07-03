'''import uvicorn
from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from FinanceManager import *

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.post("/submit-financial-data")
async def submit_financial_data(income: float = Form(...), expenses: float = Form(...), savings: float = Form(...)):
    # Process the financial data here
    # For example, save it to a database or perform calculations
    
    return RedirectResponse(url="/success", status_code=303)

# Initialize database operations and financial calculations instances
db_ops = DatabaseOperations()
financial_calcs = FinancialCalculations()

# Create a user interface for inputting financial data
@app.get("/input", response_class=HTMLResponse)
async def input_form():
    return templates.TemplateResponse("input.html", {"request": Request})

@app.post("/input", response_class=HTMLResponse)
async def process_input(request: Request, 
                         income_amount: float = Form(...), 
                         income_source: str = Form(...), 
                         income_date: str = Form(...), 
                         expense_amount: float = Form(...), 
                         expense_category: str = Form(...), 
                         expense_date: str = Form(...), 
                         loan_amount: float = Form(...), 
                         loan_interest_rate: float = Form(...), 
                         loan_lender: str = Form(...), 
                         loan_start_date: str = Form(...), 
                         loan_end_date: str = Form(...), 
                         investment_amount: float = Form(...), 
                         investment_return_rate: float = Form(...), 
                         investment_name: str = Form(...), 
                         investment_start_date: str = Form(...), 
                         investment_end_date: str = Form(...)):
    # Process user input and add to database
    # Get the user ID from the request or set a default value
    user_id = request.cookies.get("user_id", "john_doe")
    income = Income(amount=income_amount, source=income_source, date=datetime.strptime(income_date, "%Y-%m-%d"))
    db_ops.add_income(user_id, income)

    expense = Expense(amount=expense_amount, category=expense_category, date=datetime.strptime(expense_date, "%Y-%m-%d"))
    db_ops.add_expense(user_id, expense)

    loan = Loan(amount=loan_amount, interest_rate=loan_interest_rate, lender=loan_lender, start_date=datetime.strptime(loan_start_date, "%Y-%m-%d"), end_date=datetime.strptime(loan_end_date, "%Y-%m-%d"))
    db_ops.add_loan(user_id, loan)

    investment = Investment(amount=investment_amount, return_rate=investment_return_rate, name=investment_name, start_date=datetime.strptime(investment_start_date, "%Y-%m-%d"), end_date=datetime.strptime(investment_end_date, "%Y-%m-%d"))
    db_ops.add_investment(user_id, investment)

    # Generate financial summary
    financial_summary = db_ops.get_financial_summary(user_id, 6, 2023)  # Replace with actual month and year

    # Perform financial calculations
    net_return = financial_calcs.calculate_net_return(financial_summary["income"], financial_summary["expenses"], financial_summary["loans"], financial_summary["investments"])
    yearly_projection = financial_calcs.project_yearly_trend(net_return)
    min_profit = financial_calcs.calculate_min_profit_to_avoid_loss(financial_summary["expenses"] * 12)
    expense_categories = financial_calcs.categorize_expenses(financial_summary["expenses"])

    # Display financial summary and calculations
    return templates.TemplateResponse("summary.html", {"request": Request, 
                                                       "financial_summary": financial_summary, 
                                                       "net_return": net_return, 
                                                       "yearly_projection": yearly_projection, 
                                                       "min_profit": min_profit, 
                                                       "expense_categories": expense_categories})

# Run the application
#Type "localhost:8000/docs" in a browser to view the website
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    '''

from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pymongo import MongoClient
import os
from bson import ObjectId

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient(os.environ.get("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["finance_manager"]

# Models
class Income(BaseModel):
    amount: float
    source: str
    date: datetime

class Expense(BaseModel):
    amount: float
    category: str
    date: datetime

class Loan(BaseModel):
    amount: float
    interest_rate: float
    lender: str
    start_date: datetime
    end_date: datetime

class Investment(BaseModel):
    amount: float
    return_rate: float
    name: str
    start_date: datetime
    end_date: Optional[datetime]

class User(BaseModel):
    username: str
    email: str
    password: str

# Database Operations
class DatabaseOperations:
    @staticmethod
    def create_user(user: User):
        user_dict = user.dict()
        result = db.users.insert_one(user_dict)
        return str(result.inserted_id)

    @staticmethod
    def add_income(user_id: str, income: Income):
        income_dict = income.dict()
        income_dict["user_id"] = ObjectId(user_id)
        db.incomes.insert_one(income_dict)

    @staticmethod
    def add_expense(user_id: str, expense: Expense):
        expense_dict = expense.dict()
        expense_dict["user_id"] = ObjectId(user_id)
        db.expenses.insert_one(expense_dict)

    @staticmethod
    def add_loan(user_id: str, loan: Loan):
        loan_dict = loan.dict()
        loan_dict["user_id"] = ObjectId(user_id)
        db.loans.insert_one(loan_dict)

    @staticmethod
    def add_investment(user_id: str, investment: Investment):
        investment_dict = investment.dict()
        investment_dict["user_id"] = ObjectId(user_id)
        db.investments.insert_one(investment_dict)

    @staticmethod
    def get_monthly_income(user_id: str, month: int, year: int):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        pipeline = [
            {"$match": {
                "user_id": ObjectId(user_id),
                "date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(db.incomes.aggregate(pipeline))
        return result[0]["total"] if result else 0

    @staticmethod
    def get_monthly_expenses(user_id: str, month: int, year: int):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        pipeline = [
            {"$match": {
                "user_id": ObjectId(user_id),
                "date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(db.expenses.aggregate(pipeline))
        return result[0]["total"] if result else 0

    @staticmethod
    def get_loans(user_id: str):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(db.loans.aggregate(pipeline))
        return result[0]["total"] if result else 0

    @staticmethod
    def get_investments(user_id: str):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = list(db.investments.aggregate(pipeline))
        return result[0]["total"] if result else 0

# Financial Calculations
class FinancialCalculations:
    @staticmethod
    def calculate_net_return(income: float, expenses: float, loan_payments: float, investment_returns: float):
        return income - expenses + investment_returns - loan_payments

    @staticmethod
    def project_yearly_trend(monthly_net_return: float):
        return monthly_net_return * 12

    @staticmethod
    def calculate_min_profit_to_avoid_loss(yearly_expenses: float):
        return yearly_expenses / 12

    @staticmethod
    def categorize_expenses(user_id: str, month: int, year: int):
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        pipeline = [
            {"$match": {
                "user_id": ObjectId(user_id),
                "date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
        ]
        result = list(db.expenses.aggregate(pipeline))
        return {item["_id"]: item["total"] for item in result}

# API Routes
@app.post("/user/create")
async def create_user(user: User):
    try:
        user_id = DatabaseOperations.create_user(user)
        return {"message": "User created successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/user/{user_id}/income/add")
async def add_income(
    income: Income,
    user_id: str = Path(..., title="The ID of the user to add income for")
):
    try:
        DatabaseOperations.add_income(user_id, income)
        return {"message": "Income added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/user/{user_id}/expense/add")
async def add_expense(
    expense: Expense,
    user_id: str = Path(..., title="The ID of the user to add expense for")
):
    try:
        DatabaseOperations.add_expense(user_id, expense)
        return {"message": "Expense added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/user/{user_id}/loan/add")
async def add_loan(
    loan: Loan,
    user_id: str = Path(..., title="The ID of the user to add loan for")
):
    try:
        DatabaseOperations.add_loan(user_id, loan)
        return {"message": "Loan added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/user/{user_id}/investment/add")
async def add_investment(
    investment: Investment,
    user_id: str = Path(..., title="The ID of the user to add investment for")
):
    try:
        DatabaseOperations.add_investment(user_id, investment)
        return {"message": "Investment added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/user/{user_id}/financial-summary")
async def get_financial_summary(
    user_id: str = Path(..., title="The ID of the user to get financial summary for"),
    month: int = Path(..., title="The month to get summary for"),
    year: int = Path(..., title="The year to get summary for")
):
    try:
        income = DatabaseOperations.get_monthly_income(user_id, month, year)
        expenses = DatabaseOperations.get_monthly_expenses(user_id, month, year)
        loans = DatabaseOperations.get_loans(user_id)
        investments = DatabaseOperations.get_investments(user_id)

        net_return = FinancialCalculations.calculate_net_return(income, expenses, loans, investments)
        yearly_projection = FinancialCalculations.project_yearly_trend(net_return)
        min_profit = FinancialCalculations.calculate_min_profit_to_avoid_loss(expenses * 12)
        expense_categories = FinancialCalculations.categorize_expenses(user_id, month, year)

        return {
            "net_return": net_return,
            "yearly_projection": yearly_projection,
            "min_profit_to_avoid_loss": min_profit,
            "expense_categories": expense_categories
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)