from fastapi import HTTPException, status, Depends, Response, APIRouter, UploadFile
from DB import schema
from sqlalchemy.orm import Session
from DB.SqlAlchemy import get_db
from DB import models
from typing import List
from .map import file_processer
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/environments",
    tags=["Environments"]
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[schema.Environment])
def get_environments(db: Session = Depends(get_db)):
    env = db.query(models.Environment).all()
    return env


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=List[schema.MapOut])
def get_map_list_environments(id: int, db: Session = Depends(get_db)):

    env = db.query(models.Environment).filter(
        models.Environment.id == id).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Not Found"))
    else:
        maps = db.query(models.Map).join(models.Relate).filter(
            models.Relate.environment_id == id).all()
        return maps


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Environment)
async def create_Environment(name: str, mapfiles: List[UploadFile], db: Session = Depends(get_db)):

    map_list = []

    try:
        newEnv = models.Environment(name=name)
        db.add(newEnv)
        db.commit()
        db.refresh(newEnv)

        for file in mapfiles:
            res = await file_processer(mapFile=file, db=db)
            map_list.append(res)

        for i in map_list:
            newRelation = models.Relate(
                environment_id=newEnv.id, map_id=i.id)
            db.add(newRelation)
            db.commit()

        return newEnv
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str("Environment already Exist"))
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_Environment(id: int, db: Session = Depends(get_db)):
    env = db.query(models.Environment).filter(
        models.Environment.id == id).first()
    # t_user=db.query(models.User).filter(models.User.id==id).first()
    if not env:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str("Not Found"))
    else:
        db.query(models.Relate).filter(
            models.Relate.environment_id == id).delete(synchronize_session=False)
        db.commit()
        db.query(models.Environment).filter(models.Environment.id ==
                                            id).delete(synchronize_session=False)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{id}", status_code=status.HTTP_201_CREATED, response_model=schema.Environment)
async def add_maps_to_Environment(id: int, mapfiles: List[UploadFile], db: Session = Depends(get_db)):

    map_list = []

    try:
        env = db.query(models.Environment).filter(
            models.Environment.id == id).first()

        if not env:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str("Environment not found"))

        for file in mapfiles:
            res = await file_processer(mapFile=file, db=db)
            map_list.append(res)

        for i in map_list:
            newRelation = models.Relate(
                environment_id=env.id, map_id=i.id)
            db.add(newRelation)
            db.commit()

        return env
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))


@router.patch("/addmap/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def add_maps_to_Environment_using_id(id: int, mapIds: List[int], db: Session = Depends(get_db)):
    print(mapIds)
    try:
        for i in mapIds:

            if not db.query(models.Map).filter(models.Map.id == i).first():
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(
                    "Please Enter all valid map ids"))

        if not db.query(models.Environment).filter(models.Environment.id == id).first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(
                "Please Enter all valid Environment id"))

        for i in mapIds:
            newRelation = models.Relate(environment_id=id, map_id=i)
            db.add(newRelation)
            db.commit()
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str("Relation already Exist"))
