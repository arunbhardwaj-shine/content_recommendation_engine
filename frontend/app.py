import streamlit as st
import requests

# -------------------------
# API BASE URL
# -------------------------

BASE_URL = "http://localhost:8000"

ALS_ENDPOINT = "/als/recommend/"
MARKOV_ENDPOINT = "/recommend/markov/"
SEMANTIC_ENDPOINT = "/recommend/content/"


# -------------------------
# PAGE CONFIG
# -------------------------

st.set_page_config(
    page_title="Recommendation Engine",
    page_icon="📚",
    layout="wide"
)

st.title("📚 PDF Recommendation Engine")

st.write("Enter a user email to get recommendations from 3 models.")

# -------------------------
# INPUT
# -------------------------

email = st.text_input("User Email")


# -------------------------
# API CALL
# -------------------------

def call_api(endpoint, email):

    url = f"{BASE_URL}{endpoint}{email}"

    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        st.error(f"API error: {e}")
        return None


# -------------------------
# RESULT DISPLAY
# -------------------------

def display_results(data):

    if not data:
        st.warning("No data returned")
        return

    based_pdf = data.get("based_on_pdf")

    if based_pdf:
        st.markdown(f"**Based on PDF:** `{based_pdf}`")

    recs = data.get("recommendations", [])

    if not recs:
        st.info("No recommendations")
        return

    cols = st.columns(len(recs))

    for i, rec in enumerate(recs):

        with cols[i]:

            st.markdown(
                f"""
                ### 📄 {rec.get('title')} (PDF {rec.get('pdf_id')})

                **Score:** {rec.get('score',0):.3f}

                🔗 [Open Document]({rec.get('docintel_url')})
                """
            )


# -------------------------
# TRIGGER
# -------------------------

if st.button("Get Recommendations"):

    if not email:
        st.warning("Please enter email")
        st.stop()

    with st.spinner("Running models..."):

        als = call_api(ALS_ENDPOINT, email)
        markov = call_api(MARKOV_ENDPOINT, email)
        semantic = call_api(SEMANTIC_ENDPOINT, email)

    tab1, tab2, tab3 = st.tabs(
        ["Semantic Model","ALS Model", "Markov Model"]
    )

    with tab1:
        display_results(semantic)
    with tab2:
        display_results(als)
    with tab3:
        display_results(markov)