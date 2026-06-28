def test_category_employee_restricted(client):
    """
    Verifies that Employees are blocked from modifying Categories.
    """
    # Login as employee
    client.post("/auth/login", data={"email": "testemployee@stockmate.com", "password": "employee123"})
    
    # Try to create category
    response = client.post("/categories", data={"name": "Restricted Cat"}, follow_redirects=False)
    assert response.status_code == 403  # ForbiddenException triggered

def test_category_owner_crud(client, db_session):
    """
    Verifies that Owners can add, edit, and delete Categories.
    """
    # 1. Login as Owner
    client.post("/auth/login", data={"email": "testowner@stockmate.com", "password": "owner123"})
    
    # 2. Add Category
    response = client.post("/categories", data={"name": "Electronics"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"].startswith("/categories?success")
    
    # Check category in DB
    from app.models.category import Category
    cat = db_session.query(Category).filter(Category.name == "Electronics").first()
    assert cat is not None
    
    # 3. Edit Category
    response = client.post(f"/categories/{cat.id}/edit", data={"name": "Computers"}, follow_redirects=False)
    assert response.status_code == 303
    
    db_session.refresh(cat)
    assert cat.name == "Computers"
    
    # 4. Delete Category
    response = client.post(f"/categories/{cat.id}/delete", follow_redirects=False)
    assert response.status_code == 303
    
    deleted_cat = db_session.query(Category).filter(Category.id == cat.id).first()
    assert deleted_cat is None
