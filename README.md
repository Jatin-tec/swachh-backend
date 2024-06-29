# Flask REST App

This is a Flask REST app that provides endpoints for interacting with the Swachh backend.

## Setup

To set up the project, follow these steps:

1. Clone the repository:

    ```shell
    git clone https://github.com/Jatin-tec/swachh-backend.git
    
    cd swachh-backend
    ```

2. Create a virtual environment:

    ```shell
    virtualenv venv
    ```

3. Activate the virtual environment:

    ```shell
    source venv/bin/activate
    ```

4. Install the required dependencies:

    ```shell
    pip install -r requirements.txt
    ```

5. Start the database using Docker Compose:

    ```shell
    docker-compose up --build
    ```

## Usage

To run the Flask app, execute the following command:

```shell
python app.py
```

The app will start running on `http://localhost:5000`.

## API Endpoints

The following endpoints are available:

- `GET /api/users`: Get a list of all users.
- `GET /api/users/{id}`: Get details of a specific user.
- `POST /api/users`: Create a new user.
- `PUT /api/users/{id}`: Update an existing user.
- `DELETE /api/users/{id}`: Delete a user.

Feel free to explore and test these endpoints using tools like Postman or cURL.
