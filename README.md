# Project 83120 - Handshaker

P2P Secure Chat Signaling Server

## What This Server Does

- ✅ User authentication (register/login)
- ✅ User discovery (search users, get public keys)
- ✅ WebRTC signaling relay (pass-through encrypted blobs)
- ✅ STUN/TURN server configuration

## What This Server Does NOT Do

- ❌ Store messages or files
- ❌ Decrypt any payload (all crypto is client-side)
- ❌ Have access to private keys

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Start MongoDB

```bash
# Using Docker
docker run -d -p 27017:27017 --name mongo-83120 mongo:latest

# Or use existing MongoDB
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API Docs

Open http://localhost:8000/docs

## API Endpoints

| Method | Endpoint                 | Description                  |
| ------ | ------------------------ | ---------------------------- |
| POST   | `/auth/register`         | Register with PGP public key |
| POST   | `/auth/login`            | Get JWT token                |
| POST   | `/auth/logout`           | Mark offline                 |
| PUT    | `/auth/pgp-key`          | Update PGP key (reinstall)   |
| GET    | `/users/search?q=@user`  | Search users                 |
| GET    | `/users/{username}`      | Get user's PGP key           |
| POST   | `/signaling/send`        | Send encrypted signal        |
| GET    | `/signaling/poll`        | Get pending signals          |
| DELETE | `/signaling/clear`       | Clear signals                |
| GET    | `/signaling/ice-servers` | Get STUN/TURN config         |

## Configuration

Edit `.env` to customize:

```env
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-secret-key
STUN_SERVERS=stun:stun.l.google.com:19302
TURN_SERVERS=turn:your-turn-server.com
TURN_USERNAME=username
TURN_CREDENTIAL=password
```
