def test_login_page_renders(client):
    """
    Verifies that the login landing page renders successfully.
    """
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "Login" in response.text

def test_login_success(client):
    """
    Tests that a user with correct credentials can login successfully,
    is redirected to the dashboard, and receives the session cookie.
    """
    login_data = {
        "email": "testowner@stockmate.com",
        "password": "owner123"
    }
    response = client.post("/auth/login", data=login_data, follow_redirects=False)
    
    assert response.status_code == 303
    assert response.headers["location"] == "/owner/dashboard"
    assert "access_token" in response.cookies

def test_login_wrong_credentials(client):
    """
    Verifies that login fails when password or email is incorrect.
    """
    login_data = {
        "email": "testowner@stockmate.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", data=login_data)
    
    assert response.status_code == 200
    assert "Invalid email or password" in response.text
    assert "access_token" not in response.cookies

def test_logout(client):
    """
    Verifies that logging out deletes the session cookie and redirects to login.
    """
    # 1. Login to establish cookie
    client.post("/auth/login", data={"email": "testemployee@stockmate.com", "password": "employee123"})
    assert "access_token" in client.cookies
    
    # 2. Call logout
    response = client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"
    
    # Cookie should be deleted/expired (Starlette sets value to empty string and max-age=0)
    assert "access_token" not in client.cookies or client.cookies["access_token"] == ""
