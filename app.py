import streamlit as st
import requests

RENDER_API_URL = "https://assessment-recommendation-3w3r.onrender.com"

st.title("SHL Assessment Recommender")

query = st.text_area("Enter hiring query / job description")

if st.button("Get Recommendations"):
    if not query.strip():
        st.warning("Please enter a query")
    else:
        with st.spinner("Fetching recommendations..."):
            response = requests.post(
                f"{RENDER_API_URL}/recommend",
                json={"query": query},
                timeout=60
            )

        if response.status_code != 200:
            st.error("API error")
        else:
            data = response.json()
            results = data["recommendations"]

            for i, r in enumerate(results, 1):
                st.markdown(f"### {i}. {r['assessment_name']}")
                st.markdown(f"- **URL:** {r['assessment_url']}")
                st.markdown(f"- **Test Type:** {r['test_type']}")
                st.markdown(f"- **Duration:** {r['duration']}")
                st.markdown(f"- **Remote:** {r['remote_support']}")
                st.markdown(f"- **Adaptive:** {r['adaptive_support']}")
                st.markdown(f"- {r['description']}")
                st.divider()