# FinanceFlow 🚀💰

[![Vue.js](https://img.shields.io/badge/Vue.js-3-green?logo=vue.js)](https://vuejs.org/)
[![Flask](https://img.shields.io/badge/Flask-blue?logo=flask)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb)](https://mongodb.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-95%25-brightgreen)](https://github.com/yourusername/personal-finance-tracker/actions)

A **full-stack personal finance management application** built with **Vue.js**, **Flask**, and **MongoDB**. Track income/expenses, set budgets, visualize spending patterns with interactive charts, and receive real-time alerts—all in a secure, responsive dashboard.

## ✨ Features

- **`📊 Transaction Management`**: Add, edit, delete income/expenses with categories (Food, Rent, Salary, etc.), dates, amounts, and notes
- **`💳 Budget Tracking`**: Set monthly/weekly limits per category with visual progress bars and over-budget alerts
- **`📈 Interactive Analytics`**: Real-time Chart.js visualizations (pie charts for categories, line graphs for trends, sankey for cash flow)
- **`🔐 Secure Multi-User Auth`**: JWT-based login/register, role-based access (User/Admin), bcrypt password hashing
- **`📋 Custom Reports`**: Filter by date range/category, generate CSV exports, customizable currency/preferences
- **`🔔 Smart Notifications`**: Celery-powered budget alerts, spending insights via email/push
- **`📱 PWA Support`**: Offline transaction logging, responsive design (mobile-first), installable app
- **`⚡ Performance`**: Handles 10k+ transactions with <200ms API response times

## 🛠 Tech Stack

| Category     | Technologies                                      |
|--------------|--------------------------------------------------|
| **Frontend** | `Vue 3` (Composition API), `Pinia`, `Vue Router`, `Chart.js`, `Tailwind CSS`, `Axios` |
| **Backend**  | `Flask`, `Flask-JWT-Extended`, `PyMongo`, `Celery`, `Flask-CORS` |
| **Database** | `MongoDB` (Atlas), Aggregation Pipelines         |


