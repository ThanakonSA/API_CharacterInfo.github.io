import json
import pandas as pd
from models.herofullmodel   import convert_row_to_heroes
from models.heromainmodel   import HeroMainModel
from models.Itemsfullmodel  import convert_row_to_item
from models.setmodel        import CreateItemBuild
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
HERO_XLSX = os.path.join(BASE_DIR, 'HeroInfo.xlsx')
ITEM_XLSX = os.path.join(BASE_DIR, 'ItemInfo.xlsx')
BUILD_XLSX = os.path.join(BASE_DIR, 'SetBuilds.xlsx')

OUT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'docs', 'api'))
os.makedirs(OUT_DIR, exist_ok=True)

def export_heroes_full():
    df = pd.read_excel(HERO_XLSX, sheet_name=0)
    data = [convert_row_to_heroes(row) for _, row in df.iterrows()]
    with open(os.path.join(OUT_DIR, 'heroes.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_heroes_main():
    df = pd.read_excel(HERO_XLSX, sheet_name=0)
    data = [{
      **HeroMainModel(
           hero_id   = str(row.get("Hero_ID","")),
           hero_name = row.get("HeroName",""),
           role      = row.get("Role",""),
           specialty = row.get("Specialty",""),
           lane_recc = row.get("Lane_Recc",""),
           icon      = row.get("Iconhero",""),
           full      = row.get("Imagehero","")
      ).dict()
    } for _, row in df.iterrows()]
    with open(os.path.join(OUT_DIR, 'heroes_main.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_items():
    df = pd.read_excel(ITEM_XLSX, sheet_name=0)
    data = [convert_row_to_item(row) for _, row in df.iterrows()]
    with open(os.path.join(OUT_DIR, 'items.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_builds():
    if not os.path.exists(BUILD_XLSX):
        print(f"⚠️  {BUILD_XLSX} not found — skipping builds export")
        return
    # สมมติคุณมีตาราง builds.csv หรือ .xlsx ที่เก็บ setitems
    df = pd.read_excel(BUILD_XLSX, sheet_name=0)
    data = []
    for _, row in df.iterrows():
        build = CreateItemBuild(
            hero_id = str(row.get("Hero_ID","")),
            item_ids= [str(row.get(f"Item{i+1}_ID","")) for i in range(6)]
        ).model_dump()   # ถ้าใช้ Pydantic V2: .model_dump()
        data.append(build)
    out_path = os.path.join(OUT_DIR, 'builds.json')
    with open(out_path,'w',encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    export_heroes_full()
    export_heroes_main()
    export_items()
    export_builds()   # ตอนนี้จะข้ามถ้าไฟล์ไม่เจอ
    print("✅ Done!")