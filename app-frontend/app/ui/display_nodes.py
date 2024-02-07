import streamlit as st
from datetime import datetime, timedelta
import uuid

from schemas.constants import NodeType
from schemas.node import NodeMetricsSubscribedBody


def truncate_and_hover(text, length=19):
    if text is None:
        text = ""  # or any placeholder text you prefer
    display_text = (text if len(text) <= length else text[:length-3] + '...')  # Truncate the text
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

    for index, node in enumerate(nodes[start:end], start=start):
        details_key = f"details_{index}"

        if details_key not in st.session_state:
            st.session_state[details_key] = False


        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 6, 1, 1, 2])

            with col1:
                status_color = "green" if node.last_metric.status else "red"
                st.markdown(f"<span style='color: {status_color};'>●</span>", unsafe_allow_html=True)

            with col2:
                st.markdown(truncate_and_hover(node.last_metric.version, 15), unsafe_allow_html=True)
            with col3:
                st.markdown(truncate_and_hover(node.last_metric.url, 37), unsafe_allow_html=True)
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


"""

def display_crn_nodes(data, start, end):
    for index, item in enumerate(data[start:end], start=start):
        expander_key = f'expand_state_{index}'
        subscribe_expander_key = f'subscribe_expander_{index}'
        unsubscribe_expander_key = f'unsubscribe_expander_{index}'

        if expander_key not in st.session_state:
            st.session_state[expander_key] = False

        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([1, 3, 6, 1, 1, 2])
            with col1:
                status_color = "green" if item['status'] else "red"
                st.markdown(f"<span style='color: {status_color};'>●</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(truncate_and_hover(item['version'], 15), unsafe_allow_html=True)
            with col3:
                st.markdown(truncate_and_hover(item['url'], 37), unsafe_allow_html=True)
            with col4:
                if st.button("📋", key=f'details_button_{index}'):
                    st.session_state[expander_key] = not st.session_state[expander_key]
            with col5:
                if st.button("🔔", key=f'subscribe_button_{index}'):  # Emoji for subscribe
                    st.session_state[subscribe_expander_key] = not st.session_state.get(subscribe_expander_key, False)
            
            with col6:
                if st.button("🔕", key=f'unsubscribe_button_{index}'):  # Emoji for unsubscribe
                    st.session_state[unsubscribe_expander_key] = not st.session_state.get(unsubscribe_expander_key, False)

            if st.session_state.get(subscribe_expander_key, False):
                with st.expander("Subscribe", expanded=True):
                    email = st.text_input("Enter your email:", key=f'email_subscribe_{index}')
                    if st.button("Submit for Subscription", key=f'submit_subscribe_{index}'):
                        st.success(f"Email {email} subscribed successfully")

            if st.session_state.get(unsubscribe_expander_key, False):
                with st.expander("Unsubscribe", expanded=True):
                    email = st.text_input("Enter your email:", key=f'email_unsubscribe_{index}')
                    if st.button("Submit for Unsubscription", key=f'submit_unsubscribe_{index}'):
                        st.success(f"Email {email} unsubscribed successfully")

            if st.session_state[expander_key]:
                with st.expander("", expanded=True):
                    st.json(item)
"""


"""

if user_session:

    email =  user_session.value
    print(st.session_state['user_session'])

    nodes_metrics = fetch_user_session_data(user_session.session_id)

    if email:
        st.write(f"Weclome {email}")
    else:
        st.write("No email associated with this session.")

    st.write("---")

    search_col, pagination_col = st.columns([3, 1])

    # Search filter in the second row
    with search_col:
        search_query = st.text_input("Search node url keyword", "").lower()

    tabs = st.tabs(["Ccn", "Crn", "Subscribed"])  # Add as many tabs as needed

    if 'current_page_ccn' not in st.session_state:
        st.session_state['current_page_ccn'] = 1
    if 'current_page_crn' not in st.session_state:
        st.session_state['current_page_crn'] = 1
    if 'current_page_subscribed' not in st.session_state:
        st.session_state['current_page_subscribed'] = 1

    ccn = []
    crn = []
    subscribed = []
    for node in nodes_metrics.metrics:
        node_url = node.last_metric.url.lower()
        if search_query in node_url:
            if node.subscribed:
                subscribed.append(node)
            elif node.node_type == NodeType.CCN:
                ccn.append(node)
            elif node.node_type == NodeType.CRN:
                crn.append(node)


    page_size = 10
    
    total_pages = {
        "ccn": (len(ccn) // page_size) + (len(ccn) % page_size > 0),
        "crn": (len(crn) // page_size) + (len(crn) % page_size > 0),
        "subscribed": (len(subscribed) // page_size) + (len(subscribed) % page_size > 0),
    }

    page_number = st.number_input(
        'Page Number', 
        min_value=1, 
        max_value=1 if total_pages[tab] == 0 else total_pages[tab],
        value=st.session_state[current_page_key], 
        step=1, 
        key="pagination"
    )
    
    # Display nodes in each tab with pagination
    for i, tab in enumerate(["ccn", "crn", "subscribed"]):
        with tabs[i]:
            current_page_key = f'current_page_{tab}'
            nodes_list = locals()[f'{tab}']

            max_pages = total_pages[tab]
            if st.session_state[current_page_key] > max_pages:
                st.session_state[current_page_key] = 1 if max_pages == 0 else max_pages

            start_index = (st.session_state[current_page_key] - 1) * page_size
            end_index = min(start_index + page_size, len(nodes_list))
            
            # Display nodes for the current tab
            display_nodes(nodes_list, start_index, end_index)


"""