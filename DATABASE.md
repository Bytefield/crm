# Database Management

This document contains all the necessary information to manage the PostgreSQL database for the CRM application.

## Database Credentials

### Default Development Configuration
- **Database Name**: `crm`
- **Username**: `postgres`
- **Password**: `postgres`
- **Host**: `localhost`
- **Port**: `5432`
- **Connection String**: `postgres://postgres:postgres@localhost:5432/crm`

## Setup Instructions

### 1. Create Database
```bash
# Create the database (run as postgres user)
sudo -u postgres createdb crm

# Create a new user (optional)
sudo -u postgres createuser --interactive
```

### 2. Set Database Password
```bash
# Set password for postgres user
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

### 3. Environment Variables
Create a `.env` file in the project root with:
```env
DATABASE_URL=postgres://postgres:postgres@localhost:5432/crm
```

## Common Operations

### Connect to Database
```bash
psql -U postgres -d crm
```

### List All Databases
```bash
psql -U postgres -l
```

### Run Migrations
```bash
cargo sqlx migrate run
```

### Create New Migration
```bash
cargo sqlx migrate add <migration_name>
```

### Reset Database (DANGER: Deletes all data!)
```bash
# Drop and recreate the database
dropdb -U postgres crm
createdb -U postgres crm
cargo sqlx migrate run
```

## Backup and Restore

### Create Backup
```bash
pg_dump -U postgres -d crm > crm_backup_$(date +%Y-%m-%d).sql
```

### Restore from Backup
```bash
psql -U postgres -d crm < crm_backup_2023-01-01.sql
```

## Troubleshooting

### Connection Issues
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Check PostgreSQL logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

### Permission Issues
If you encounter permission issues, you may need to update `pg_hba.conf`:
```bash
sudo nano /etc/postgresql/$(ls /etc/postgresql)/main/pg_hba.conf
```

Add or modify the following line for local development:
```
local   all             postgres                                md5
```

Then restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Security Notes
- Never commit sensitive information like passwords to version control
- Use environment variables for production credentials
- Consider using a more secure password in production
- Regularly backup your database
