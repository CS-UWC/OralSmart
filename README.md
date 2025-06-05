# 🦷 OralSmart

OralSmart is a Django web application that allows users to register patients, screen for dental/dietary conditions, and refer them for hospital treatment.

## 🚀 Features

- Patient Registration
- Dental Screening
- Dietary Screening
- Referral System
- History & Reports
- Admin Panel

## 🛠️ Tech Stack

- Python 3.11.0
- Django 3.2.25
- SQLite/MySQL
- HTML/CSS (Django templates)

## 🏁 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/vhutali01/oralsmart.git
cd oralsmart
```

###  2. Create a Virtual environment

#### on mac or linux

```bash
python -m venv venv
source venv/bin/activate
```
#### on Windows
```bash
python -m venv venv
./venv/Scripts/activate
```

### 3. Install dependences

```bash
pip install -r requirements.txt
```

### 4. Run the App

```bash
python manage.py migrate
python manage.py runserver
```

### 5. Access the App

Visit http://127.0.0.1:8000
