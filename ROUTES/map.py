from fastapi import HTTPException, status, Depends, APIRouter, File, UploadFile
import secrets
from DB import schema
from sqlalchemy.orm import Session
from DB.SqlAlchemy import get_db
from DB import models
from typing import List
from fastapi.responses import FileResponse
import os
from DB.config import settings

router = APIRouter(
    prefix="/maps",
    tags=["Maps"]
)


def add_map(name, db):
    try:
        newMap = models.Map(name=name)
        db.add(newMap)
        db.commit()
        db.refresh(newMap)
        return newMap
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


async def file_processer(mapFile, db):
    filePath = settings.static_directory
    fileName = mapFile.filename
    extention = fileName.split('.')[1]

    newName = secrets.token_hex(13)+"."+extention
    mapEntry = add_map(name=newName, db=db)
    fullNewPath = os.path.join(filePath, newName)
    fileContent = await mapFile.read()
    with open(fullNewPath, "wb") as file:
        file.write(fileContent)

    return mapEntry


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.MapOut])
def get_all_maps(db: Session = Depends(get_db)):
    maps = db.query(models.Map).all()
    return maps


@router.get("/{id}", status_code=status.HTTP_200_OK)
def download_map(id: int, db: Session = Depends(get_db)):
    filePath = settings.static_directory
    selectedMap = db.query(models.Map).filter(models.Map.id == id).first()
    if selectedMap:
        fileName = selectedMap.name
        return FileResponse(path=os.path.join(filePath, fileName), filename=fileName)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=str("Map Not Found"))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_map(id: int, db: Session = Depends(get_db)):
    # find map
    mapQuery = db.query(models.Map).filter(models.Map.id == id)
    selectedMap = mapQuery.first()
    if not selectedMap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Not Found"))
    else:

        try:

            # delete relation
            result = db.query(models.Relate).filter(
                models.Relate.map_id == id).distinct(models.Relate.environment_id).all()
            x = [i.environment_id for i in result]
            db.query(models.Relate).filter(models.Relate.map_id ==
                                           id).delete(synchronize_session=False)
            db.commit()
            # delete env
            for i in x:
                if len(db.query(models.Relate).filter(models.Relate.environment_id == i).all()) == 0:
                    db.query(models.Environment).filter(
                        models.Environment.id == i).delete(synchronize_session=False)
                    db.commit()

            # delete file
            filePath = settings.static_directory
            os.remove(os.path.join(filePath, selectedMap.name))
            # delete map
            mapQuery.delete(synchronize_session=False)
            db.commit()
        except ValueError as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str("Internal Error"))


# Map
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.MapOut)
async def upload_map(mapfile: UploadFile = File(...), db: Session = Depends(get_db)):
    result = await file_processer(mapFile=mapfile, db=db)
    return result
