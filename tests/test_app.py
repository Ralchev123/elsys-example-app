import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import main


from pathlib import Path

client = TestClient(main.app)

def setup_tmp_storage(tmp_path):
    # пренасочваме storage директорията към tmp_path за изолация
    main.STORAGE_DIR = Path(tmp_path / "storage")
    main.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

def test_health(tmp_path):
    setup_tmp_storage(tmp_path)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

def test_list_files_initially_empty(tmp_path):
    setup_tmp_storage(tmp_path)
    r = client.get("/files")
    assert r.status_code == 200
    data = r.json()
    assert "files" in data and isinstance(data["files"], list)
    assert data["count"] == 0

def test_upload_file_and_list(tmp_path):
    setup_tmp_storage(tmp_path)
    p = tmp_path / "a.txt"
    p.write_text("hello world")
    with open(p, "rb") as f:
        r = client.post("/files", files={"file": ("a.txt", f, "text/plain")})
    assert r.status_code == 200
    data = r.json()
    assert data["filename"] == "a.txt"
    # now list
    r2 = client.get("/files")
    assert r2.status_code == 200
    l = r2.json()
    assert "a.txt" in l["files"]
    assert l["count"] == 1

def test_retrieve_uploaded_file(tmp_path):
    setup_tmp_storage(tmp_path)
    p = tmp_path / "b.txt"
    p.write_text("content-123")
    with open(p, "rb") as f:
        client.post("/files", files={"file": ("b.txt", f, "text/plain")})
    r = client.get("/files/b.txt")
    assert r.status_code == 200
    assert b"content-123" in r.content

def test_metrics_includes_counters(tmp_path):
    setup_tmp_storage(tmp_path)
    # create one file for metrics
    p = tmp_path / "c.txt"
    p.write_text("x"*10)
    with open(p, "rb") as f:
        client.post("/files", files={"file": ("c.txt", f, "text/plain")})
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    assert "files_stored_total" in data
    assert "files_current" in data
    assert data["files_current"] == 1
