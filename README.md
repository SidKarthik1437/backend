# Getting Started with Nexa Application

This guide will walk you through the steps to set up and run the Nexa application on your local machine.

## Prerequisites

- Python 3.x installed
- Docker installed

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/SidKarthik1437/eXcentriX_NEXA_Backend.git
    ```

2. Navigate to the project directory:

    ```bash
    cd eXcentriX_NEXA_Backend
    ```

3. Install all requirements:

    ```bash
    pip install -r requirements.txt
    ```

## Setting up PostgreSQL Database

1. Create a PostgreSQL Docker container:

    ```bash
    docker run --name nexa-postgres -e POSTGRES_DB=nexa -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres
    ```

## Running the Application

1. Run the entrypoint script:

    ```bash
    zsh entrypoint.sh
    # OR
    bash entrypoint.sh
    ```

2. Stop the server by pressing `Ctrl + C`.


## Creating a Superuser

1. Create a superuser for logging in:

    ```bash
    python manage.py createsuperuser
    ```

2. Follow the prompts to set up the superuser account.



## Restarting the Application

1. Run the entrypoint script again:

    ```bash
    bash entrypoint.sh
    ```

2. You can now log in to the application using the superuser credentials.

## Additional Notes

- Make sure to update the Docker container name, PostgreSQL database name, username, and password as needed in the commands above.
- For more information on Django management commands, refer to the [Django documentation](https://docs.djangoproject.com/en/stable/ref/django-admin/).

