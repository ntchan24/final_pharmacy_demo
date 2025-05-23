import os
import subprocess
from datetime import datetime

def create_backup():
    # Create a backup
    subprocess.run(['heroku', 'pg:backups:capture'])
    
    # Get the latest backup URL
    result = subprocess.run(['heroku', 'pg:backups:url'], capture_output=True, text=True)
    backup_url = result.stdout.strip()
    
    # Create a filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'backup_{timestamp}.dump'
    
    # Download the backup
    subprocess.run(['curl', '-o', filename, backup_url])
    
    print(f'Backup created: {filename}')

if __name__ == '__main__':
    create_backup() 