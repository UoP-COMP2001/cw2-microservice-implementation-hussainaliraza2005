# Profile Service (COMP2001 Coursework 2)

A RESTful microservice managing user profiles, activities, and saved trails for the Trail Application.

## Overview
This service handles:
- **Profiles:** Creating, reading, updating, and deleting user accounts.
- **Authentication:** Verifies identity via the University Authenticator API.
- **Activities:** Links users to their favorite activities (e.g., Hiking).
- **Saved Trails:** Allows users to save trails (linked by ID).

## Tech Stack
- **Language:** Python 3.9
- **Framework:** Flask + Connexion (OpenAPI 3.0)
- **Database:** MS SQL Server (Schema: `CW2`)
- **Containerization:** Docker

## How to Run (Docker)
The image is hosted on Docker Hub. You can run it using the following commands.

### 1. Pull and run the image

~~~bash
docker pull hussainaliraza/profile-service:latest
docker run --name profile-service -p 8000:8000 hussainaliraza/profile-service:latest
~~~
