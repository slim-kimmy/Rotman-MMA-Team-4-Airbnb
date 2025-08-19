import streamlit as st
import sys
sys.path.append("..")
import pandas as pd
import numpy as np
import importlib
from utils import db_utils as db
from utils import similarity_utils as sim
importlib.reload(sim)

if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "saved_properties" not in st.session_state:
    st.session_state.saved_properties = []

def show_user_sidebar():
    """Render the sidebar only for logged-in users."""
    if st.session_state.auth_user is None:
        return

    user = dict(db.view_user(st.session_state.auth_user))
    if not user:
        st.session_state.auth_user = None
        return

    with st.sidebar:
        st.header("My Account")

        if not st.session_state.edit_mode:
            with st.expander("Profile", expanded=True):
                st.write(f"**Name:** {user['name']}")
                st.write(f"**User Name:** {user['username']}")
                st.write(f"**Group size:** {user['group_size']}")
                st.write(f"**Preferred environment:** {user['preferred_env']}")
                st.write(f"**Budget:** {user['min_price']} to {user['max_price']}")
                st.caption(f"User ID: {user['user_id']} ")

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

        else:
            st.subheader("Edit profile")
            with st.form("edit_form_sidebar"):
                e_name = st.text_input("Full name", value=user["name"])
                e_group = st.number_input("Group size", min_value=1, step=1, value=int(user["group_size"]))
                e_env = st.text_input("Preferred environment", value=user.get("preferred_env", ""))
                e_min = st.number_input("Min nightly price", min_value=0.0, value=float(user["min_price"]), step=10.0)
                e_max = st.number_input("Max nightly price", min_value=0.0, value=float(user["max_price"]), step=10.0)

                save = st.form_submit_button("Save changes", use_container_width=True)

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
                if st.button("Delete account", use_container_width=True):
                    conn = db.get_db_connection()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM users WHERE username = ?", (user["username"],))
                    conn.commit()
                    conn.close()
                    st.success("Account deleted")
                    st.session_state.auth_user = None
                    st.session_state.edit_mode = False
                    st.rerun()

st.title("Summer Home Recommender")


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
                    st.success(f"Logged in as {log_user}")
                    st.balloons()
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
            user_info["min_price"]
        )
        if not results:
            st.info("No matches found.")
        else:
            result_df = pd.DataFrame(results)
            key_cols = ["property_id", "location", "type", "price_per_night", "capacity"]
            cols_to_show = [c for c in key_cols if c in result_df.columns]
            st.dataframe(result_df[cols_to_show] if cols_to_show else result_df, use_container_width=True)


            st.subheader("Details")
            for r in results:
                title = f"#{r.get('property_id')} • {r.get('location')} • ${r.get('price_per_night')}/night"
                with st.expander(title, expanded=False):
                    if r.get("description"):
                        st.write(r["description"])
                    if r.get("tags"):
                        st.write("Tags: " + ", ".join(map(str, r["tags"])))
                    if r.get("features"):
                        st.write("Features: " + ", ".join(map(str, r["features"])))
                    st.write(f"Type: {r.get('type', '')}")
                    if "capacity" in r:
                        st.write(f"Capacity: {r['capacity']}")



