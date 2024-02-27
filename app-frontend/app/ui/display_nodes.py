import streamlit as st
from datetime import datetime, timedelta
import uuid

from schemas.constants import NodeType
from schemas.node import NodeMetricsSubscribedBody


def truncate_and_hover(text, length=19):
    if text is None:
        text = ""
    display_text = (text if len(text) <= length else text[:length-3] + '...')
    return f"<span title='{text}' style='cursor: pointer;'>{display_text}</span>"



def display_nodes(
        nodes: list[NodeMetricsSubscribedBody],
        start: int, 
        end: int,
        subscribe_callback,
        unsubscribe_callback
    ):

    if 'last_opened_details' not in st.session_state:
        st.session_state['last_opened_details'] = None

    min_height_style = """
    <style>
    .div-height {
        min-height: 35px;
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    </style>
    """

    st.markdown(min_height_style, unsafe_allow_html=True)

    for index, node in enumerate(nodes[start:end], start=start):
        details_key = f"details_{index}"

        if details_key not in st.session_state:
            st.session_state[details_key] = False

        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([1, 3, 6, 1, 1])

            with col1:
                status_color = "green" if node.last_metric.status else "red"
                st.markdown(f"<div class='div-height'><span style='color: {status_color}; font-size: 22px;'>●</span></div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"<div class='div-height'>{truncate_and_hover(node.last_metric.version, 15)}</div>", unsafe_allow_html=True)

            with col3:
                st.markdown(f"<div class='div-height'><a href='{node.last_metric.url}' target='_blank'>{truncate_and_hover(node.last_metric.url, 37)}</a></div>", unsafe_allow_html=True)
            with col4:
                if st.button("📋", key=f'details_button_{index}'):
                    current_state = st.session_state[details_key]
                    if st.session_state['last_opened_details'] is not None and st.session_state['last_opened_details'] != details_key:
                        st.session_state[st.session_state['last_opened_details']] = False
                    st.session_state[details_key] = not current_state
                    if not current_state:
                        st.session_state['last_opened_details'] = details_key
                    else:
                        st.session_state['last_opened_details'] = None

            if node.subscribed:
                with col5:
                    if st.button("🔕", key=f'unsubscribe_button_{index}'):
                        unsubscribe_callback(node.node_id)
            else:
                with col5:
                    if st.button("🔔", key=f'subscribe_button_{index}'):
                        subscribe_callback(node.node_id)
            
            if st.session_state[details_key]:
                with st.container(border=True):
                    if node.node_type == NodeType.CCN:
                        st.json({
                                "id":node.aleph_node_id,
                                "asn":node.last_metric.asn,
                                "url":node.last_metric.url,
                                "as_name":node.last_metric.as_name,
                                "version":node.last_metric.version,
                                "txs_total":node.last_metric.txs_total,
                                "measured_at":node.last_metric.measured_at,
                                "measured_at_formatted":node.last_metric.measured_at_formatted,
                                "base_latency":node.last_metric.base_latency,
                                "metrics_latency":node.last_metric.metrics_latency,
                                "pending_messages":node.last_metric.pending_messages,
                                "aggregate_latency":node.last_metric.aggregate_latency,
                                "base_latency_ipv4":node.last_metric.base_latency_ipv4,
                                "eth_height_remaining":node.last_metric.eth_height_remaining,
                                "file_download_latency":node.last_metric.file_download_latency,
                            }
                        )
        
                    elif node.node_type == NodeType.CRN:
                        st.json({
                                    "id":node.aleph_node_id,
                                    "asn":node.last_metric.asn,
                                    "url":node.last_metric.url,
                                    "as_name":node.last_metric.as_name,
                                    "version":node.last_metric.version,
                                    "measured_at":node.last_metric.measured_at,
                                    "measured_at_formatted":node.last_metric.measured_at_formatted,
                                    "base_latency":node.last_metric.base_latency,
                                    "base_latency_ipv4":node.last_metric.base_latency_ipv4,
                                    "full_check_latency":node.last_metric.full_check_latency,
                                    "diagnostic_vm_latency":node.last_metric.diagnostic_vm_latency,
                                }
                        )
