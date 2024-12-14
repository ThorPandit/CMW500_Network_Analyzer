# Updated Main Code
import pyvisa
import logging
import json
import time

# Configure the logging settings
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format of log messages
)

# Load configuration file
def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        exit(1)
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON: {e}")
        exit(1)

config = load_config()

rm = pyvisa.ResourceManager()
cmw = rm.open_resource(config["device_address"])
print(cmw.query("*IDN?"))
cmw.write("*RST;*OPC;*CLS")
logging.info("Logging L.15: RST, OPC and CLS fired")
print("Identity:", cmw.query("*IDN?"))  # Verify device is responsive
print("Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
cmw.timeout = 30000  # Increase timeout to 30 seconds

# RF Signal Generator
cmw.write("SOURce:LTE:SIGN:CELL:STATe ON;*OPC")
logging.info("Logging L.21: Activating DL LTE channel")
try:
    if cmw.query("SOURce:LTE:SIGN:CELL:STATe:ALL?"):
        print("DL LTE channel enabled, STATUS:", cmw.query("SOURce:LTE:SIGN:CELL:STATe:ALL?"))
        cmw.write(f"CONFigure:LTE:SIGN:PCC:BAND {config['band']}")  # Band configured dynamically
        logging.info(f"Logging L.27: {config['band']} Configured")
        cmw.timeout = 30000

        cmw.write(f"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel {config['power_level']}")  # Set RS EPRE
        logging.info(f"Logging L.33: Power Level Set to {config['power_level']} dBm")
        cmw.write("SOURce:LTE:SIGN1:CELL:STATe ON")
        cmw.timeout = 50000

        # Query IPv4 and IPv6 address

        # Query RSRP and RSRQ with Retry Mechanism
        max_retries = 5
        retry_delay = 2  # seconds
        for attempt in range(max_retries):
            UE_IPV4 = cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV4?')
            UE_IPV6 = cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV6?')
            if "NAV" not in UE_IPV4 and "NAV" not in UE_IPV6:
                print(f"IPV4 address: {UE_IPV4}, IPV6 address: {UE_IPV6}")
                break
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: IPV4 or IPV6 not available, retrying in {retry_delay}s...")
                time.sleep(retry_delay)

        if "NAV" in UE_IPV4 or "NAV" in UE_IPV6:
            print("IPV4 and/or IPV6 are still not available after retries. Please check the configuration.")


        # Query UE IMEI and IMSI Number
        UE_IMEI = cmw.query('SENSe:LTE:SIGN1:UESinfo:IMEI?')
        UE_IMSI = cmw.query('SENSe:LTE:SIGN1:UESinfo:IMSI?')
        print(f"NIC of IMEI: {UE_IMEI} & SIM of IMSI: {UE_IMSI}")
        cmw.timeout = 1000

        # UE Report enable settings 1.Reporting Interval
        cmw.write("CONFigure:LTE:SIGN1:UEReport:RINTerval I640")  # Example: 640 ms
        print("RINTerval Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 1000  # Increase timeout to 1 seconds

        # Measurement Gap Enable (Optional)
        cmw.write("CONFigure:LTE:SIGN1:UEReport:MGENable ON")
        print("MGENable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 1000  # Increase timeout to 1 seconds

        # Measurement Gap Period (Optional)
        cmw.write("CONFigure:LTE:SIGN1:UEReport:MGPeriod G040")
        print("MGPeriod Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 1000  # Increase timeout to 1 seconds

        cmw.write('CONFigure:LTE:SIGN1:UEReport:ENABle ON')
        print("UEReport Enable Errors:", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
        cmw.timeout = 10000  # Increase timeout to 10 seconds

        # Query RSRP and RSRQ with Retry Mechanism
        max_retries = 5
        retry_delay = 2  # seconds
        for attempt in range(max_retries):
            RSRP_RCOM1 = cmw.query("SENSe:LTE:SIGN1:UEReport:PCC:RSRP?")
            RSRQ_RCOM1 = cmw.query("SENSe:LTE:SIGN1:UEReport:PCC:RSRQ?")
            if "NAV" not in RSRP_RCOM1 and "NAV" not in RSRQ_RCOM1:
                print(f"RSRP: {RSRP_RCOM1}, RSRQ: {RSRQ_RCOM1}")
                break
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: RSRP or RSRQ not available, retrying in {retry_delay}s...")
                time.sleep(retry_delay)

        if "NAV" in RSRP_RCOM1 or "NAV" in RSRQ_RCOM1:
            print("RSRP or RSRQ still not available after retries. Please check the configuration.")

        # Query DL/UL Throughput
        full_DL_throughput = cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:DL:ALL?")
        full_UL_throughput = cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:UL:ALL?")
        print(f"DL Throughput: {float(full_DL_throughput) * 1e-3:.2f} Mbps")
        print(f"UL Throughput: {float(full_UL_throughput) * 1e-3:.2f} Mbps")

        # Query SINR and CQI
        ##CQI = cmw.query("SENSe:LTE:SIGN1:UEReport:PCC:CQI?")
        #print(f"SINR: {SINR}, CQI: {CQI}")

        # Log results to CSV
        import csv
        from datetime import datetime

        with open("network_measurements.csv", "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Timestamp", "RSRP", "RSRQ", "SINR", "CQI", "DL_Throughput", "UL_Throughput"])
            writer.writerow([
                datetime.now().isoformat(),
                RSRP_RCOM1, RSRQ_RCOM1, #SINR, CQI,
                f"{float(full_DL_throughput) * 1e-3:.2f}",
                f"{float(full_UL_throughput) * 1e-3:.2f}"
            ])
        print("Measurements saved to network_measurements.csv")

except pyvisa.errors.VisaIOError as e:
    print("VISA Communication Error:", str(e))
finally:
    # Close the connection
    cmw.close()