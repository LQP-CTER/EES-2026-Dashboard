import os
import sys
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import toml

def init_firebase():
    """Initialize Firebase using credentials from secrets.toml"""
    if firebase_admin._apps:
        return firestore.client()
        
    secrets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.streamlit', 'secrets.toml'))
    with open(secrets_path, 'r', encoding='utf-8') as f:
        secrets = toml.load(f)
        
    firebase_config = secrets.get('firebase')
    if not firebase_config:
        raise ValueError("Firebase configuration not found in secrets.toml")
        
    if "\\n" in firebase_config['private_key']:
        firebase_config['private_key'] = firebase_config['private_key'].replace('\\n', '\n')
        
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
    return firestore.client()

def upload_dataframe_to_firestore(db, df: pd.DataFrame, collection_name: str, batch_size=500):
    print(f"Uploading {len(df)} rows to collection '{collection_name}'...")
    df = df.where(pd.notnull(df), None)
    records = df.to_dict(orient='records')
    
    total = len(records)
    batch = db.batch()
    count = 0
    uploaded = 0
    
    for i, record in enumerate(records):
        doc_ref = db.collection(collection_name).document()
        batch.set(doc_ref, record)
        count += 1
        
        if count >= batch_size:
            batch.commit()
            uploaded += count
            print(f"  Uploaded {uploaded}/{total}...")
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
        uploaded += count
        print(f"  Uploaded {uploaded}/{total}...")
        
    print(f"Successfully uploaded {total} documents to {collection_name}!\n")

def main():
    print("Initializing Firebase...")
    db = init_firebase()
    
    # 1. Survey Data Setup
    # Hardcode URLs to completely bypass Streamlit dependencies
    central_id = "1wiv9c12jnSe7QFbqD-SHQo2tOWMD5My0pyE5JbmtYkU"
    groups = ['1A', '1B', '2A', '2B', '3A', '3B']
    
    print("\n--- MIGRATING SURVEY DATA ---")
    for group_id in groups:
        sheet_name = f"{group_id} - Data"
        sheet_name_encoded = sheet_name.replace(' ', '%20')
        url = f"https://docs.google.com/spreadsheets/d/{central_id}/gviz/tq?tqx=out:csv&sheet={sheet_name_encoded}"
        
        print(f"Downloading data for Group {group_id} from Google Sheets...")
        try:
            df = pd.read_csv(url)
            if df.empty:
                print(f"Skipping empty dataframe for {group_id}")
                continue
            collection_name = f"survey_{group_id.lower()}"
            upload_dataframe_to_firestore(db, df, collection_name)
        except Exception as e:
            print(f"Error migrating {group_id}: {e}")

    # 2. Upload Workforce Data
    print("\n--- MIGRATING WORKFORCE DATA ---")
    try:
        print("Downloading Workforce Data from Google Sheets...")
        export_url = f"https://docs.google.com/spreadsheets/d/{central_id}/export?format=xlsx"
        try:
            df_wf = pd.read_excel(export_url, sheet_name="Workforce Data", engine="calamine")
        except:
            df_wf = pd.read_excel(export_url, sheet_name="Workforce Data")
            
        if not df_wf.empty:
            upload_dataframe_to_firestore(db, df_wf, "workforce_data")
        else:
            print("Failed to load workforce data.")
    except Exception as e:
        print(f"Error migrating workforce data: {e}")

    print("\n✅ MIGRATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
