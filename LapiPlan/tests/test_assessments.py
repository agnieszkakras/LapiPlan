import pytest
from lapiplan import db


def test_assessment_roundtrip_and_migration(tmp_path):
    path=tmp_path/'app.db'
    db.init_db(path)
    db.init_assessments(path)
    db.init_assessments(path)
    child=db.add_child('Demo','2012-02-02',40,path)
    ident=db.add_assessment(child,'2027-03-11','olympiad','Chemistry Olympiad','Chemistry','09:00','Stage I',path)
    found=db.list_assessments(child,'2027-01-01','2027-12-31',path)
    assert len(found)==1 and found[0]['id']==ident
    assert found[0]['event_time']=='09:00'
    db.set_assessment_completed(ident,child,True,path)
    assert db.list_assessments(child,db_path=path)[0]['completed']==1
    db.delete_assessment(ident,child,path)
    assert db.list_assessments(child,db_path=path)==[]


def test_invalid_assessment(tmp_path):
    path=tmp_path/'app.db'
    db.init_db(path)
    db.init_assessments(path)
    child=db.add_child('Demo','2012-02-02',40,path)
    with pytest.raises(ValueError):
        db.add_assessment(child,'2027-06-02','invalid','Title',db_path=path)
    with pytest.raises(ValueError):
        db.add_assessment(child,'2027-06-02','test',' ',db_path=path)
