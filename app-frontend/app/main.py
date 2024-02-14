from datetime import datetime, timedelta
import uuid
import streamlit as st
import requests

import extra_streamlit_components as stx 

from schemas.user_session import UserSessionBodyResponse, UserSessionSchema
from schemas.subscriber import SubscriberCreate
from schemas.constants import NodeType, SubscribeType
from schemas.node import NodeMetricsSubscribedBody, NodesMetrics

from ui.display_nodes import display_nodes


def request_subscribe_node(node_id:uuid.UUID, subscriber_id:uuid.UUID):
    url = f"http://localhost:8000/api/v1/node/{node_id}/subscriber/{subscriber_id}"
    response = requests.post(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
def request_unsubscribe_node(node_id:uuid.UUID, subscriber_id:uuid.UUID):
    url = f"http://localhost:8000/api/v1/node/{node_id}/subscriber/{subscriber_id}"
    response = requests.delete(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


@st.cache_data 
def fetch_user_session(user_session_id: uuid.UUID) -> UserSessionBodyResponse | str | None:
    url = f"http://localhost:8000/api/v1/user-session?user_session_id={user_session_id}"
    response = requests.get(url)

    print(f"status: {response.status_code} - reponse: {response.json()}")

    if response.status_code == 200:
        return response.status_code, UserSessionBodyResponse.model_validate(response.json())
    elif response.status_code == 403:
        return response.status_code, response.json()["detail"]
    else:
        return response.status_code, None
    
def handle_user_session(session_id: uuid.UUID):
    status, data = fetch_user_session(session_id)
    if status == 200:
        return status, data
    
    st.cache_data.clear()
    return status, data

@st.cache_data(ttl=15)
def fetch_user_session_data(user_session_id: uuid.UUID) -> NodesMetrics:
    url = f"http://localhost:8000/api/v1/user-session-data?user_session_id={user_session_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return NodesMetrics.model_validate(response.json())
    else:
        return []

def register_user_session(subscriber_create: SubscriberCreate) -> UserSessionBodyResponse | None:
    url = "http://localhost:8000/api/v1/register-session"

    payload = subscriber_create.model_dump()
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return UserSessionBodyResponse.model_validate(response.json())
    else:
        return None

def filter_nodes(
        metrics: list[NodeMetricsSubscribedBody], node_type: NodeType=None, subscribed=False
    ) -> list[NodeMetricsSubscribedBody]:
    filtered = []
    for node in metrics:
        if search_query in node.last_metric.url.lower():
            if subscribed and node.subscribed:
                filtered.append(node)
            elif node_type and node.node_type == node_type:
                filtered.append(node)
    return filtered

def subscribe_node(node_id: uuid.UUID):
    subscriber_id = st.session_state['user_session'].subscriber_id
    result = request_subscribe_node(node_id, subscriber_id)

    if result is not None:
        st.cache_data.clear()
        st.toast("Node Unsubscribed")
        st.rerun()

def unsubscribe_node(node_id: uuid.UUID):
    subscriber_id = st.session_state['user_session'].subscriber_id
    print(subscriber_id)
    print
    result = request_unsubscribe_node(node_id, subscriber_id)

    if result is not None:
        st.cache_data.clear()
        st.toast("Node Unsubscribed")
        st.rerun()
     

#  ****************** MAIN *****************
    

cookie_manager = stx.CookieManager()
cookie_user_session_id = cookie_manager.get("user_session_id")

#print(cookie_manager.cookies)
user_session:UserSessionBodyResponse = None


if 'user_session' not in st.session_state:
    st.session_state['user_session'] = None
if 'user_session_status' not in st.session_state:
    st.session_state['user_session_status'] = 404

st.title('Aleph Community node tracker')

print(f"------------- cookie_user_session_id: {cookie_user_session_id}")
print(f"------------- user_session_id: {st.session_state['user_session']}")


if cookie_user_session_id:
    status, user_session = handle_user_session(cookie_user_session_id)
    if status == 403:

        st.info(user_session)

        if st.button("🔄", key="refresh"):
            st.rerun()

        st.session_state['user_session_status'] = 403
    else:
        st.session_state['user_session'] = user_session
        st.session_state['user_session_status'] = 200

if st.session_state['user_session'] is None:

    verify_mail_text = "Verify a new email" if st.session_state['user_session_status'] == 403 else "Enter your email"
    email = st.text_input(verify_mail_text, "")

    if st.button("Send verification link"):
        print("Button clicked, attempting to send verification email...")
        subscribe_create = SubscriberCreate(type=SubscribeType.EMAIL, value=email)
        user_session = register_user_session(subscribe_create)

        if user_session:
            expires_at = datetime.now() + timedelta(days=30)
            cookie_manager.set("user_session_id", str(
                user_session.session_id), secure=True, key="user_session_cookie", expires_at=expires_at)

            print(f"User session created: {user_session}")
        else:
            st.error("Unable to register session.")

 
user_session = st.session_state['user_session']
print(user_session)

if user_session:

    st.session_state['tab_selected'] = "ccn"

    email =  user_session.value
    print(st.session_state['user_session'])

    nodes_metrics = fetch_user_session_data(user_session.session_id)
    #print(nodes_metrics)

    if email:
        st.write(f"Weclome {email}")
    else:
        st.write("No email associated with this session.")

    st.write("---")

    search_col, pagination_col = st.columns([3, 1])
    tab_col, update_time_col = st.columns([3, 1])

    with search_col:
        search_query = st.text_input("Search node url keyword", "").lower()

    col1, col2 = st.columns([20, 2], gap="small")

    chosen_id = stx.tab_bar(data=[
        stx.TabBarItemData(id="ccn", title="🌐 CCN", description=""),
        stx.TabBarItemData(id="crn", title="💻 CRN", description=""),
        stx.TabBarItemData(id="subscribed", title="🌟 Subscribed", description="")
    ], default=st.session_state['tab_selected'])



    with col1:
        st.write(f"Last update: {nodes_metrics.updated_at}")

    with col2:
        if st.button("🔄", key="refresh"):
            st.rerun()

    


    st.session_state['tab_selected'] = chosen_id

    if chosen_id == "ccn":
        filtered_nodes = filter_nodes(nodes_metrics.metrics, NodeType.CCN)
        #print(filtered_nodes)
    elif chosen_id == "crn":
        filtered_nodes = filter_nodes(nodes_metrics.metrics, NodeType.CRN)
    else: 
        filtered_nodes = filter_nodes(nodes_metrics.metrics, subscribed=True)

    page_size = 20
    total_pages = max(1, len(filtered_nodes) // page_size + (len(filtered_nodes) % page_size > 0))
    with pagination_col:
        page_number = st.number_input(
            'Page Number', min_value=1, max_value=total_pages, value=1, step=1, key=f"page_{chosen_id}"
        )

    
    start_index = (page_number - 1) * page_size
    end_index = min(start_index + page_size, len(filtered_nodes))

    
    display_nodes(filtered_nodes, start_index, end_index, subscribe_node, unsubscribe_node)
    