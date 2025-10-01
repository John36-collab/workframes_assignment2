


---

📊 CORD-19 Metadata Explorer

An interactive Streamlit application for exploring CORD-19-style metadata.
This tool allows filtering by year, source, and title, generating publication statistics, creating word clouds, and downloading customized datasets.


---

🚀 Features

Filter by year, source, and title keywords

Visualize publication trends by year

Rank top journals with bar charts

Generate word clouds from publication titles

Preview and download filtered metadata in CSV format

LIVE URL: [http://10.250.97.78:8507] 

---

📂 Project Structure

workframes_assignment2/
│
├── scripts/
│   └── app.py          # Main Streamlit application
├── data/
│   └── metadata.csv    # Full dataset (place here if using full data)
├── outputs/
│   └── sample_metadata.csv   # Faster, smaller dataset (preferred)
├── README.md           # Project documentation
└── requirements.txt    # Dependencies


---

⚙️ Installation

1. Clone the repository:

git clone https://github.com/John36-collab/workframes_assignment2.git
cd workframes_assignment2


2. Create and activate a virtual environment (recommended):

python -m venv venv
source venv/bin/activate    # On Linux/Mac
venv\Scripts\activate       # On Windows


3. Install dependencies:

pip install -r requirements.txt




---

▶️ Running the App

Use the following command:

streamlit run scripts/app.py

🔍 Syntax & Structure Breakdown

streamlit → Command-line interface provided by the Streamlit package.

run → Subcommand that tells Streamlit to launch a web app.

scripts/app.py → Path to the Python script that defines your application.


This command starts a lightweight local server, executes app.py, and serves the app in your browser.


---

🌐 Accessing the App

When you run the command, you will see something like this:

You can now view your Streamlit app in your browser.

Local URL: http://localhost:8507
Network URL: http://10.250.97.78:8507

Local URL (http://localhost:8507)

Runs only on your machine.

localhost means “this computer.”

8507 is the port used by the server.


Network URL (http://10.250.97.78:8507)

Accessible by other devices on the same network/WiFi.

Useful for testing or sharing your app within a local environment.




---

📊 Example Usage

Explore yearly publication counts.

Identify top journals by publication volume.

Generate a word cloud of publication titles.

Export filtered metadata for offline analysis.



---

📌 Notes

For faster performance, generate a sample dataset with:

python scripts/explore.py --input data/metadata.csv --outdir outputs --sample_size 5000

This creates outputs/sample_metadata.csv, which the app will prioritize.



---

📝 License

This project is licensed under the MIT License.


---
