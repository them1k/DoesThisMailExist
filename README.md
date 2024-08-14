<p align="center">
  <img src="https://raw.githubusercontent.com/them1k/assets/main/logo_dtme.png" alt="dtme"/>
</p>

## Description

This is a framework for verifying the existence of accounts on Google (gmail and workspace) and Microsoft (outlook, hotmail, Office 365...) using Selenium and Chromedriver based in timings and responses.

## Requirements

- `Python 3.x`
- `requests`
- `beautifulsoup4`
- `selenium`
- `colorama`
- `dnspython`

## Installation

**Clone the Repository**

   ```bash
   git clone https://github.com/them1k/DoesThisMailExist.git
   cd your_repository
   ```

**Install Dependencies**

Make sure you have Python 3.x and then install the dependencies using pip:

   ```bash
   python3 -m pip install requirements.txt
   ```

**Chromedriver Setup**

You dont need to have `Chromedriver` installed, the script will automatically download the latest version of `Chromedriver` automatically.

## Usage

**Run the Script**

Execute the main script with the following command:

   ```bash
   python3 DTME.py
   ```

**Main Menu**

The script will present a main menu with the following options:

    1: Verify Google Accounts
    2: Verify Microsoft Accounts
    3: I don't know the server, Do it for me!
    4: Update Chromedriver
    5: Install requirements
    6: Update app
    7: Exit

**Account Verification**

    Option 1: Verify the existence of Google accounts. Enter the path to the file containing email addresses and the path where results will be saved.
    Option 2: Verify the existence of Microsoft Office 365 accounts. Enter the path to the file containing email addresses and the path where results will be saved.
    Option 3: Read the first line of the txt provided and check the spf and dns records to verify the mail server being used. After this it automatically selects option 1 or 2 depending on the result.
    
**Update Chromedriver**

    Download and install the latest version of Chromedriver for your system.

**Install requirements**

    Install the requirements for you if you have not yet done so ;)

**Update the Application**

    Update the application from the GitHub repository.

**Exit**

    Exit the script.

## Notes

Ensure you have an internet connection to download necessary files and for account verification.

To use a specific proxy, you will be prompted to enter the proxy address in the format http://user:pass@proxyserver:port or http://proxyserver:port or proxyserver:port

The script checks if the proxy is accessible before proceeding with account verification.

The use of free proxies is available, but neither the integrity of the results nor the confidentiality of the results is guaranteed. Use it at your own risk and if you know what you are doing :)

The output is always saved even if there is an error, so we avoid data loss if the script fails or we have an internet outage in the middle of the process.

## Disclaimer

You may not use this application for non-educational purposes.

## Contributing

If you wish to contribute to this project, please open an issue or submit a pull request through GitHub.
