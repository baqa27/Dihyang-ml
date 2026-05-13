# Contributing to Dihyang Web (DITA)

Terima kasih atas minat Anda untuk berkontribusi pada proyek DITA!

## Development Setup

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

## Project Structure

```
CAPSTONE/
├── backend/
│   ├── app/
│   │   ├── models/          # ML models
│   │   ├── routers/         # API endpoints
│   │   ├── services/        # Background services
│   │   └── data/            # Datasets
│   ├── notebooks/           # Jupyter notebooks
│   └── scraper/             # Data collection
└── frontend/
    └── src/
        ├── pages/           # React pages
        ├── components/      # Reusable components
        └── services/        # API services
```

## Coding Standards

### Python (Backend)
- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Maximum line length: 100 characters

### JavaScript (Frontend)
- Use ES6+ syntax
- Follow Airbnb style guide
- Use functional components with hooks
- Add JSDoc comments for complex functions

## Testing

### Backend
```bash
python -m pytest tests/
```

### Frontend
```bash
npm test
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Code Review

All submissions require review. We use GitHub pull requests for this purpose.

## Questions?

Contact: Tim PJK-GM067
