from fastapi.testclient import TestClient
from pymongo import MongoClient
from bson import ObjectId
import pytest
from main import app

client = TestClient(app)
mongo_client = MongoClient("mongodb://localhost:27017")
db = mongo_client["Courses"]


def test_get_courses_no_params():
    response = client.get("/courses")
    assert response.status_code == 200

def test_get_courses_sort_by_alphabetical():
    response = client.get("/courses?sort_by=alphabetical")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key = lambda x:x['name']) == courses


def test_get_courses_sort_by_date():
    response = client.get("/courses?sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses

def test_get_courses_sort_by_rating():
    response = client.get("/courses?sort_by=rating")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['rating']['total'], reverse=True) == courses

def test_get_courses_filter_by_domain():
    response = client.get("/courses?domain=mathematics")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])

# def test_get_courses_filter_by_domain_and_sort_by_alphabetical():
#     response = client.get("/courses?domain=mathematics&sort_by=alphabetical")
#     assert response.status_code == 200
#     courses = response.json()
#     assert len(courses) > 0
#     assert all([c['domain'][0] == 'mathematics' for c in courses])
#     assert sorted(courses, key=lambda x: x['name']) == courses
    
def test_get_courses_filter_by_domain_and_sort_by_date():
    response = client.get("/courses?domain=mathematics&sort_by=date")
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses
    
def test_get_course_by_id_exists():
    response = client.get("/courses/64dc966d177072cd2ffa28dd")
    assert response.status_code == 200
    course = response.json()
    name_response = course["name"]

    course_db = db.physics.find_one({"_id": ObjectId('64dc966d177072cd2ffa28dd')})
    name_db = course_db["name"]
    assert name_db==name_response

def test_get_course_by_id_not_exists():
    response = client.get("/courses/6431137ab5da949e5978a280")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Course Not Found!! Sorry.'}

def test_get_chapter_info():
    response = client.get("/courses/64dc966d177072cd2ffa28dd/0")
    assert response.status_code == 200
    chapter = response.json()
    assert chapter['name'] == "Gil Strang's Introduction to Calculus for Highlights for High School"
    assert chapter['text'] == 'Highlights of Calculus'

def test_get_chapter_info_not_exists():
    response = client.get("/courses/64dc966d177072cd2ffa28df/9883")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Chapter not Found in Course: Computer Vision Course'}

def test_rate_chapter():
    course_id = "64dc966d177072cd2ffa28df"
    chapter_id = "0"
    rating = 1

    response = client.post(f"/courses/{course_id}/{chapter_id}?rating={rating}")
    chapter = response.json()

    assert response.status_code ==200
    assert "name" in chapter
    assert "rating" in chapter
    assert "total" in chapter["rating"]
    assert "count" in chapter["rating"]
    assert chapter["rating"]["total"] > 0
    assert chapter["rating"]["count"] > 0

def test_rate_chapter_not_exists():
    response = client.post("/courses/6431137ab5da949e5978a281/990/rate", json={"rating": 1})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}