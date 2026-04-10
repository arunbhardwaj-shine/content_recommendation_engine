from fastapi import FastAPI
#from api.search import router as search_router
from core.model_registry import initialize_models, start_background_refresh
from api.markov_routes import router as markov_router
from api.als_routes import router as als_router
from api.qdrant_route import router as qdrant_router
from api.all_routes import router as all_router
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from core.als_model import ALSRecommender
from utils.data_preprocessing import prepare_als_data
from utils.db_utils import get_engine
engine = get_engine()
app = FastAPI(
    title="Ingest & Search API",
    version="1.0.0"
)
als_model = ALSRecommender()
@app.on_event("startup")
def startup_event():
    initialize_models()
    start_background_refresh()
    interaction_df = prepare_als_data(engine)
    als_model.train(interaction_df)
    app.state.als_model = als_model
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],          # GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],          # Authorization, Content-Type, etc.
)

# Include routers
#app.include_router(search_router)
app.include_router(markov_router)
app.include_router(als_router)
app.include_router(qdrant_router)
app.include_router(all_router)
@app.get("/")
async def health_check():
    return {"status": "API is running"}


