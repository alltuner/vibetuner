// MongoDB initialization script for development
// This script creates the application database and user

// Switch to the application database
db = db.getSiblingDB('${COMPOSE_PROJECT_NAME:-vibetuner}');

// Create application user with read/write permissions
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: '${COMPOSE_PROJECT_NAME:-vibetuner}'
    }
  ]
});

// Create initial collections (optional)
db.createCollection('users');
db.createCollection('sessions');

print('Database initialization completed for ${COMPOSE_PROJECT_NAME:-vibetuner}');