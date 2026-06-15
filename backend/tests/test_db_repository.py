import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import repository
from app.db.engine import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    with factory() as s:
        yield s


def _new(session, *, request_id, count, objects, status="success"):
    return repository.create_detection(
        session,
        detection_id=request_id,
        original_filename=f"{request_id}.png",
        original_path=f"/data/images/x/{request_id}/original.png",
        annotated_path=f"/data/images/x/{request_id}/annotated.jpg",
        model_name="stub",
        model_weights=None,
        count=count,
        objects=objects,
        inference_ms=12.0,
        image_width=100,
        image_height=80,
        status=status,
        error=None,
    )


def test_create_and_get_detection(session):
    _new(session, request_id="a", count=3, objects=[("person", 2), ("car", 1)])
    session.commit()

    got = repository.get_detection(session, "a")
    assert got is not None
    assert got.count == 3
    assert got.model_name == "stub"
    assert {(o.cls, o.count) for o in got.objects} == {("person", 2), ("car", 1)}


def test_list_detections_newest_first_with_pagination(session):
    for rid in ("a", "b", "c"):
        _new(session, request_id=rid, count=1, objects=[("person", 1)])
        session.commit()

    rows = repository.list_detections(session, limit=2, offset=0)
    assert [r.id for r in rows] == ["c", "b"]  # newest first
    page2 = repository.list_detections(session, limit=2, offset=2)
    assert [r.id for r in page2] == ["a"]


def test_get_missing_returns_none(session):
    assert repository.get_detection(session, "nope") is None
