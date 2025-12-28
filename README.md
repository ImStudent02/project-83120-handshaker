# 🤝 Project 83120 - Handshaker

> **"We Believe in Privacy & Anonymity"**

**Signaling Server for P2P Secure Chat**

A FastAPI backend that facilitates WebRTC signaling, user authentication, and connection management for end-to-end encrypted peer-to-peer communication.

[![Open Source](https://img.shields.io/badge/Open%20Source-Yes-green)](./LICENSE)
[![Privacy First](https://img.shields.io/badge/Privacy-First-blue)](../PRIVACY_POLICY.md)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Development Status](#-development-status)
- [Contributing](#-contributing)
- [Legal](#-legal)

---

## ✅ Features

### What This Server Does

- ✅ User authentication (register/login with JWT)
- ✅ Password reset with OTP
- ✅ User discovery (search users, get public keys)
- ✅ Connection request system (request/accept/reject)
- ✅ WebRTC signaling relay (encrypted offer/answer/ICE)
- ✅ STUN/TURN server configuration

### What This Server Does NOT Do

- ❌ Store messages or files (P2P only)
- ❌ Decrypt any payload (all crypto is client-side)
- ❌ Have access to private keys or message content

---

## 🏗 Architecture

```
┌─────────────┐     Signaling      ┌─────────────┐
│   Client A  │◄──────────────────►│  Handshaker │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │  P2P (WebRTC)                    │
       │◄─────────────────────────────────┼── TURN relay (if needed)
       │                                  │
       ▼                                  │
┌─────────────┐     Signaling      ┌──────┴──────┐
│   Client B  │◄──────────────────►│   MongoDB   │
└─────────────┘                    └─────────────┘
```

---

## 🚀 Quick Start

### 🪟 Windows Setup

#### 1. Install Python

```powershell
# Download from https://python.org (version 3.10+)
# Or use winget:
winget install Python.Python.3.11

# Verify
python --version
```

#### 2. Install MongoDB

```powershell
# Option A: Docker (recommended)
docker run -d -p 27017:27017 --name mongo-83120 mongo:latest

# Option B: MongoDB Community Server
# Download from https://www.mongodb.com/try/download/community
```

#### 3. Install & Run

```powershell
cd project-83120-handshaker

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env
# Edit .env with your configuration

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 🐧 Linux Setup (Ubuntu/Debian)

#### 1. Install Python

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3 --version
```

#### 2. Install MongoDB

```bash
# Option A: Docker
sudo apt install docker.io
sudo docker run -d -p 27017:27017 --name mongo-83120 mongo:latest

# Option B: MongoDB Server
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
```

#### 3. Install & Run

```bash
cd project-83120-handshaker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
nano .env  # Edit configuration

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Run as Service (Production)

```bash
# Create systemd service
sudo nano /etc/systemd/system/handshaker.service
```

```ini
[Unit]
Description=Project 83120 Handshaker
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/project-83120-handshaker
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable handshaker
sudo systemctl start handshaker
```

---

### 🍎 macOS Setup

#### 1. Install Homebrew & Python

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.11
```

#### 2. Install MongoDB

```bash
# Using Docker
brew install docker
docker run -d -p 27017:27017 --name mongo-83120 mongo:latest

# Or MongoDB directly
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### 3. Install & Run

```bash
cd project-83120-handshaker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
nano .env  # Edit configuration

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Environment Configuration

Create `.env` file with:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=project_83120

# Security (generate random keys!)
SECRET_KEY=your-secret-key-here-min-32-chars
EMAIL_ENCRYPTION_KEY=your-32-byte-fernet-key

# TURN Server (optional)
TURN_SERVERS=turn:your-turn-server.com:3478
TURN_USERNAME=username
TURN_CREDENTIAL=password
```

### Access API Docs

Open http://localhost:8000/docs (Swagger UI)

---

## 📚 API Reference

### Authentication

| Method | Endpoint                | Description                                       |
| ------ | ----------------------- | ------------------------------------------------- |
| POST   | `/auth/register`        | Register with username, email, birthday, password |
| POST   | `/auth/login`           | Login, get JWT token                              |
| POST   | `/auth/logout`          | Mark user offline                                 |
| PUT    | `/auth/pgp-key`         | Update PGP public key                             |
| POST   | `/auth/forgot-password` | Request password reset OTP                        |
| POST   | `/auth/reset-password`  | Reset password with OTP                           |

### Users

| Method | Endpoint                    | Description                      |
| ------ | --------------------------- | -------------------------------- |
| GET    | `/users/search?q=@username` | Search users by username         |
| GET    | `/users/{username}`         | Get user's public info + PGP key |

### Connection Requests

| Method | Endpoint                  | Description             |
| ------ | ------------------------- | ----------------------- |
| POST   | `/connections/request`    | Send connection request |
| GET    | `/connections/pending`    | Get pending requests    |
| POST   | `/connections/respond`    | Accept/reject request   |
| GET    | `/connections/`           | List all connections    |
| DELETE | `/connections/{username}` | Remove connection       |

### WebRTC Signaling

| Method | Endpoint                 | Description                              |
| ------ | ------------------------ | ---------------------------------------- |
| POST   | `/signaling/send`        | Send encrypted signal (offer/answer/ICE) |
| GET    | `/signaling/poll`        | Poll for pending signals                 |
| DELETE | `/signaling/clear`       | Clear all pending signals                |
| GET    | `/signaling/ice-servers` | Get STUN/TURN configuration              |

---

## ⚙️ Configuration

### Environment Variables

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=project_83120

# Security
SECRET_KEY=your-jwt-secret-key
EMAIL_ENCRYPTION_KEY=your-32-byte-fernet-key

# TURN Server (optional, for NAT traversal)
TURN_SERVERS=turn:your-turn-server.com:3478
TURN_USERNAME=turn-username
TURN_CREDENTIAL=turn-password
```

---

## 📊 Development Status

### ✅ Completed

- [x] User registration with email encryption
- [x] JWT authentication
- [x] Password reset with OTP
- [x] User search and discovery
- [x] PGP key storage and exchange
- [x] Connection request/accept system
- [x] WebRTC signaling (offer/answer/ICE relay)
- [x] CORS configuration

### 🔄 In Progress

- [ ] TURN server integration (Coturn/Cloudflare)
- [ ] WebSocket-based signaling (replace polling)
- [ ] Online/offline status heartbeat

### 📋 Planned

- [ ] Rate limiting
- [ ] Connection request expiry
- [ ] Push notifications (FCM/APNs)
- [ ] Admin dashboard

---

## 🤝 Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

### Code Style

- Use Python type hints
- Follow PEP 8 guidelines
- Document functions with docstrings

### Project Structure

```
app/
├── main.py              # FastAPI app entry
├── config.py            # Configuration
├── database.py          # MongoDB connection
├── routes/
│   ├── auth.py          # Authentication endpoints
│   ├── users.py         # User endpoints
│   ├── connection.py    # Connection request endpoints
│   └── signaling.py     # WebRTC signaling endpoints
├── services/
│   ├── auth_service.py  # Auth business logic
│   └── connection_service.py  # Connection logic
└── schemas/
    ├── auth.py          # Auth request/response models
    └── connection.py    # Connection models
```

### Reporting Issues

Please include:

- Description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Logs if applicable

---

## 📄 License

MIT License - See LICENSE file for details.

---

## ⚖️ Legal

- [Terms of Service](../TERMS_OF_SERVICE.md)
- [Privacy Policy](../PRIVACY_POLICY.md)
- [Roadmap](../ROADMAP.md)

---

## 🔗 Related

- [Mobile Client](../project-83120-f-mobile) - React Native app
- [Roadmap](../ROADMAP.md) - Feature status & vision

---

_"Privacy is not about hiding something. Privacy is about being able to control what you reveal about yourself."_
