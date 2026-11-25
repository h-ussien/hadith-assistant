"""Application layer: orchestrates queries and validates catalog additions."""
from . import data,domain

def search(kind,query):
    if kind not in ('hadith','quote'):raise ValueError('Invalid search category')
    if not isinstance(query,str) or not 3<=len(query.strip())<=2000:raise ValueError('Enter 3–2000 characters')
    return domain.find_matches(query,data.get_all(kind))

def create_quote(payload):
    fields=['passage','book','author','volume','page','reference','url','note']
    values={k:str(payload.get(k,'')).strip() for k in fields}
    if not all(values[k] for k in ('passage','book','author','reference')):raise ValueError('Passage, book, author, and reference are required')
    if any(len(v)>2000 for v in values.values()):raise ValueError('Field too long')
    if values['url'] and not values['url'].startswith(('https://','http://')):raise ValueError('URL must start with https:// or http://')
    if payload.get('verified') is not True:
        raise ValueError('Confirm that you checked the quotation against the named edition')
    data.add_quote(**values)
    return {'message':'Reference added to local catalog; independently verify its accuracy.'}

import csv, io, re
from urllib.parse import urlsplit

BOOK_FIELDS=('kind','passage','book','author','chapter','hadith_number','volume','page','edition','url','note')

def import_catalog(filename, content):
    """Import a user-supplied UTF-8 CSV or TXT. No automatic verification claims."""
    if not isinstance(filename,str) or not re.fullmatch(r'[\w.\- ]{1,120}',filename):
        raise ValueError('Invalid filename')
    if len(content.encode('utf-8')) > 2_000_000:
        raise ValueError('File too large (2 MB limit)')
    records=[]
    if filename.lower().endswith('.csv'):
        reader=csv.DictReader(io.StringIO(content.lstrip('\ufeff')))
        if not reader.fieldnames or not {'kind','passage','book','author'}.issubset(reader.fieldnames):
            raise ValueError('CSV needs kind,passage,book,author columns')
        for row in reader:
            if len(records)>=3000: raise ValueError('Maximum 3000 records per import')
            records.append({k:(row.get(k) or '').strip() for k in BOOK_FIELDS})
    elif filename.lower().endswith('.txt'):
        # Plain text is one book excerpt; metadata comes from a separate form.
        raise ValueError('Use CSV for book imports so each passage has traceable source metadata')
    else: raise ValueError('Only UTF-8 CSV files are supported')
    if not records:raise ValueError('No records found')
    for row in records:
        if row['kind'] not in ('hadith','quote') or not all(row[k] for k in ('passage','book','author')):
            raise ValueError('Every row needs kind (hadith/quote), passage, book, author')
        if any(len(v)>12000 for v in row.values()):raise ValueError('A field is too long')
        if row['url'] and urlsplit(row['url']).scheme not in ('http','https'):
            raise ValueError('Invalid source URL')
    data.add_book_passages(records,filename)
    return {'message':f'Imported {len(records)} user-provided passages. Source authenticity is not verified.', 'count':len(records)}

def search_books(kind,query):
    if kind not in ('hadith','quote'):raise ValueError('Invalid search category')
    if not isinstance(query,str) or not 3<=len(query.strip())<=2000:raise ValueError('Enter 3–2000 characters')
    rows=data.get_book_passages(kind)
    results=domain.find_matches(query,rows)
    for r in results:
        r['catalog']='User-imported book passages (unverified)'
        r['full_text_available']=True
    return results


def search_all(kind,query):
    if kind not in ('hadith','quote'):raise ValueError('Invalid search category')
    if not isinstance(query,str) or not 3<=len(query.strip())<=2000:raise ValueError('Enter 3–2000 characters')
    base=domain.find_matches(query,data.get_all(kind))
    imported=domain.find_matches(query,data.get_book_passages(kind))
    for r in base:r['provenance']='Demonstration or manually entered local catalog; verify source'
    for r in imported:r['provenance']='User-imported source; verify original edition'
    return sorted(base+imported,key=lambda r:-r['match_score'])[:50]

def create_hadith(payload):
    fields=['passage','book','author','reference','chapter','hadith_number','url','note']
    values={k:str(payload.get(k,'')).strip() for k in fields}
    if not all(values[k] for k in ('passage','book','author','reference')):raise ValueError('Hadith text, book, author, and reference are required')
    if any(len(v)>12000 for v in values.values()):raise ValueError('Field too long')
    if values['url'] and urlsplit(values['url']).scheme not in ('https','http'):raise ValueError('Invalid source URL')
    if payload.get('verified') is not True:raise ValueError('Confirm that you checked the Hadith against the source')
    data.add_hadith(**values)
    return {'message':'Hadith record added. Verify all citations independently.'}

def delete_record(payload):
    try:record_id=int(payload.get('id'))
    except (TypeError,ValueError):raise ValueError('Invalid record ID')
    if record_id<1:raise ValueError('Invalid record ID')
    if not data.delete_record(record_id):raise ValueError('Record not found')
    return {'message':'Record deleted'}
