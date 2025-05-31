# 🏠 Property Management System - Microservices Architecture

A scalable and modular Property Management System built using a microservices architecture. This system enables users to manage apartments, event centers, rental listings, bookings, payments, and maintenance efficiently across separate services.

---

## ✨ Features

-   🔐 **User Management** – Signup, login, role-based access (Django + DRF)
-   🏘 **Property Listings** – Apartments, Event Centers, CRUD operations (Node.js + Express)
-   📆 **Bookings** – Reservation for properties, approval workflow (Flask)
-   💳 **Payments** – Rent payment and history with third-party integration (Django/Node.js)
-   🔧 **Maintenance Requests** – Issue tracking, status updates (Flask/Node)
-   📩 **Notifications** – Email/SMS alerts for system activities (Flask + Redis)
-   📦 **Microservice Architecture** – Independent services with dedicated databases
-   🐳 **Dockerized** – Easily deployable with Docker and Docker Compose

---

## 🧱 Technologies Used

| Service                | Stack                          | Database   |
| ---------------------- | ------------------------------ | ---------- |
| User Service           | Django + DRF                   | PostgreSQL |
| Property Service       | Node.js + Express              | MongoDB    |
| Booking Service        | Flask                          | PostgreSQL |
| Payment Service        | Django or Node.js              | PostgreSQL |
| Maintenance Service    | Node.js / Flask                | MongoDB    |
| Notification Service   | Flask + Redis + Celery/RQ      | Redis      |
| API Gateway (optional) | NGINX / Express Gateway / Kong | -          |

---

## 🧭 Project Structure
property-management-system/
│
├── user-service/ # Django REST Framework
├── property-service/ # Node.js + Express
├── booking-service/ # Flask
├── payment-service/ # Django or Node.js
├── maintenance-service/ # Flask or Node.js
├── notification-service/ # Flask + Celery
├── api-gateway/ # (Optional)
├── docker-compose.yml
└── README.md


---

## ⚙️ Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.10+
- Node.js 18+
- MongoDB, PostgreSQL
- Redis (for notifications)

### Clone the repo

```bash
git clone https://github.com/Franklyn883/property-management-system.git
cd property-management-system
docker-compose up --build
```
Or run each service individually in development mode.

## 🔐 Authentication Strategy
JWT-based authentication issued from user-service

Each microservice validates JWT via shared secret or public key

Internal API communication can use service-level API keys or internal auth headers

## 🔄 Inter-service Communication
REST-based communication between services

Event-based flow using Redis Pub/Sub or RabbitMQ (coming soon)

## 📌 Roadmap## 📌 Roadmap

### ✅ Completed

- [x] **User Service** – Django REST Framework
- [x] **Property Service** – Node.js + Express + MongoDB

### 🔧 In Progress

- [ ] **Booking Service** – Flask + PostgreSQL
- [ ] **Payment Integration** – Paystack or Flutterwave
- [ ] **Maintenance Tracking Service** – Flask or Node.js
- [ ] **Notification System** – Flask + Redis + Celery/RQ

### 🛠️ Infrastructure

- [x] **Docker Compose Setup**
- [ ] **API Gateway** – NGINX or Express Gateway

### 🧪 Testing & CI/CD

- [ ] **Unit & Integration Testing**
- [ ] **CI/CD Pipeline** – GitHub Actions or GitLab CI


## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author
Frank Alimimian
Backend Developer | Building scalable systems


