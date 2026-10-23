import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def backup_database():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("DATABASE_URL not configured in .env file.")
        return

    # Parse MySQL connection parameters from DATABASE_URL
    # Format: mysql+pymysql://username:password@localhost:3306/school_college_erp
    try:
        raw_conn = db_url.split("://")[1]
        user_pass, host_db = raw_conn.split("@")
        user, password = user_pass.split(":") if ":" in user_pass else (user_pass, "")
        host_port, db_name = host_db.split("/")
        host = host_port.split(":")[0] if ":" in host_port else host_port
        
        backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backups'))
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f"{db_name}_backup_{timestamp}.sql")
        
        # Construct mysqldump command
        cmd = ["mysqldump", f"-h{host}", f"-u{user}"]
        if password:
            cmd.append(f"-p{password}")
        cmd.extend([db_name, f"--result-file={backup_file}"])
        
        print(f"Starting database backup for '{db_name}'...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"SUCCESS: Database backup created successfully at:\n{backup_file}")
        else:
            print(f"ERROR: Backup failed!\n{result.stderr}")
            print("Note: Ensure 'mysqldump' utility is installed and added to system PATH.")
            
    except Exception as e:
        print(f"Exception during backup execution: {str(e)}")

if __name__ == '__main__':
    backup_database()