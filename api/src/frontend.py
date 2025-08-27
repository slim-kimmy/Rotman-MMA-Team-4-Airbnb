import streamlit as st
import sys
sys.path.append("..")
from PIL import Image
import io
import base64
import requests
import pandas as pd
import numpy as np
import importlib
from streamlit_card import card
from utils import db_utils as db
from utils import similarity_utils as sim
import streamlit.components.v1 as components
importlib.reload(sim)


# Set page configuration
st.set_page_config(page_title="Rotel", 
                   layout="wide",
                   page_icon="../data/images/logo.svg")

# Define session state variables to check if user is logged in or not
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
#if "saved_properties" not in st.session_state:
    #st.session_state.saved_properties = []


def show_user_sidebar():
    """
    Render the sidebar only for logged-in users.
    """
    # Check if user is logged in
    if st.session_state.auth_user is None:
        return
    # Fetch user details from the database
    user = dict(db.view_user(st.session_state.auth_user))
    # If user not found, reset auth_user
    if not user:
        st.session_state.auth_user = None
        return
    # Sidebar content for user profile and ads
    with st.sidebar:
        st.header("My Account")
        # If not in edit mode, show profile details as immutable
        if not st.session_state.edit_mode:
            # Profile details gotten from database
            with st.expander("Profile", expanded=True):
                st.write(f"**Name:** {user['name']}")
                st.write(f"**User Name:** {user['username']}")
                st.write(f"**Group size:** {user['group_size']}")
                st.write(f"**Preferred environment:** {user['preferred_env']}")
                st.write(f"**Budget:** {user['min_price']} to {user['max_price']}")
                st.caption(f"User ID: {user['user_id']} ")
            # Buttons to edit profile or logout
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Edit", use_container_width=True):
                    st.session_state.edit_mode = True
                    st.rerun()
            with c2:
                if st.button("Logout", use_container_width=True):
                    st.session_state.auth_user = None
                    st.session_state.edit_mode = False
                    st.rerun()
            st.divider()
            # API call to local image server to fetch ad image
            response = requests.get("http://localhost:8000/images/ads/3?n=280&m=400&format=png", timeout=6)
            # Checking response code before displaying
            if response.status_code == 200:
                # Convert to image and display
                img = Image.open(io.BytesIO(response.content))
                # Center the ad image in the sidebar
                col1, col2, col3 = st.columns(spec=[1,5,1])
                with col2:
                    st.image(img, caption="Sponsored")
            else:
                # Error handling
                st.error(f"Error {response.status_code}: {response.text}")
        # Case for user in edit mode
        else:
            # Title and form to edit profile details
            st.subheader("Edit profile")
            with st.form("edit_form_sidebar"):
                e_name = st.text_input("Full name", value=user["name"])
                e_group = st.number_input("Group size", min_value=1, step=1, value=int(user["group_size"]))
                e_env = st.text_input("Preferred environment", value=user.get("preferred_env", ""))
                e_min = st.number_input("Min nightly price", min_value=0.0, value=float(user["min_price"]), step=10.0)
                e_max = st.number_input("Max nightly price", min_value=0.0, value=float(user["max_price"]), step=10.0)
                # Buttons to save changes
                save = st.form_submit_button("Save changes", use_container_width=True)
            # Splitting for two columns for cancel and delete account
            c1, c2 = st.columns(2)
            if save:
                if e_min > e_max:
                    st.error("Min price cannot be greater than max price")
                else:
                    try:
                        db.edit_user(
                            username=user["username"],
                            name=e_name,
                            group_size=int(e_group),
                            preferred_env=e_env,
                            min_price=float(e_min),
                            max_price=float(e_max),
                        )
                        st.success("Profile updated")
                        st.session_state.edit_mode = False
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Update failed: {ex}")
            with c1:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.edit_mode = False
                    st.rerun()
            with c2:
                # Option to delete account which resets session state variables
                if st.button("Delete account", use_container_width=True):
                    db.delete_user(user["username"])
                    st.success("Account deleted")
                    st.session_state.auth_user = None
                    st.session_state.edit_mode = False
                    st.rerun()

# Convert svg into base64 then to data URI for embedding in HTML
with open("../data/images/logo.svg", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")
mime = "image/svg+xml"
data_uri = f"data:{mime};base64,{b64}"
st.markdown(
    f"""
    <style>
    @keyframes fadeIn {{
        from {{ opacity: .2; }}
        to {{ opacity: 1; }}
    }}

    @keyframes slideIn {{
        from {{ transform: translateX(-50px); opacity: 0; }}
        to {{ transform: translateX(0); opacity: 1; }}
    }}
    .slide-in {{
        animation: slideIn 1s ease-out;
    }}


    </style>
    <div class="slide-in" style="display: flex; align-items: center;">
        <img src="{data_uri}" width="80" style="margin-right: 10px;">
        <span style="font-size: 5em; font-weight: bold;">Rotel</span>
        <span style="font-size: 3em; font-weight: bold; margin-top: 10px;">&nbsp- AI Powered Vacationing</span>
    </div>
    """,
    unsafe_allow_html=True
)

if st.session_state.auth_user is None:
    mode = st.radio("Choose:", ["Join", "Login"])
    if mode == "Join":
        st.subheader("Create account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        name = st.text_input("Full name")
        group_size = st.number_input("Group size", 1, step=1)
        preferred_env = st.text_input("Preferred environment:")
        min_price = st.number_input("Min nightly price", 0.0, step=10.0)
        max_price = st.number_input("Max nightly price", 0.0, step=10.0)

        if st.button("Create account"):
            try:
                db.insert_user(username, password, name, int(group_size),
                                     preferred_env, float(min_price), float(max_price))

                st.success("Account created. Please login now.")
                st.balloons()
                st.session_state.auth_user = username
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.subheader("Login")
        log_user = st.text_input("Username", key="user_log")
        log_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            user_info = dict(db.view_user(log_user))
            if user_info:
                if log_pass == user_info['password']:
                    st.session_state.auth_user = log_user
                    st.balloons()
                    st.success(f"Logged in as {log_user}")
                    st.rerun()
                else:
                    st.error("Wrong password.")
            else:
                st.error("User not exist. Please join first.")

else:
    show_user_sidebar()
    query_text = st.text_input("Enter your search query:", icon=":material/search:")
    user_info = dict(db.view_user(st.session_state.auth_user))
    if st.button("Search"):
        results = sim.similarity_search(
            user_info["preferred_env"],
            query_text,
            user_info["max_price"],
            user_info["min_price"],
            user_info["group_size"],
        )
        if not results:
            st.info("No matches found.")
        else:
            rank = 0
            for r in results:
                with st.container(border= True, height=400, gap="small"):
                    col1, col2, = st.columns(2)
                    rank += 1
                    r = dict(r)
                    with col1:
                        st.markdown(f" ### Top {rank}")
                        if r.get("page_content"):
                            st.write(r["page_content"])
                        if r.get("metadata"):
                            tags = r.get("metadata")
                            st.write("Tags: " + ", ".join(map(str, tags["tags"])))
                            st.write("Features: " + ", ".join(map(str, tags["features"])))
                            st.write("Size: " + str(tags["group size"]))
                            st.write("Property ID: " + str(tags["property_id"]))
                            image_id = tags.get("property_id")
                    with col2:
                        if image_id:
                            try:
                                folder_id = image_id
                                # fetch all PNGs in the folder as data-URIs
                                resp = requests.get(f"http://localhost:8000/images/{folder_id}?n=400&m=400", timeout=6)
                                data = resp.json()
                                uris = [item["data_uri"] for item in data.get("images", [])]

                                # Build slides dynamically from uris
                                slides = "".join(
                                    [f'<div class="swiper-slide" style="; border-radius: 10px 10px 10px 10px;"><img src="{u}" style="width:100%; margin-top: 40px"/></div>' for u in uris]
                                )

                                html_code = f"""
                                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.css"/>
                                <script src="https://cdn.jsdelivr.net/npm/swiper/swiper-bundle.min.js"></script>

                                <div class="swiper" style="width:400px; height:300px">
                                <div class="swiper-wrapper">
                                    {slides}
                                </div>
                                <div class="swiper-pagination"></div>
                                <div class="swiper-button-prev"></div>
                                <div class="swiper-button-next"></div>
                                </div>

                                <script>
                                var swiper = new Swiper('.swiper', {{
                                loop: true,
                                pagination: {{el: '.swiper-pagination'}},
                                navigation: {{nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev'}},
                                }});
                                </script>
                                """
                                components.html(html_code, height=350)
                            except Exception as e:
                                st.error(f"Error loading images: {e}")