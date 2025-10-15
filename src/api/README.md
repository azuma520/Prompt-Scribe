# Prompt-Scribe API

> LLM-Friendly Tag Recommendation API

**Version**: 2.0.0  
**Status**: Production-Ready ✅

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_ANON_KEY=your-anon-key

# Run server
uvicorn main:app --reload

# Open docs
open http://localhost:8000/docs
```

---

## 📁 Project Structure

```
src/api/
├── main.py                    # FastAPI application entry
├── config.py                  # Configuration management
│
├── models/                    # Pydantic models
│   ├── requests.py           # Request models
│   └── responses.py          # Response models
│
├── routers/                   # API routes
│   ├── v1/                   # Basic endpoints
│   │   ├── tags.py          # Tag queries
│   │   ├── search.py        # Search functionality
│   │   └── statistics.py   # Statistics
│   └── llm/                  # LLM-optimized endpoints
│       ├── recommendations.py   # Tag recommendations
│       ├── validation.py       # Prompt validation
│       ├── helpers.py          # Helper endpoints
│       └── smart_combinations.py  # Smart combinations (V2)
│
├── services/                  # Core business logic
│   ├── supabase_client.py          # Database client
│   ├── keyword_expander.py         # Keyword expansion
│   ├── cache_manager.py            # Memory cache
│   ├── keyword_analyzer.py         # P1: Keyword weights
│   ├── ngram_matcher.py            # P1: N-gram matching
│   ├── relevance_scorer.py         # P1: Enhanced scoring
│   ├── usage_logger.py             # P1: Usage logging
│   ├── tag_combination_analyzer.py # P2: Smart combinations
│   ├── redis_cache_manager.py      # P2: Redis cache
│   ├── hybrid_cache_manager.py     # P2: Hybrid cache
│   └── cache_strategy.py           # P2: Cache strategy
│
├── middleware/                # Middleware
│   └── logging_middleware.py  # Usage logging
│
├── data/                      # Data files
│   ├── keyword_synonyms.yaml
│   └── keyword_synonyms_extended.yaml
│
└── tests/                     # Test suite
    ├── test_basic_api.py           # Basic API tests
    ├── test_llm_endpoints.py       # LLM endpoint tests
    ├── test_cache.py               # Cache tests
    ├── test_batch_queries.py       # Batch query tests
    ├── test_load_performance.py    # Load tests
    ├── test_user_scenarios.py      # User scenario tests
    ├── requirements-test.txt       # Test dependencies
    ├── run_tests.sh               # Linux/Mac test runner
    ├── run_tests.ps1              # Windows test runner
    └── TESTING_GUIDE.md           # Testing guide
```

---

## 🔧 Configuration

### Environment Variables

**Required**:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

**Optional (V2.0 Features)**:
```bash
# Cache Strategy
CACHE_STRATEGY=hybrid  # memory, redis, or hybrid
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0

# Cache TTL
HYBRID_L1_TTL=300   # L1 cache: 5 minutes
HYBRID_L2_TTL=3600  # L2 cache: 1 hour

# Logging
LOG_LEVEL=INFO
```

### Cache Strategies

1. **memory** (Default for Vercel)
   - In-memory only
   - Fast, zero config
   - Lost on restart

2. **redis**
   - Redis only
   - Persistent cache
   - Requires Redis server

3. **hybrid** (Recommended)
   - L1: Memory (fast)
   - L2: Redis (persistent)
   - Best of both worlds

---

## 📚 API Endpoints

### Core Endpoints (V2.0 Enhanced)

**Recommendation**:
```
POST /api/llm/recommend-tags
→ Smart tag recommendations with P1 optimizations
```

**Smart Combinations (V2.0 NEW)**:
```
POST /api/llm/suggest-combinations
→ Intelligent tag combination suggestions

POST /api/llm/analyze-tags
→ Tag balance analysis
```

**Validation**:
```
POST /api/llm/validate-prompt
→ Detect conflicts and issues
```

**Search**:
```
POST /api/v1/search
→ Keyword search with expansion
```

**Health & Monitoring**:
```
GET /health          → Health check
GET /cache/stats     → Cache statistics
GET /cache/health    → Cache health
```

Full API documentation: http://localhost:8000/docs

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific test suite
pytest tests/test_user_scenarios.py -v

# With coverage
pytest tests/ --cov=services --cov=routers --cov-report=html

# Quick test
pytest tests/test_cache.py -v
```

### Test Suites

- `test_basic_api.py` - Basic API functionality
- `test_llm_endpoints.py` - LLM endpoints
- `test_cache.py` - Caching system (20 tests)
- `test_batch_queries.py` - Batch queries (12 tests)
- `test_load_performance.py` - Load testing (11 tests)
- `test_user_scenarios.py` - Real scenarios (17 tests)

**Coverage**: 98.7% ⭐

---

## 🔥 V2.0 New Features

### P1: Accuracy Improvements

1. **Multi-level Keyword Weights**
   - Automatic POS tagging
   - Nouns: 1.0, Adjectives: 0.85, Prepositions: 0.3
   - Expected: +10-15% accuracy

2. **N-gram Compound Word Matching**
   - Prioritize "school_uniform" over separate matches
   - 2-gram and 3-gram extraction
   - Expected: +15-20% compound word accuracy

3. **Enhanced Relevance Scoring**
   - Combines N-gram + weighted keywords + popularity
   - Three-tier matching strategy

### P2: Experience & Infrastructure

4. **Smart Tag Combinations**
   - 10+ predefined patterns
   - Balance analysis
   - Complete prompt suggestions

5. **Redis Cache Upgrade**
   - Persistent caching
   - Cross-instance sharing
   - Cache warming

6. **Hybrid Cache Strategy**
   - L1: Memory (ultra-fast)
   - L2: Redis (persistent)
   - Auto-promotion for hot data

---

## 📈 Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| P90 Response | < 2s | 319ms | ✅ 6.3x |
| P95 Response | < 2s | 337ms | ✅ 5.9x |
| Throughput | > 100 req/s | 770 req/s | ✅ 7.7x |
| Cache Hit Rate | > 80% | 90%+ | ✅ |
| Accuracy | > 80% | 85-90% | ✅ |

---

## 📖 Documentation

### User Guides
- [Testing Guide](tests/TESTING_GUIDE.md)
- [Deployment Guide](../../DEPLOYMENT_GUIDE.md)
- [CI/CD Setup](../../.github/CICD_SETUP_GUIDE.md)

### Technical Docs
- [P1 & P2 Optimization](../../docs/P1_P2_OPTIMIZATION_COMPLETE.md)
- [Optimization Roadmap](../../OPTIMIZATION_ROADMAP.md)
- [Performance Notes](../../docs/api/PERFORMANCE_NOTES.md)

### Reports
- [Test Execution Summary](../../TEST_EXECUTION_SUMMARY.md)
- [Test Optimization Report](../../TEST_OPTIMIZATION_FINAL_REPORT.md)

---

## 🔧 Development

### Setup

```bash
cd src/api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r tests/requirements-test.txt
```

### Run Development Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy services/ routers/
```

---

## 🐛 Troubleshooting

### Common Issues

**Import errors**:
- Ensure `PYTHONPATH` includes `src/api`
- Check all dependencies are installed

**Cache errors**:
- Redis not available → Auto fallback to memory cache
- Check `CACHE_STRATEGY` setting

**Slow responses**:
- Check `/cache/stats` for hit rate
- Verify Supabase connection
- Review logs for slow queries

---

## 📞 Support

- **Issues**: See [GitHub Issues](https://github.com/your-org/prompt-scribe/issues)
- **Documentation**: [docs/](../../docs/)
- **API Docs**: http://localhost:8000/docs

---

**Made with ❤️ by Prompt-Scribe Team**

Version 2.0.0 | Updated: 2025-10-15
