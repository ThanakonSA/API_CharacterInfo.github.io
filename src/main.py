from fastapi import FastAPI, HTTPException, Body
from pymongo import MongoClient, DESCENDING
from fastapi.middleware.cors import CORSMiddleware
from models.setmodel import CreateItemBuild, ItemBuild, PatchItemBuild
from models.heromainmodel import HeroMainModel
from models.herofullmodel import HeroFullModel, convert_row_to_heroes
from models.Itemsfullmodel import ItemFullModel, ItemInfo, ItemMainModel, convert_row_to_item
from typing import List, Optional


tags_metadata = [
    {
        "name": "default",
        "description": "Endpoints กลุ่มทั่วไป (ยังไม่กำหนด tags)"
    },
    {
        "name": "heroes",
        "description": "จัดการข้อมูลฮีโร่"
    },
    {
        "name": "items",
        "description": "จัดการข้อมูลไอเท็ม"
    },
]

app = FastAPI(
    title="MLBB API",
    version="1.0.0",
    openapi_tags=tags_metadata,
    docs_url="/docs",
    redoc_url=None
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb+srv://thanakon3:Teera0Chineseboi@cluster0.mft4otf.mongodb.net/")
db = client["MobileLegend_wiki_backend"]
heroes_collection = db["heroesinfos"]
items_collection = db["itemsInfos"]
setitems_collection = db["setitems"]


def fix_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# -------------------- Heroes_id HEROES ROUTES --------------------
# @app.get("/heroes/{hero_id}", response_model=HeroFullModel) #ตัวดึง Hero_ID
@app.get(
    "/heroes/{hero_id}",
    response_model=HeroFullModel,
    tags=["heroes"],
    summary="ดึงฮีโร่ตามไอดี",
    description="รับ Hero_ID แล้วคืนข้อมูลฮีโร่ทั้งหมดแบบ nested structure"
)
def get_hero_by_id(hero_id: str):
    doc = heroes_collection.find_one({"Hero_ID": hero_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Hero not found")
    flat = { k: str(v) for k, v in doc.items() if k != "_id" }
    return convert_row_to_heroes(flat)

# ------------------------ HEROES ROUTES ----------------------------
# @app.get("/heroes", response_model=List[HeroFullModel])
@app.get(
    "/heroes",
    response_model=List[HeroFullModel],
    tags=["heroes"],
    summary="ดึงข้อมูลฮีโร่ทั้งหมด",
    description="คืนรายการฮีโร่ทุกตัวพร้อมรายละเอียดครบทุกฟิลด์"
)
def list_all_heroes():
    docs = list(heroes_collection.find())
    heroes = []
    for doc in docs:
        flat = { k: str(v) for k, v in doc.items() if k != "_id" }
        heroes.append(convert_row_to_heroes(flat))
    return heroes

# -------------------- Heroesmian_id HEROESMain ROUTES --------------------
# @app.get("/heroesmain/{hero_id}", response_model=HeroFullModel) #ตัวดึง Hero_ID
@app.get(
    "/heroesmain/{hero_id}",
    response_model=HeroFullModel,
    tags=["heroes"],
    summary="ดึงฮีโร่ตามไอดี",
    description="รับ Hero_ID แล้วคืนข้อมูลฮีโร่ทั้งหมดแบบ nested structure"
)
def get_hero_heroesmain(hero_id: str):
    doc = heroes_collection.find_one({"Hero_ID": hero_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Hero not found")
    flat = { k: str(v) for k, v in doc.items() if k != "_id" }
    return convert_row_to_heroes(flat) 

# ------------------------ HEROESMain ROUTES ----------------------------
@app.get(
    "/heroesmain",
    response_model=List[HeroMainModel],
    tags=["heroes"],
    summary="ดึงข้อมูลฮีโร่บางส่วน",
    description="รับ Hero_ID แล้วคืนข้อมูลฮีโร่ทั้งหมดแบบ nested structure"
)
def list_all_heroes():
    docs = list(heroes_collection.find())
    heroes = [
        HeroMainModel(
            hero_id=doc.get("Hero_ID", ""),
            hero_name=doc.get("HeroName", ""),
            role=doc.get("Role", ""),
            specialty=doc.get("Specialty", ""),
            lane_recc=doc.get("Lane_Recc", ""),
            icon=doc.get("Iconhero", ""),
            full=doc.get("Imagehero", "")
        )
        for doc in docs
    ]
    return heroes



# -------------------- Item_id ITEMS ROUTES --------------------
@app.get(
    "/items/{item_id}", 
    response_model=ItemFullModel,
    tags=["items"],
    summary="ดึงไอเทมตามไอดี",
    description="รับ Item_ID แล้วคืนข้อมูลไอเทมทั้งหมดแบบ nested structure"
)
def get_item_full(item_id: str):
    doc = items_collection.find_one({"Item_ID": item_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    flat = { k: str(v) for k, v in doc.items() if k != "_id" }
    return convert_row_to_item(flat)

# ------------------------- ITEMS ROUTES ----------------------------------
@app.get(
    "/items", 
    response_model=List[ItemFullModel],
    tags=["items"],
    summary="ดึงข้อมูลไอเทมทั้งหมด",
    description="คืนรายการไอเทมทุกอย่างพร้อมรายละเอียดครบทุกฟิลด์"
)
def list_all_items():
    docs = list(items_collection.find())
    items = []
    for doc in docs:
        flat = { k: str(v) for k, v in doc.items() if k != "_id" }
        items.append(convert_row_to_item(flat))
    return items


#--------------------- Setitems_id SETITEMS ROUTES --------------------
@app.post(
    "/newsetitems",
    response_model=ItemBuild,
    summary="สร้างเซตไอเทมใหม่",
    description="รับ hero_id และรายการ item_ids (6 ช่อง) → ดึงข้อมูลจาก itemsInfos → บันทึกลง setitems"
)
def create_item_build(payload: CreateItemBuild):
    last = setitems_collection.find_one(sort=[("setitems_id", DESCENDING)])
    next_id = (last["setitems_id"] + 1) if last else 1

    items = []
    for iid in payload.item_ids:
        if iid is None:
            items.append(ItemMainModel(iteminfo=None))
            continue

        doc = items_collection.find_one(
            {"Item_ID": iid},
            {"_id":0, "Item_ID":1, "ItemName":1, "Type_Item":1, "Price":1, "Icon_Item":1}
        )
        if not doc:
            raise HTTPException(404, f"Item {iid} not found")

        info = ItemInfo(
            item_id   = doc["Item_ID"],
            item_name = doc["ItemName"],
            type_item = doc["Type_Item"],
            price     = str(doc["Price"]),
            icon      = doc["Icon_Item"]
        )
        items.append(ItemMainModel(iteminfo=info))

    set_doc = {
        "setitems_id": next_id,
        "hero_id":     payload.hero_id,
        "items":       [item.dict() for item in items]
    }
    setitems_collection.insert_one(set_doc)
    return set_doc

# ——— ดึงชุดไอเทมตาม id ———
@app.get(
    "/setitems/{set_id}",
    response_model=ItemBuild,
    summary="ดึงข้อมูลเซตไอเทมตาม setitems_id",
    description="รับ setitems_id ใน path → คืนข้อมูลเซตไอเทมตัวนั้น (ไม่คืน _id จาก Mongo)"
)
def get_item_build(set_id: int):
    # ค้นใน MongoDB โดยตัดฟิลด์ internal _id ออก
    doc = setitems_collection.find_one(
        {"setitems_id": set_id},
        {"_id": 0}
    )
    if not doc:
        # ถ้าไม่เจอ ให้ตอบ 404
        raise HTTPException(status_code=404, detail=f"Setitems {set_id} not found")
    return doc


#-------------------- edit setitems_id SETITEMS ROUTES --------------------
@app.put(
    "/sets/{set_id}",
    response_model=ItemBuild,
    summary="อัปเดตเซตไอเทม",
)
def update_item_build(set_id: int, payload: CreateItemBuild):
    # ยืนยันว่ามีชุดนี้อยู่
    existing = setitems_collection.find_one({"setitems_id": set_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Set not found")

    # ดึงข้อมูลไอเทมใหม่
    items = []
    for iid in payload.item_ids:
        doc = items_collection.find_one({"Item_ID": iid})
        if not doc:
            raise HTTPException(status_code=404, detail=f"Item {iid} not found")
        flat = { k: str(v) for k, v in doc.items() if k != "_id" }
        items.append(convert_row_to_item(flat))

# อัปเดตใน Mongo
    updated = {
        "hero_id": payload.hero_id,
        "items":   [item.dict() for item in items]
    }
    setitems_collection.update_one(
        {"setitems_id": set_id},
        {"$set": updated}
    )
    # ส่งกลับข้อมูลใหม่
    return {**{"setitems_id": set_id}, **updated}
#-----------------------------------------------------------------------
@app.patch(
    "/sets/{set_id}",
    response_model=ItemBuild,
    summary="อัปเดตเฉพาะบางฟิลด์ของชุดไอเทม",
)
def patch_item_build(set_id: int, payload: PatchItemBuild):
    # 1) ดึงของเดิมมาจาก DB
    doc = setitems_collection.find_one({"setitems_id": set_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Set not found")

    update_data = {}
    # 2) ถ้ามี hero_id ใหม่ ให้อัปเดต
    if payload.hero_id is not None:
        update_data["hero_id"] = payload.hero_id

    # 3) ถ้ามี item_ids ใหม่ ให้เช็กความยาวและอัปเดต
    if payload.item_ids is not None:
        if len(payload.item_ids) != 6:
            raise HTTPException(422, "item_ids ต้องมี 6 ช่อง")
        # (คุณอาจจะต้องดึงรายละเอียดจาก itemsInfos เหมือน POST/PUT)
        update_data["items"] = payload.item_ids  # หรือแปลงเป็น full model เหมือนเดิม

    # 4) ถ้าไม่มีอะไรให้แก้เลย
    if not update_data:
        raise HTTPException(400, "ไม่มีข้อมูลอะไรให้อัปเดต")

    # 5) บันทึกลง DB
    setitems_collection.update_one(
        {"setitems_id": set_id},
        {"$set": update_data}
    )

    # 6) ดึงของใหม่ส่งกลับ
    return setitems_collection.find_one({"setitems_id": set_id}, {"_id": 0})

#####################################################################
@app.get(
    "/setitems",
    response_model=List[ItemBuild],
    summary="ดึงข้อมูลชุดไอเทมทั้งหมด",
    description="คืนค่าเป็นลิสต์ของทุกเซตไอเทมในฐานข้อมูล"
)
def list_item_builds():
    # Query ทั้งหมด โดยตัดฟิลด์ _id ออก
    cursor = setitems_collection.find({}, {"_id": 0})
    # แปลงเป็น list ของ dict แล้วให้ FastAPI map เป็น ItemBuild ให้อัตโนมัติ
    return list(cursor)