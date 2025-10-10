import streamlit as st
import subprocess
import sys
import os
import time

# --- Page Configuration ---
st.set_page_config(
    page_title="ML Streaming Pipeline Controller",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 ML Streaming Pipeline Controller")
st.caption("A Streamlit interface to manage the Kafka-gRPC inference pipeline.")

# --- Session State Initialization ---
if 'server_proc' not in st.session_state:
    st.session_state.server_proc = None
if 'consumer_proc' not in st.session_state:
    st.session_state.consumer_proc = None
if 'producer_proc' not in st.session_state:
    st.session_state.producer_proc = None
# Store file handles for logs
if 'log_files' not in st.session_state:
    st.session_state.log_files = {}

# --- Helper Functions ---
def start_process(command, process_key, log_file_name):
    """Starts a subprocess, redirecting its output to a log file."""
    if st.session_state[process_key] is None or st.session_state[process_key].poll() is not None:
        # Open a log file in write mode
        log_file = open(log_file_name, "w")
        st.session_state.log_files[process_key] = log_file
        
        # Determine the command to run
        if ".py" in command: # Simple script
            run_command = [sys.executable, command]
        else: # Module
            run_command = [sys.executable, "-m"] + command.split()

        process = subprocess.Popen(
            run_command,
            stdout=log_file,
            stderr=subprocess.STDOUT
        )
        st.session_state[process_key] = process
        st.info(f"Started {process_key.replace('_proc','')} with PID: {process.pid}")
    else:
        st.warning(f"{process_key.replace('_proc','')} is already running.")

def stop_process(process_key):
    """Stops a subprocess and closes its log file."""
    if st.session_state[process_key] is not None and st.session_state[process_key].poll() is None:
        pid = st.session_state[process_key].pid
        st.session_state[process_key].terminate()
        try:
            st.session_state[process_key].wait(timeout=5)
            st.success(f"Stopped {process_key.replace('_proc','')} (PID: {pid}).")
        except subprocess.TimeoutExpired:
            st.session_state[process_key].kill()
            st.warning(f"Force-killed {process_key.replace('_proc','')} (PID: {pid}).")

        st.session_state[process_key] = None
        # Close the associated log file
        if process_key in st.session_state.log_files:
            st.session_state.log_files[process_key].close()
            del st.session_state.log_files[process_key]

def read_log_file(log_file_name):
    """Reads the content of a log file."""
    if os.path.exists(log_file_name):
        with open(log_file_name, "r") as f:
            return f.read()
    return ""

# --- UI Layout ---
col1, col2, col3 = st.columns(3)

with col1:
    st.header("1. Inference Server")
    if st.button("▶️ Start Server", key="start_server"):
        start_process("inference_service.server", "server_proc", "server.log")

with col2:
    st.header("2. Stream Consumer")
    if st.button("▶️ Start Consumer", key="start_consumer"):
        start_process("streaming_simulator.consumer", "consumer_proc", "consumer.log")

with col3:
    st.header("3. Stream Producer")
    if st.button("▶️ Start Producer", key="start_producer"):
        producer_command = os.path.join("streaming_simulator", "producer.py")
        start_process(producer_command, "producer_proc", "producer.log")

st.divider()

# --- Stop All Button ---
if st.button("⏹️ Stop All Services", type="primary"):
    stop_process("producer_proc")
    stop_process("consumer_proc")
    stop_process("server_proc")

st.divider()

# --- Log Display ---
st.header("Process Logs")

log_col1, log_col2, log_col3 = st.columns(3)

with log_col1:
    with st.expander("Inference Server Logs", expanded=True):
        log_content = read_log_file("server.log")
        st.text_area("Server Output", value=log_content, height=300, key="server_log_area", disabled=True)

with log_col2:
    with st.expander("Consumer Logs", expanded=True):
        log_content = read_log_file("consumer.log")
        st.text_area("Consumer Output", value=log_content, height=300, key="consumer_log_area", disabled=True)

with log_col3:
    with st.expander("Producer Logs", expanded=True):
        log_content = read_log_file("producer.log")
        st.text_area("Producer Output", value=log_content, height=300, key="producer_log_area", disabled=True)

# A small loop to force a re-run and update the logs by re-reading the files
time.sleep(1)
st.rerun()