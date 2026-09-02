import streamlit as st

from database import (
    init_db,
    create_user,
    login_user,
    create_post,
    get_posts,
    toggle_like,
    get_like_count,
    user_liked,
    add_comment,
    get_comments,
    create_group,
    get_groups,
    join_group,
    get_user_groups,
    add_message,
    get_messages,
)


# ==========================================
# INSTÄLLNINGAR
# ==========================================

st.set_page_config(
    page_title="SocialApp",
    page_icon="💬",
    layout="centered"
)

# Starta databasen
init_db()


# ==========================================
# SESSION
# ==========================================

if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "Flöde"

if "selected_group" not in st.session_state:
    st.session_state.selected_group = None


# ==========================================
# CSS / DESIGN
# ==========================================

st.markdown(
    """
    <style>

    .main {
        max-width: 850px;
        margin: auto;
    }

    .post {
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #dddddd;
        margin-bottom: 20px;
        background-color: white;
    }

    .username {
        font-weight: bold;
        font-size: 18px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# LOGIN
# ==========================================

def login_page():

    st.title("📱 SocialApp")

    st.write("Välkommen! Logga in eller skapa ett konto.")

    login_tab, register_tab = st.tabs(
        ["🔐 Logga in", "📝 Skapa konto"]
    )

    # --------------------------------------
    # LOGGA IN
    # --------------------------------------

    with login_tab:

        st.subheader("Logga in")

        username = st.text_input(
            "Användarnamn",
            key="login_username"
        )

        password = st.text_input(
            "Lösenord",
            type="password",
            key="login_password"
        )

        if st.button(
            "Logga in",
            use_container_width=True
        ):

            if not username or not password:

                st.error(
                    "Fyll i användarnamn och lösenord."
                )

            else:

                user = login_user(
                    username,
                    password
                )

                if user:

                    st.session_state.user = dict(user)
                    st.session_state.page = "Flöde"

                    st.success("Du är inloggad!")

                    st.rerun()

                else:

                    st.error(
                        "Fel användarnamn eller lösenord."
                    )

    # --------------------------------------
    # SKAPA KONTO
    # --------------------------------------

    with register_tab:

        st.subheader("Skapa konto")

        new_username = st.text_input(
            "Användarnamn",
            key="register_username"
        )

        new_password = st.text_input(
            "Lösenord",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Upprepa lösenord",
            type="password",
            key="register_confirm"
        )

        if st.button(
            "Skapa konto",
            use_container_width=True
        ):

            if not new_username or not new_password:

                st.error(
                    "Fyll i alla fält."
                )

            elif len(new_username) < 3:

                st.error(
                    "Användarnamnet måste vara minst 3 tecken."
                )

            elif len(new_password) < 6:

                st.error(
                    "Lösenordet måste vara minst 6 tecken."
                )

            elif new_password != confirm_password:

                st.error(
                    "Lösenorden matchar inte."
                )

            else:

                success = create_user(
                    new_username,
                    new_password
                )

                if success:

                    st.success(
                        "Kontot skapades! Du kan nu logga in."
                    )

                else:

                    st.error(
                        "Det användarnamnet används redan."
                    )


# ==========================================
# NYTT INLÄGG
# ==========================================

def create_post_page():

    st.header("✏️ Skapa inlägg")

    st.write(
        "Skriv något eller lägg till en bild."
    )

    text = st.text_area(
        "Text",
        placeholder="Vad tänker du på?"
    )

    image = st.file_uploader(
        "📷 Lägg till bild",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ]
    )

    if image:

        st.image(
            image,
            caption="Förhandsvisning",
            use_container_width=True
        )

    if st.button(
        "🚀 Publicera",
        use_container_width=True
    ):

        if not text.strip() and not image:

            st.warning(
                "Skriv något eller lägg till en bild."
            )

            return

        image_data = None

        if image:
            image_data = image.getvalue()

        create_post(
            st.session_state.user["id"],
            text.strip(),
            image_data
        )

        st.success(
            "Inlägget publicerades!"
        )

        st.session_state.page = "Flöde"

        st.rerun()


# ==========================================
# HUVUDFLÖDE
# ==========================================

def feed_page():

    st.header("🏠 Huvudflöde")

    posts = get_posts()

    if not posts:

        st.info(
            "Det finns inga inlägg ännu. "
            "Bli den första att publicera något!"
        )

        return

    for post in posts:

        st.markdown(
            f"### 👤 {post['username']}"
        )

        if post["text"]:

            st.write(
                post["text"]
            )

        if post["image"]:

            st.image(
                post["image"],
                use_container_width=True
            )

        # ----------------------------------
        # LIKE
        # ----------------------------------

        liked = user_liked(
            post["id"],
            st.session_state.user["id"]
        )

        like_count = get_like_count(
            post["id"]
        )

        if liked:

            button_text = (
                f"❤️ Gillar ({like_count})"
            )

        else:

            button_text = (
                f"🤍 Gilla ({like_count})"
            )

        if st.button(
            button_text,
            key=f"like_{post['id']}"
        ):

            toggle_like(
                post["id"],
                st.session_state.user["id"]
            )

            st.rerun()

        # ----------------------------------
        # KOMMENTARER
        # ----------------------------------

        comments = get_comments(
            post["id"]
        )

        with st.expander(
            f"💬 Kommentarer ({len(comments)})"
        ):

            if comments:

                for comment in comments:

                    st.markdown(
                        f"**{comment['username']}**: "
                        f"{comment['text']}"
                    )

            else:

                st.write(
                    "Inga kommentarer ännu."
                )

            comment_text = st.text_input(
                "Skriv en kommentar...",
                key=f"comment_{post['id']}"
            )

            if st.button(
                "Kommentera",
                key=f"comment_button_{post['id']}"
            ):

                if comment_text.strip():

                    add_comment(
                        post["id"],
                        st.session_state.user["id"],
                        comment_text.strip()
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Skriv en kommentar först."
                    )

        st.divider()


# ==========================================
# GRUPPER
# ==========================================

def groups_page():

    st.header("👥 Grupper")

    my_groups_tab, create_tab, join_tab = st.tabs(
        [
            "👥 Mina grupper",
            "➕ Skapa grupp",
            "🔑 Gå med"
        ]
    )

    # ======================================
    # MINA GRUPPER
    # ======================================

    with my_groups_tab:

        my_groups = get_user_groups(
            st.session_state.user["id"]
        )

        if not my_groups:

            st.info(
                "Du är inte med i någon grupp ännu."
            )

        else:

            for group in my_groups:

                st.subheader(
                    f"👥 {group['name']}"
                )

                if group["description"]:

                    st.write(
                        group["description"]
                    )

                if st.button(
                    "💬 Öppna grupp",
                    key=f"open_group_{group['id']}",
                    use_container_width=True
                ):

                    st.session_state.selected_group = (
                        group["id"]
                    )

                    st.session_state.page = "Grupp"

                    st.rerun()

    # ======================================
    # SKAPA GRUPP
    # ======================================

    with create_tab:

        st.subheader(
            "➕ Skapa en ny grupp"
        )

        group_name = st.text_input(
            "Gruppnamn"
        )

        group_description = st.text_area(
            "Beskrivning",
            placeholder="Vad handlar gruppen om?"
        )

        group_code = st.text_input(
            "4-siffrig kod",
            max_chars=4,
            placeholder="1234"
        )

        st.caption(
            "Personer behöver denna kod för att gå med i gruppen."
        )

        if st.button(
            "Skapa grupp",
            use_container_width=True
        ):

            if not group_name.strip():

                st.error(
                    "Skriv ett gruppnamn."
                )

            elif not group_code.isdigit():

                st.error(
                    "Gruppkoden får bara innehålla siffror."
                )

            elif len(group_code) != 4:

                st.error(
                    "Gruppkoden måste vara exakt 4 siffror."
                )

            else:

                create_group(
                    group_name.strip(),
                    group_description.strip(),
                    group_code,
                    st.session_state.user["id"]
                )

                st.success(
                    "Gruppen skapades!"
                )

                st.rerun()

    # ======================================
    # GÅ MED I GRUPP
    # ======================================

    with join_tab:

        st.subheader(
            "🔑 Gå med i en grupp"
        )

        all_groups = get_groups()

        if not all_groups:

            st.info(
                "Det finns inga grupper ännu."
            )

        else:

            for group in all_groups:

                st.markdown(
                    f"### 👥 {group['name']}"
                )

                if group["description"]:

                    st.write(
                        group["description"]
                    )

                st.caption(
                    f"Skapad av: {group['owner']}"
                )

                code = st.text_input(
                    "Gruppkod",
                    max_chars=4,
                    key=f"join_code_{group['id']}"
                )

                if st.button(
                    "Gå med",
                    key=f"join_{group['id']}",
                    use_container_width=True
                ):

                    success, message = join_group(
                        group["id"],
                        st.session_state.user["id"],
                        code
                    )

                    if success:

                        st.success(message)

                        st.rerun()

                    else:

                        st.error(message)

                st.divider()


# ==========================================
# GRUPP + CHATT
# ==========================================

def group_page():

    group_id = st.session_state.selected_group

    if not group_id:

        st.error(
            "Ingen grupp är vald."
        )

        return

    # --------------------------------------
    # HÄMTA ANVÄNDARENS GRUPPER
    # --------------------------------------

    groups = get_user_groups(
        st.session_state.user["id"]
    )

    group = None

    for current_group in groups:

        if current_group["id"] == group_id:

            group = current_group

            break

    if group is None:

        st.error(
            "Du har inte tillgång till den här gruppen."
        )

        return

    # --------------------------------------
    # HEADER
    # --------------------------------------

    if st.button("⬅️ Tillbaka till grupper"):

        st.session_state.page = "Grupper"

        st.rerun()

    st.header(
        f"👥 {group['name']}"
    )

    if group["description"]:

        st.write(
            group["description"]
        )

    st.divider()

    # --------------------------------------
    # CHAT
    # --------------------------------------

    st.subheader("💬 Gruppchatt")

    messages = get_messages(
        group_id
    )

    if not messages:

        st.info(
            "Inga meddelanden ännu. "
            "Skriv det första!"
        )

    else:

        for message in messages:

            st.markdown(
                f"**{message['username']}**"
            )

            st.write(
                message["text"]
            )

            st.caption(
                message["created_at"]
            )

            st.divider()

    # --------------------------------------
    # SKICKA MEDDELANDE
    # --------------------------------------

    message = st.chat_input(
        "Skriv ett meddelande..."
    )

    if message:

        if message.strip():

            add_message(
                group_id,
                st.session_state.user["id"],
                message.strip()
            )

            st.rerun()


# ==========================================
# HUVUDPROGRAM
# ==========================================

if st.session_state.user is None:

    login_page()

else:

    # ======================================
    # SIDEBAR
    # ======================================

    with st.sidebar:

        st.title("📱 SocialApp")

        st.write(
            f"👤 {st.session_state.user['username']}"
        )

        st.divider()

        if st.button(
            "🏠 Huvudflöde",
            use_container_width=True
        ):

            st.session_state.page = "Flöde"

            st.rerun()

        if st.button(
            "✏️ Skapa inlägg",
            use_container_width=True
        ):

            st.session_state.page = "Skapa"

            st.rerun()

        if st.button(
            "👥 Grupper",
            use_container_width=True
        ):

            st.session_state.page = "Grupper"

            st.rerun()

        st.divider()

        if st.button(
            "🚪 Logga ut",
            use_container_width=True
        ):

            st.session_state.user = None

            st.session_state.page = "Flöde"

            st.session_state.selected_group = None

            st.rerun()

    # ======================================
    # VISA RÄTT SIDA
    # ======================================

    if st.session_state.page == "Flöde":

        feed_page()

    elif st.session_state.page == "Skapa":

        create_post_page()

    elif st.session_state.page == "Grupper":

        groups_page()

    elif st.session_state.page == "Grupp":

        group_page()
