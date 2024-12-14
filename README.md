**# CMW500_Network_Analyzer**
Comprehensive Network Analysis for IoT Modules using CMW500.

**Overview**
This project provides a tool to automate and simplify the verification of smart meter modules and other IoT devices using the Rohde & Schwarz CMW500 Communication Tester. 
It focuses on critical network parameters such as:
RSRP (Reference Signal Received Power)
RSRQ (Reference Signal Received Quality)
Throughput Measurements (DL/UL)
Custom Signal Strength and Performance Metrics
The application is designed to enhance testing efficiency and accuracy while minimizing manual intervention.

**Features**
RSRP and RSRQ Measurements
Automates the process of measuring signal strength and quality.
Throughput Testing
Validates module performance by assessing upload and download speeds.
Configurable Test Parameters
Supports flexible configuration for frequencies, power levels, bandwidth, and more.
Real-Time Monitoring
Displays live results for instant verification.
Report Generation
Automatically creates reports with graphs and key metrics in CSV and image formats.
User-Friendly Interface
Simplified UI for seamless operation.

**Getting Started
Prerequisites**
Rohde & Schwarz CMW500 Communication Tester.
Installed Python environment (>=3.8).
Dependencies listed in requirements.txt.
View results in real-time and export them as reports.

**Folder Structure**
CMW500_Module_Performance_Tester/
├── CableLoss_Multifrequency_Graphgeneration.py  # Measurement script
├── Config.json                                  # Default configuration file
├── LICENSE                                      # Open-source license
├── README.md                                    # Project documentation
├── requirements.txt                             # Dependencies
├── UI_Code.py                                   # User interface script
├── Reports/                                     # Auto-generated reports (CSV, images)

**Usage**
Connect CMW500 to Netwoirk as this will enable this testing anywhere in the network range. 
Open the application and input the required parameters such as CMWIP, frequency, power levels, and bandwidth.
Select the metrics you want to measure (RSRP, RSRQ, Throughput, etc.).
Click on "Run Measurement" to start testing.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Author
Developed by:
Mr. Shubham Kumar Bhardwaj
https://www.linkedin.com/in/shubham-kumar-bhardwaj-773368335/
[GitHub Repository](https://github.com/ThorPandit?tab=repositories)
