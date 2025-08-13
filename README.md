1️⃣ Clone the repository
git clone <github-repo-url>
cd <project-folder>

2️⃣ Create and activate a virtual environment
# Create venv
python -m venv venv  

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

3️⃣ Install dependencies from requirements.txt
pip install -r requirements.txt

4️⃣ Apply migrations
python manage.py migrate

5️⃣ Run the development server
python manage.py runserver

6️⃣ (Optional) Create a superuser for admin login
python manage.py createsuperuser
