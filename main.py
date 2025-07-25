import streamlit as st
import pandas as pd
from backend.groq_api import ask_groq
from backend.codeexecutor import execute_code
from backend.sqlquery import run_sql_query
from utils.helpers import show_stats, is_numeric_query

st.set_page_config(page_title="CSV Chatbot 📊", layout="wide")
st.title("🤖 Chat with your CSV!")
st.caption("Upload a CSV and ask any question about it. The AI will answer using charts, Python or SQL.")

st.sidebar.header("Upload Your CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("📄 Data Preview")
    st.dataframe(df, use_container_width=True)

    show_stats(df)

    st.subheader("💬 Ask a Question")
    user_query = st.text_input("What would you like to know?", placeholder="e.g. What is the average age of passengers?")

    if user_query:
        df_sample = df.head(10).to_csv(index=False)
        try:
            # 🔮 Main call to Groq LLM with sample data
            response, fig, tokens = ask_groq(user_query, df_sample)

            st.success("✅ Answer:")
            st.write(response)
            st.info(f"🔢 Tokens used: {tokens}")

            # 📊 Chart from model (e.g. Plotly object)
            if fig is not None:
                st.subheader("📊 Auto-Generated Chart")
                st.plotly_chart(fig, use_container_width=True)

            # 🧠 Python code block from model
            elif "```python" in response:
                try:
                    code = response.split("```python")[1].split("```")[0]
                    st.code(code, language="python")
                    output, image_bytes = execute_code(code, df)
                    if "⚠️ Error" in output:
                        st.error("❌ Error running code:")
                        st.text(output)
                    else:
                        st.success("✅ Output:")
                        st.text(output)
                        if image_bytes:
                            st.image(image_bytes, caption="📈 Auto-generated Chart")
                except Exception as e:
                    st.error(f"❌ Failed to extract or execute code: {e}")

            # 🧮 If it's a numeric/statistical query but no chart/code was returned
            elif is_numeric_query(user_query):
                try:
                    sql_result = run_sql_query(user_query, df)
                    st.success("✅ SQL Result:")
                    st.dataframe(sql_result)
                except Exception as e:
                    st.warning("🔍 No chart/code/SQL result found. Try asking differently.")
                    st.error(e)

            # 🟪 Fallback for graph-type queries
            elif any(k in user_query.lower() for k in ["graph", "plot", "chart"]):
                st.subheader("📊 Try generating a manual graph below if needed")

                graph_type = st.selectbox("Choose a graph type", ["Line", "Bar", "Pie", "Histogram", "Scatter"])
                x_axis = st.selectbox("X-axis", df.columns)
                y_axis = st.selectbox("Y-axis", df.columns)

                if st.button("📈 Generate Chart"):
                    try:
                        import matplotlib.pyplot as plt
                        import seaborn as sns

                        fig, ax = plt.subplots()
                        if graph_type == "Line":
                            sns.lineplot(x=df[x_axis], y=df[y_axis], ax=ax)
                        elif graph_type == "Bar":
                            sns.barplot(x=df[x_axis], y=df[y_axis], ax=ax)
                        elif graph_type == "Pie":
                            df_grouped = df.groupby(x_axis)[y_axis].sum()
                            ax.pie(df_grouped, labels=df_grouped.index, autopct='%1.1f%%')
                            ax.axis('equal')
                        elif graph_type == "Histogram":
                            sns.histplot(df[y_axis], ax=ax, bins=20)
                        elif graph_type == "Scatter":
                            sns.scatterplot(x=df[x_axis], y=df[y_axis], ax=ax)

                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Failed to plot chart: {e}")

            else:
                st.warning("🤖 No chart, code, or SQL result found. Try rephrasing your question.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

else:
    st.info("⬅️ Upload a CSV file from the sidebar to get started.")
