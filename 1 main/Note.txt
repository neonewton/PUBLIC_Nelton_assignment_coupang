# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Check Python Version
python3 -V

# Install Required Packages
pip install -r requirements.txt



r"""
MAC:
open -a "Google Chrome" --args \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/chrome-debug-profile"
then
curl http://127.0.0.1:9222/json
WINDOWS:
& 'C:\Program Files\Google\Chrome\Application\chrome.exe' `
  --remote-debugging-port=9222 `
  --user-data-dir="C:\Users\Neone\chrome-debug-profile"
then
curl http://127.0.0.1:9222/json

"""


# 3) Setup Chrome WebDriver to attach to existing debug session
#macos-----
chrome_driver_path = "/Users/neltontan/Driver/chromedriver-mac-arm64/chromedriver"
#windows-----
# chrome_driver_path = "C:\WebDrivers\chromedriver-win64\chromedriver.exe"

global driver
service = Service(executable_path=chrome_driver_path)
options = Options()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(service=service, options=options)
print("✅ Chrome WebDriver started")
log("✅ Chrome WebDriver started")

