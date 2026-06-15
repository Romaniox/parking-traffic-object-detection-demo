"""
Regression test: list_detections must NOT trigger N+1 queries when accessing
object relationships.  We count SQL statements via SQLAlchemy's event hook and
assert the total stays bounded regardless of the number of rows returned.
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.db import repository
from app.db.engine import Base, init_db


@pytest.fixture
def counted_session():
    """Yields (session, query_counter_list) — each fired SQL appends to the list."""
    engine = create_engine("sqlite:///:memory:")
    init_db(engine)
    factory = sessionmaker(engine)

    queries: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def _count(conn, cursor, statement, *_):
        queries.append(statement)

    with factory() as s:
        yield s, queries


def _insert(session, rid: str, n_objects: int = 2) -> None:
    repository.create_detection(
        session,
        detection_id=rid,
        original_filename=f"{rid}.png",
        original_path=f"/data/{rid}/original.png",
        annotated_path=f"/data/{rid}/annotated.jpg",
        model_name="stub",
        model_weights=None,
        count=n_objects,
        objects=[(f"cls{i}", 1) for i in range(n_objects)],
        inference_ms=5.0,
        image_width=100,
        image_height=80,
        status="success",
        error=None,
    )
    session.commit()


def test_list_detections_does_not_n_plus_1(counted_session):
    """
    With 5 detections list_detections should use at most 2 SELECT statements
    (one for Detection rows, one batch-load for DetectionObject), not 6.
    """
    session, queries = counted_session

    for i in range(5):
        _insert(session, f"det{i}", n_objects=3)

    queries.clear()  # reset counter — we only care about the list call
    rows = repository.list_detections(session, limit=10)

    # Access the relationship so lazy-load would be triggered if not eager-loaded.
    for row in rows:
        _ = [o.cls for o in row.objects]

    n_selects = sum(1 for q in queries if q.strip().upper().startswith("SELECT"))
    assert n_selects <= 2, (
        f"Expected ≤2 SELECT statements for list_detections, got {n_selects}.\n"
        f"Queries fired:\n" + "\n---\n".join(queries)
    )
