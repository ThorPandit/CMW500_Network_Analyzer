# Updated Main Code
import pyvisa
import logging
import json
import time
from datetime import datetime
import csv

# Load configuration
def load_config():
    try:
        with open("config.json", "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error("Configuration file not found.")
        exit(1)

config = load_config()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_measurements():
    # Initialize VISA resource
    rm = pyvisa.ResourceManager()
    cmw = rm.open_resource(f"TCPIP::{config["device_address"]}::INSTR")
    timeout = config["timeout"]
    max_retries = config["max_retries"]

    # Reset and initialize device
    cmw.write("*RST;*OPC;*CLS")
    print("Ensure all well: ", cmw.query("SYST:ERR?"))  # Ensure no errors occurred
    cmw.timeout = timeout

    logging.info("Device reset and initialized.")

    results = []

    for band in config["bands"]:
        for power_level in config["power_levels"]:
            try:
                cmw.query("SOURce:LTE:SIGN1:CELL:STATe?")
                # Configure band and power level
                cmw.write(f"CONFigure:LTE:SIGN:PCC:BAND {band}")
                cmw.timeout = timeout
                cmw.write(f"CONFigure:LTE:SIGN:DL:PCC:RSEPre:LEVel {power_level}")
                cmw.timeout = timeout
                logging.info(f"Configured Band: {band}, Power Level: {power_level}")

                cmw.write("SOURce:LTE:SIGN1:CELL:STATe ON")
                cmw.timeout = timeout
                # Query IPv4 and IPv6 address
                retry_delay = 4  # seconds
                for attempt in range(max_retries):
                    cmw.timeout = timeout
                    UE_IPV4 = cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV4?')
                    UE_IPV6 = cmw.query('SENSe:LTE:SIGN:UESinfo:UEADdress:IPV6?')
                    if "NAV" not in UE_IPV4 and "NAV" not in UE_IPV6:
                        print(f"IPV4 address: {UE_IPV4}, IPV6 address: {UE_IPV6}")
                        break
                    else:
                        print(
                            f"Attempt {attempt + 1}/{max_retries}: IPV4 or IPV6 not available, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)

                if "NAV" in UE_IPV4 or "NAV" in UE_IPV6:
                    print("IPV4 and/or IPV6 are still not available after retries. Please check the configuration.")

                # Query UE IMEI and IMSI Number
                UE_IMEI = cmw.query('SENSe:LTE:SIGN1:UESinfo:IMEI?')
                UE_IMSI = cmw.query('SENSe:LTE:SIGN1:UESinfo:IMSI?')
                print(f"NIC of IMEI: {UE_IMEI} & SIM of IMSI: {UE_IMSI}")

                # Perform measurements
                cmw.write("CONFigure:LTE:SIGN1:UEReport:RINTerval I640")
                cmw.write("CONFigure:LTE:SIGN1:UEReport:MGENable ON")
                cmw.write("CONFigure:LTE:SIGN1:UEReport:MGPeriod G040")
                cmw.write('CONFigure:LTE:SIGN1:UEReport:ENABle ON')

                # Query RSRP and RSRQ with Retry Mechanism
                retry_delay = 4  # seconds
                for attempt in range(max_retries):
                    RSRP = cmw.query("SENSe:LTE:SIGN1:UEReport:PCC:RSRP?")
                    RSRQ = cmw.query("SENSe:LTE:SIGN1:UEReport:PCC:RSRQ?")
                    if "NAV" not in RSRP and "NAV" not in RSRQ:
                        print(f"RSRP: {RSRP}, RSRQ: {RSRQ}")
                        break
                    else:
                        print(
                            f"Attempt {attempt + 1}/{max_retries}: RSRP or RSRQ not available, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)

                if "NAV" in RSRP or "NAV" in RSRQ:
                    print("RSRP or RSRQ still not available after retries. Please check the configuration.")
                    RSRP = 0
                    RSRQ = 0

                DL_Throughput = cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:DL:ALL?")
                UL_Throughput = cmw.query("SENSe:LTE:SIGN1:CONNection:ETHRoughput:UL:ALL?")
                cmw.write("SOURce:LTE:SIGN1:CELL:STATe OFF")
                cmw.write('CONFigure:LTE:SIGN1:UEReport:ENABle OFF')

                results.append({
                    "timestamp": datetime.now().isoformat(),
                    "band": band,
                    "power_level": power_level,
                    "RSRP": RSRP.strip(),
                    "RSRQ": RSRQ.strip(),
                    "DL_Throughput": f"{float(DL_Throughput) * 1e-3:.2f} Mbps",
                    "UL_Throughput": f"{float(UL_Throughput) * 1e-3:.2f} Mbps"
                })

                logging.info(
                    f"Measurement Results: Band: {band}, Power Level: {power_level}, RSRP: {RSRP}, RSRQ: {RSRQ}")
            except Exception as e:
                logging.error(f"Measurement failed for Band: {band}, Power Level: {power_level}: {e}")

    # Save results to CSV
    with open("network_measurements.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    logging.info("All measurements completed and saved to network_measurements.csv.")

