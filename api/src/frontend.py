import streamlit as st


if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

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
                db_utils.insert_user(username, password, name, int(group_size),
                                     preferred_env, float(min_price), float(max_price))
                st.balloons()
                st.success("Account created.")
            except Exception as e:
                st.error(f"Error: {e}")

    else:
        st.subheader("Login")
        log_user = st.text_input("Username", key="user_log")
        log_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if validate_login(log_user, log_pass):
                st.session_state.auth_user = log_user
                st.balloons()
                st.success(f"Logged in as {log_user}")
            else:
                st.error("Invalid login")
