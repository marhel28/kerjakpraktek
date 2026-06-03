import os
import re
import uuid
import logging
import httpx
import mmh3
import aiomysql

logger = logging.getLogger(__name__)

# URL of Manticore HTTP port and MySQL port
MANTICORE_URL = os.getenv("MANTICORE_URL", os.getenv("ELASTICSEARCH_URL", "http://manticore:9308"))
# Parse host and port from URL or use defaults
manticore_host = "manticore"
manticore_port = 9306

# If MANTICORE_URL is something like http://manticore:9308, we extract "manticore" as host
match = re.search(r'https?://([^:/]+)', MANTICORE_URL)
if match:
    manticore_host = match.group(1)

def get_manticore_id(id_val) -> int:
    if isinstance(id_val, int):
        return id_val
    if isinstance(id_val, str):
        try:
            uuid_obj = uuid.UUID(id_val)
            return uuid_obj.int & 0x7fffffffffffffff
        except ValueError:
            return mmh3.hash64(id_val.encode('utf-8'))[0] & 0x7fffffffffffffff
    return id_val

def escape_sql_string(val: str) -> str:
    if not val:
        return ""
    return val.replace('\\', '\\\\').replace("'", "''")

import json

SYNONYMS_DICT = {
    "kamera": ["camera", "cctv"],
    "camera": ["kamera", "cctv"],
    "cctv": ["kamera", "camera"],
    "pasang": ["jasa", "setting", "instalasi"],
    "jasa": ["pasang", "setting", "instalasi", "service"],
    "setting": ["jasa", "pasang", "konfigurasi"],
    "instalasi": ["jasa", "pasang"],
    "wifi": ["wireless", "nirkabel", "router", "ap"],
    "wireless": ["wifi", "nirkabel"],
    "kabel": ["lan", "utp", "belden", "cat6", "cat5"],
    "lan": ["kabel", "utp", "cat6", "cat5"],
    "paket": ["bundling", "promo", "hemat"],
    "bundling": ["paket", "promo", "hemat"],
    "murah": ["promo", "diskon", "hemat"],
}

def get_synonyms(word: str) -> list:
    w_clean = word.lower().strip()
    if w_clean in SYNONYMS_DICT:
        return list(set([word] + SYNONYMS_DICT[w_clean]))
    return [word]

def parse_manticore_match_strict(q: str) -> str:
    if not q:
        return ""
    q_clean = re.sub(r'[\\\'"()|\-!@~*&/]', ' ', q)
    words = [w.strip() for w in q_clean.split() if w.strip()]
    if not words:
        return ""
    processed = []
    for w in words:
        syns = get_synonyms(w)
        if len(syns) > 1:
            processed.append(f"( {' | '.join(syns)} )")
        else:
            processed.append(w)
    return " & ".join(processed)

def parse_manticore_match_loose(q: str) -> str:
    if not q:
        return ""
    q_clean = re.sub(r'[\\\'"()|\-!@~*&/]', ' ', q)
    words = [w.strip() for w in q_clean.split() if w.strip()]
    if not words:
        return ""
    processed = []
    for w in words:
        syns = get_synonyms(w)
        if len(syns) > 1:
            processed.append(f"( {' | '.join(syns)} )")
        else:
            processed.append(w)
    return " | ".join(processed)

def parse_manticore_match_wildcard(q: str) -> str:
    if not q:
        return ""
    q_clean = re.sub(r'[\\\'"()|\-!@~*&/]', ' ', q)
    words = [w.strip() for w in q_clean.split() if w.strip()]
    if not words:
        return ""
    processed = []
    for w in words:
        syns = get_synonyms(w)
        expanded = [f"{s}*" for s in syns]
        processed.append(f"( {' | '.join(expanded)} )")
    return " | ".join(processed)

# Fallback helper for compat
def parse_manticore_match(q: str, fields: list = None) -> str:
    match_str = parse_manticore_match_loose(q)
    if fields and match_str:
        field_target = ",".join(fields)
        return f"@{({field_target})} ({match_str})"
    return match_str

def parse_date_to_timestamp(val) -> int:
    if not val:
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    if isinstance(val, str):
        try:
            from datetime import datetime
            val_clean = val.replace('Z', '+00:00')
            dt = datetime.fromisoformat(val_clean)
            return int(dt.timestamp())
        except Exception:
            return 0
    return 0

class ManticoreIndicesClient:
    def __init__(self, client):
        self.client = client

    async def exists(self, index: str):
        try:
            res = await self.client.execute_sql(f"SHOW TABLES LIKE '{index}'")
            return len(res) > 0
        except Exception:
            return False

    async def delete(self, index: str):
        await self.client.execute_sql(f"DROP TABLE IF EXISTS {index}")

    async def create(self, index: str, body: dict = None, settings: dict = None, mappings: dict = None):
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {index} (
            uuid string,
            slug string,
            title text,
            brand text,
            brand_attr string,
            brand_normalized string,
            category_slug string,
            subcategory_slug string,
            type text,
            type_attr string,
            specs json,
            specs_text text,
            original_price int,
            discount_percentage int,
            online_price int,
            stok int,
            terjual int,
            sisa int,
            is_active bool,
            created_at timestamp,
            image_url string
        ) morphology='stem_en' min_prefix_len='2' html_strip='1'
        """
        await self.client.execute_sql(create_sql)
        print(f"✅ Manticore index '{index}' created with optimal schema.")

def format_manticore_doc(doc: dict) -> dict:
    manticore_doc = {}
    for k, v in doc.items():
        if k in ("created_at", "updated_at") and isinstance(v, str):
            manticore_doc[k] = parse_date_to_timestamp(v)
        elif k == "is_active" and isinstance(v, bool):
            manticore_doc[k] = 1 if v else 0
        else:
            manticore_doc[k] = v
            
    # Add attributes for grouping/display and full text searching
    if "brand" in doc:
        brand_val = doc["brand"] or ""
        manticore_doc["brand"] = brand_val
        manticore_doc["brand_attr"] = brand_val
        manticore_doc["brand_normalized"] = brand_val.lower().strip()
        
    if "type" in doc:
        type_val = doc["type"] or ""
        manticore_doc["type"] = type_val
        manticore_doc["type_attr"] = type_val
        
    if "specs" in doc:
        specs = doc["specs"] or {}
        specs_values = []
        if isinstance(specs, dict):
            for val in specs.values():
                if isinstance(val, (str, int, float)):
                    specs_values.append(str(val))
        elif isinstance(specs, str):
            try:
                specs_dict = json.loads(specs)
                for val in specs_dict.values():
                    if isinstance(val, (str, int, float)):
                        specs_values.append(str(val))
            except Exception:
                pass
        manticore_doc["specs_text"] = " ".join(specs_values)
        
    return manticore_doc

class ManticoreClient:
    def __init__(self, url: str, mysql_host: str, mysql_port: int):
        self.url = url
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.http_client = httpx.AsyncClient(timeout=15.0)
        self.indices = ManticoreIndicesClient(self)

    async def execute_sql(self, sql: str) -> list:
        try:
            conn = await aiomysql.connect(
                host=self.mysql_host,
                port=self.mysql_port,
                user='root',
                password='',
                db='',
                autocommit=True
            )
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql)
                res = await cur.fetchall()
            conn.close()
            return list(res) if res else []
        except Exception as e:
            logger.error(f"Manticore execute_sql error: {e}. Query: {sql}")
            raise

    async def index(self, index: str, id: str, document: dict):
        doc_id = get_manticore_id(id)
        manticore_doc = format_manticore_doc(document)
        
        payload = {
            "index": index,
            "id": doc_id,
            "doc": manticore_doc
        }
        res = await self.http_client.post(f"{self.url}/replace", json=payload)
        res.raise_for_status()

    async def update(self, index: str, id: str, doc: dict, ignore: list = None):
        doc_id = get_manticore_id(id)
        manticore_doc = format_manticore_doc(doc)
                
        payload = {
            "index": index,
            "id": doc_id,
            "doc": manticore_doc
        }
        try:
            res = await self.http_client.post(f"{self.url}/update", json=payload)
            if ignore and res.status_code in ignore:
                return
            res.raise_for_status()
        except Exception as e:
            if ignore and isinstance(e, httpx.HTTPStatusError) and e.response.status_code in ignore:
                return
            raise

    async def delete(self, index: str, id: str, ignore: list = None):
        doc_id = get_manticore_id(id)
        payload = {
            "index": index,
            "id": doc_id
        }
        try:
            res = await self.http_client.post(f"{self.url}/delete", json=payload)
            if ignore and res.status_code in ignore:
                return
            res.raise_for_status()
        except Exception as e:
            if ignore and isinstance(e, httpx.HTTPStatusError) and e.response.status_code in ignore:
                return
            raise

    async def delete_by_query(self, index: str, body: dict, wait_for_completion: bool = False):
        slug = None
        try:
            should_list = body.get("query", {}).get("bool", {}).get("should", [])
            for term_dict in should_list:
                term = term_dict.get("term", {})
                for k, v in term.items():
                    if k.startswith("category_slug"):
                         slug = v
                         break
                if slug:
                    break
        except Exception:
            pass
        
        if slug:
            sql = f"DELETE FROM {index} WHERE category_slug = '{escape_sql_string(slug)}'"
            await self.execute_sql(sql)

    async def close(self):
        await self.http_client.aclose()

es_client = ManticoreClient(MANTICORE_URL, manticore_host, manticore_port)

async def init_es_index():
    await es_client.indices.create(index="products")

async def reindex_es(drop_first: bool = False):
    index_name = "products"
    if drop_first:
        await es_client.indices.delete(index=index_name)
        print(f"🗑️  Index '{index_name}' deleted.")
    await init_es_index()