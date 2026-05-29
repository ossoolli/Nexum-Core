import sqlite3
import pytest
import os
from nexum.memory.store import SovereignMemoryStore

def test_memory_persistence():
    db_path = "/tmp/test_sovereign_memory.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    store = SovereignMemoryStore(db_path)
    store.add_memory("system", "The quick brown fox jumps over the lazy dog.")
    
    results = store.search_memory("fox")
    assert len(results) == 1
    assert "fox" in results[0]["content"]
    
    if os.path.exists(db_path):
        os.remove(db_path)

def test_fts5_search():
    db_path = "/tmp/test_fts5.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    store = SovereignMemoryStore(db_path)
    store.add_memory("agent", "Deploying new architecture to the cloud.")
    store.add_memory("agent", "Monitoring the system health.")
    
    # Test FTS5
    results = store.search_memory("architecture")
    assert len(results) == 1
    assert "Deploying" in results[0]["content"]
    
    results = store.search_memory("system")
    assert len(results) == 1
    assert "health" in results[0]["content"]

    if os.path.exists(db_path):
        os.remove(db_path)
