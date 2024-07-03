from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["finance_manager"]

class FinanceManager:
    @staticmethod
    def create_user(username: str, email: str, password: str):
        user = {
            "username": username,
            "email": email,
            "password": password  # In a real app, ensure this is hashed
        }
        result = db.users.insert_one(user)
        return str(result.inserted_id)

    @staticmethod
    def add_income(user_id: str, amount: float, source: str, date: datetime):
        income = {
            "user_id": ObjectId(user_id),
            "amount": amount,
            "source": source,
            "date": date
        }
        db.incomes.insert_one(income)

    @staticmethod
    def add_expense(user_id: str, amount: float, category: str, date: datetime):
        expense = {
            "user_id": ObjectId(user_id),
            "amount": amount,
            "category": category,
            "date": date
        }
        db.expenses.insert_one(expense)

    @staticmethod
    def add_loan(user_id: str, amount: float, interest_rate: float, lender: str, start_date: datetime, end_date: datetime):
        loan = {
            "user_id": ObjectId(user_id),
            "amount": amount,
            "interest_rate": interest_rate,
            "lender": lender,
            "start_date": start_date,
            "end_date": end_date
        }
        db.loans.insert_one(loan)

    @staticmethod
    def add_investment(user_id: str, amount: float, return_rate: float, name: str, start_date: datetime, end_date: datetime = None):
        investment = {
            "user_id": ObjectId(user_id),
            "amount": amount,
            "return_rate": return_rate,
            "name": name,
            "start_date": start_date,
            "end_date": end_date
        }
        db.investments.insert_one(investment)

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

    @staticmethod
    def calculate_net_return(user_id: str, month: int, year: int):
        income = FinanceManager.get_monthly_income(user_id, month, year)
        expenses = FinanceManager.get_monthly_expenses(user_id, month, year)
        
        # Calculate loan interest
        loans = list(db.loans.find({"user_id": ObjectId(user_id)}))
        loan_interest = sum(loan["amount"] * (loan["interest_rate"] / 12) for loan in loans)
        
        # Calculate investment returns
        investments = list(db.investments.find({"user_id": ObjectId(user_id)}))
        investment_returns = sum(inv["amount"] * (inv["return_rate"] / 12) for inv in investments)
        
        return income - expenses - loan_interest + investment_returns

    @staticmethod
    def project_yearly_trend(user_id: str, month: int, year: int):
        monthly_net_return = FinanceManager.calculate_net_return(user_id, month, year)
        return monthly_net_return * 12
    
    @staticmethod
    def calculate_min_profit_to_avoid_loss(user_id: str, month: int, year: int):
        yearly_expenses = FinanceManager.get_monthly_expenses(user_id, month, year) * 12
        return yearly_expenses / 12
    
    def get_user_input():
        print("Welcome to the Finance Manager!")
        
        # Create user
        username = input("Enter username: ")
        email = input("Enter email: ")
        password = input("Enter password: ")
        user_id = FinanceManager.create_user(username, email, password)
        print(f"Created user with ID: {user_id}")

        # Add income
        amount = float(input("Enter income amount: "))
        source = input("Enter income source: ")
        date_str = input("Enter income date (YYYY-MM-DD): ")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        FinanceManager.add_income(user_id, amount, source, date)

        # Add expense
        amount = float(input("Enter expense amount: "))
        category = input("Enter expense category: ")
        date_str = input("Enter expense date (YYYY-MM-DD): ")
        date = datetime.strptime(date_str, "%Y-%m-%d")
        FinanceManager.add_expense(user_id, amount, category, date)

        # Add loan
        amount = float(input("Enter loan amount: "))
        interest_rate = float(input("Enter loan interest rate: "))
        lender = input("Enter lender name: ")
        start_date_str = input("Enter loan start date (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date_str = input("Enter loan end date (YYYY-MM-DD): ")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        FinanceManager.add_loan(user_id, amount, interest_rate, lender, start_date, end_date)

        # Add investment
        amount = float(input("Enter investment amount: "))
        return_rate = float(input("Enter investment return rate: "))
        name = input("Enter investment name: ")
        start_date_str = input("Enter investment start date (YYYY-MM-DD): ")
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        FinanceManager.add_investment(user_id, amount, return_rate, name, start_date)

        # Get summary month and year
        month = int(input("Enter month for summary (1-12): "))
        year = int(input("Enter year for summary: "))

        return user_id, month, year

    def display_summary(user_id, month, year):
        # Get financial summary
        income = FinanceManager.get_monthly_income(user_id, month, year)
        expenses = FinanceManager.get_monthly_expenses(user_id, month, year)
        loans = FinanceManager.get_loans(user_id)
        investments = FinanceManager.get_investments(user_id)
        
        print(f"\nFinancial Summary for {month}/{year}")
        print(f"Monthly Income: ${income}")
        print(f"Monthly Expenses: ${expenses}")
        print(f"Total Loans: ${loans}")
        print(f"Total Investments: ${investments}")

        # Calculate net return
        net_return = FinanceManager.calculate_net_return(user_id, month, year)
        print(f"Net Return: ${net_return}")

        # Project yearly trend
        yearly_trend = FinanceManager.project_yearly_trend(user_id, month, year)
        print(f"Yearly Projection: ${yearly_trend}")

        # Get expense categories
        categories = FinanceManager.categorize_expenses(user_id, month, year)
        print("Expense Categories:")
        for category, amount in categories.items():
            print(f"  {category}: ${amount}")

        # Calculate minimum profit to avoid loss
        min_profit = FinanceManager.calculate_min_profit_to_avoid_loss(user_id, month, year)
        print(f"Minimum Monthly Profit to Avoid Loss: ${min_profit}")

# Example usage:
if __name__ == "__main__":
    user_id, month, year = FinanceManager.get_user_input()
    FinanceManager.display_summary(user_id, month, year)