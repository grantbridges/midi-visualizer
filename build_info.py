from datetime import datetime

# illustri version info - set in build pipeline
VERSION = "1.0.0-beta.2"
BUILD_DATE = f"{datetime.now().strftime('%b')} {datetime.now().day}, {datetime.now().year} (local)"