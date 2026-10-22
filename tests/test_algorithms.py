import math
import pytest
from app.algorithms.scoring import bia_score,bia_category,risk_score,evaluate_disruption


@pytest.mark.parametrize("values,expected",[((0,0,0,0),0),((5,5,5,5),100),((4,5,3,3),80),((5,0,0,0),30),((0,5,0,0),35),((0,0,5,0),20),((0,0,0,5),15)])
def test_bia_weights(values,expected):
    assert bia_score(*values,24,4,1)[0]==expected


@pytest.mark.parametrize("score,category",[(0,"Low"),(24.99,"Low"),(25,"Medium"),(49.99,"Medium"),(50,"High"),(74.99,"High"),(75,"Critical"),(100,"Critical")])
def test_bia_boundaries(score,category):assert bia_category(score)==category


@pytest.mark.parametrize("mtpd,rto,rpo",[(0,1,0),(-1,1,0),(10,0,0),(10,-1,0),(10,11,0),(10,1,-1),(math.nan,1,0),(10,math.inf,0)])
def test_invalid_recovery_targets(mtpd,rto,rpo):
    with pytest.raises(ValueError):bia_score(1,1,1,1,mtpd,rto,rpo)


@pytest.mark.parametrize("bad",[-1,5.1,math.inf,math.nan,"oops",None])
def test_invalid_impact(bad):
    with pytest.raises(ValueError):bia_score(bad,1,1,1,10,2,1)


@pytest.mark.parametrize("l,i,category",[(1,1,"Low"),(1,5,"Low"),(2,3,"Medium"),(2,5,"Medium"),(3,4,"High"),(3,5,"High"),(4,4,"Critical"),(5,5,"Critical")])
def test_risk_boundaries(l,i,category):assert risk_score(l,i)==(l*i,category)


@pytest.mark.parametrize("l,i",[(0,1),(6,1),(1,0),(1,6),(1.5,2),(math.nan,2),(1,math.inf)])
def test_invalid_risk(l,i):
    with pytest.raises(ValueError):risk_score(l,i)


@pytest.mark.parametrize("duration,rto_bad,mtpd_bad",[(0,False,False),(4,False,False),(4.01,True,False),(24,True,False),(24.01,True,True)])
def test_scenario_boundaries(duration,rto_bad,mtpd_bad):
    row=evaluate_disruption(duration,[{"id":1,"name":"P","rto":4,"mtpd":24}])[0]
    assert row["rto_violation"] is rto_bad and row["mtpd_violation"] is mtpd_bad


def test_scenario_unknown_bia():
    row=evaluate_disruption(10,[{"id":1,"name":"P","rto":None}])[0]
    assert row["rto_violation"] is None and "BIA" in row["recommendation"]


def test_negative_disruption():
    with pytest.raises(ValueError):evaluate_disruption(-1,[])
