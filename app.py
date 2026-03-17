import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="BagTrace", layout="wide")

st.title("BagTrace")
st.subheader("Airline Baggage Tracking Intelligence Platform")
st.write(
    "A prototype tool designed to estimate baggage disruption risk based on scan visibility, "
    "connections, transfer complexity, and delay conditions."
)

st.divider()

# Sidebar inputs
st.sidebar.header("Baggage Journey Inputs")

scan_status = st.sidebar.selectbox(
    "Latest Bag Scan Status",
    ["Checked In", "Loaded on Aircraft", "In Transfer", "Arrived at Destination", "Unknown"]
)

connections = st.sidebar.slider(
    "Number of Flight Connections",
    min_value=0,
    max_value=4,
    value=1
)

airport_transfer_complexity = st.sidebar.slider(
    "Airport Transfer Complexity",
    min_value=0,
    max_value=10,
    value=4,
    help="Higher values reflect larger airports, tighter transfers, or more complex connections."
)

flight_delay_minutes = st.sidebar.slider(
    "Flight Delay Minutes",
    min_value=0,
    max_value=300,
    value=35
)

international_transfer = st.sidebar.selectbox(
    "International Transfer Involved?",
    ["No", "Yes"]
)

# Risk scoring logic
risk_score = 0

if scan_status == "Checked In":
    risk_score += 25
elif scan_status == "Loaded on Aircraft":
    risk_score += 10
elif scan_status == "In Transfer":
    risk_score += 20
elif scan_status == "Arrived at Destination":
    risk_score -= 15
elif scan_status == "Unknown":
    risk_score += 35

risk_score += connections * 10
risk_score += airport_transfer_complexity * 3
risk_score += min(flight_delay_minutes * 0.1, 20)

if international_transfer == "Yes":
    risk_score += 15

risk_score = max(0, min(100, int(risk_score)))

# Status classification
if risk_score < 30:
    bag_status = "ON TRACK"
    recommendation = "Baggage journey appears stable with low disruption risk."
elif risk_score < 65:
    bag_status = "DELAY RISK"
    recommendation = "There is moderate baggage disruption risk. Additional transfer or delay monitoring is recommended."
else:
    bag_status = "MISCONNECTED RISK"
    recommendation = "This baggage journey shows high disruption risk. Recovery support and proactive tracking may be needed."

# Layout
col1, col2 = st.columns(2)

with col1:
    st.metric("Bag Disruption Risk Score", f"{risk_score}/100")
    st.metric("Bag Status", bag_status)

    st.markdown("### Recommendation")
    st.info(recommendation)

with col2:
    factor_df = pd.DataFrame({
        "Factor": [
            "Scan Visibility",
            "Connections",
            "Transfer Complexity",
            "Delay Impact",
            "International Transfer"
        ],
        "Impact": [
            25 if scan_status == "Checked In" else 10 if scan_status == "Loaded on Aircraft" else 20 if scan_status == "In Transfer" else -15 if scan_status == "Arrived at Destination" else 35,
            connections * 10,
            airport_transfer_complexity * 3,
            min(flight_delay_minutes * 0.1, 20),
            15 if international_transfer == "Yes" else 0
        ]
    })

    fig, ax = plt.subplots()
    ax.bar(factor_df["Factor"], factor_df["Impact"])
    ax.set_ylabel("Risk Impact")
    ax.set_title("Bag Disruption Risk Drivers")
    plt.xticks(rotation=30, ha="right")
    st.pyplot(fig)

st.divider()

# Baggage journey timeline
st.markdown("## Baggage Journey Timeline")

timeline_df = pd.DataFrame({
    "Journey Stage": ["Check-In", "Departure Sort", "Transfer Point", "Arrival Station"],
    "Status": [
        "Complete",
        "Complete" if scan_status in ["Loaded on Aircraft", "In Transfer", "Arrived at Destination"] else "Pending",
        "In Progress" if scan_status == "In Transfer" else "Pending" if connections > 0 else "Not Required",
        "Complete" if scan_status == "Arrived at Destination" else "Pending"
    ]
})

st.dataframe(timeline_df, use_container_width=True)

st.divider()

# Scenario analysis
st.markdown("## Scenario Comparison")

comparison_df = pd.DataFrame({
    "Scenario": ["Current Journey", "No Delay Scenario", "No Connections Scenario"],
    "Estimated Risk Score": [
        risk_score,
        max(0, risk_score - min(int(flight_delay_minutes * 0.1), 20)),
        max(0, risk_score - (connections * 10))
    ]
})

st.dataframe(comparison_df, use_container_width=True)

fig2, ax2 = plt.subplots()
ax2.plot(comparison_df["Scenario"], comparison_df["Estimated Risk Score"], marker="o")
ax2.set_ylabel("Estimated Risk Score")
ax2.set_title("Bag Journey Scenario Comparison")
st.pyplot(fig2)

st.divider()

# Summary
st.markdown("## Baggage Tracking Summary")

summary = {
    "Latest Scan Status": scan_status,
    "Connections": connections,
    "Transfer Complexity": airport_transfer_complexity,
    "Delay Minutes": flight_delay_minutes,
    "International Transfer": international_transfer,
    "Overall Status": bag_status
}

summary_df = pd.DataFrame(list(summary.items()), columns=["Category", "Value"])
st.table(summary_df)

st.caption(
    "Disclaimer: BagTrace is a prototype concept for demonstration purposes only. "
    "It does not use live airline baggage handling or operational data."
)
