import datetime
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from ai_model.ai_model import AIModel
import crud
from database import SessionLocal, engine
from image_utils.image_utils import ImageUtils
import app_models
import schemas
from fastapi.middleware.cors import CORSMiddleware
app_models.Base.metadata.create_all(bind=engine)
from spa_static_files import SPAStaticFiles
import uvicorn
from fastapi.responses import FileResponse


app = FastAPI()

# Set up CORS
origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173",
           "http://localhost:8080", "http://127.0.0.1:3000", "http://127.0.0.1:8080"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def serve_index():
    return FileResponse("dist/index.html")



@app.post("/evaluate_pwb")
async def evaluate_pwb(image_data: schemas.ImageData, db: Session = Depends(get_db)):
    # Save the image to disk
    image = ImageUtils.read_base64_image(image_data.datauri)
    ai_model = AIModel()
    gray_scale_image = ImageUtils.image_to_grayscale(image)
    result = ai_model.classify(gray_scale_image)
    evaluation = ai_model.evaluate(result)

    # img_bytes = ImageUtils.convert_image_to_base64(image)
    result = schemas.ClassificationResultCreate(
        class_name=evaluation["label"], probability=evaluation["probability"], created_at=datetime.datetime.now(), batch_id=image_data.batch_id)
    db_classification_result = crud.create_classification_result(
        db=db, classification_result=result
    )
    return db_classification_result


@app.post("/classification_result", response_model=schemas.ClassificationResult)
def create_classification_result(classification_result: schemas.ClassificationResultCreate, db: Session = Depends(get_db)):
    db_classification_result = crud.create_classification_result(
        db=db, classification_result=classification_result)
    return db_classification_result


@app.get("/classification_result/{result_id}", response_model=schemas.ClassificationResult)
def read_classification_result(result_id: int, db: Session = Depends(get_db)):
    db_classification_result = crud.get_classification_result(
        db, result_id=result_id)
    if db_classification_result is None:
        raise HTTPException(
            status_code=404, detail="Classification Result not found")
    return db_classification_result


@app.get("/classification_counts")
def get_classification_counts_endpoint(db: Session = Depends(get_db)):
    counts = crud.get_classification_counts(db)
    return counts


@app.get("/classification_result", response_model=List[schemas.ClassificationResult])
def read_classification_results(
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    descending: bool = True,
    db: Session = Depends(get_db)
):
    results = crud.get_classification_results(
        db, skip=skip, limit=limit, order_by=order_by, descending=descending)
    return [schemas.ClassificationResult.from_orm(result) for result in results]


# Get Classification Results by Batch ID
@app.get("/classification_results/{batch_id}", response_model=List[schemas.ClassificationResult])
def get_classification_results_by_batch_id(batch_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    classification_results = crud.get_classification_results(
        db, batch_id=batch_id, skip=skip, limit=limit)
    return classification_results

app.mount("/", SPAStaticFiles(directory="dist", html=True), name='PWB App')


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)