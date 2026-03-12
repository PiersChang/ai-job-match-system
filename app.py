# 匯入必要套件
import os
import re
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, AuthenticationError, APIError

# 本機開發時讀取 .env
load_dotenv()

# 先從 Streamlit secrets 取值，沒有再回退到本機 .env
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# 建立 OpenAI client
client = OpenAI(api_key=api_key)

# 設定 Streamlit 網頁基本資訊
st.set_page_config(
    page_title="AI Job Match System",  # 網頁標題
    layout="wide"                      # 使用寬版畫面
)

st.caption("AI-powered resume and job description matching system")

# 顯示標題
st.title("AI Job Match System")

# 顯示說明文字
st.write("Analyze resume content against a job description.")

# 建立左右兩個欄位
col1, col2 = st.columns(2)

# 左邊欄位：履歷輸入
with col1:
    resume_text = st.text_area(
        "Resume Content",              # 輸入框標題
        height=300,                    # 輸入框高度
        placeholder="Paste your resume here..."
    )

# 右邊欄位：職缺描述輸入
with col2:
    job_text = st.text_area(
        "Job Description",
        height=300,
        placeholder="Paste the job description here..."
    )

# 建立按鈕
st.info("Paste your resume and job description, then click Analyze Match.")
if st.button("Analyze Match"):

    # 如果其中一個欄位沒有填寫
    if not resume_text or not job_text:
        st.warning("Please fill in both fields.")

    else:
        try:
            # 顯示處理中動畫
            with st.spinner("AI is analyzing the resume..."):

                # 建立提示詞（Prompt）
                prompt = f"""
                        You are a professional career assistant.
                        
                        Please analyze the following resume and job description.
                        
                        Resume:
                        {resume_text}
                        
                        Job Description:
                        {job_text}
                        
                        Return the result in exactly this format:
                        
                        1. Resume Summary:
                        [your answer]
                        
                        2. Matching Skills:
                        - item 1
                        - item 2
                        
                        3. Missing Skills:
                        - item 1
                        - item 2
                        
                        4. Match Score: [integer between 0 and 100]
                        
                        5. Suggestions for Improvement:
                        - item 1
                        - item 2
                        """

                # 呼叫 OpenAI API
                response = client.chat.completions.create(

                    # 使用的模型
                    model="gpt-4o-mini",

                    # 對話內容
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful AI career assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    # 控制回答隨機性（越低越穩定）
                    temperature=0.3
                )

                # 取得 AI 回傳的文字內容
                result = response.choices[0].message.content 
                # 預設分數
                score = "N/A"
               # 從 AI 回傳結果中抓取 Match Score
                match = re.search(
                    r"Match Score(?:\s*\(0-100\))?\s*[:：]\s*(\d{1,3})%?",
                    result,
                    re.IGNORECASE
                )
                
                if match:
                    score = f"{match.group(1)}%"                
               # 顯示分數
                st.metric("Match Score", score)         

                # 顯示結果標題
                st.subheader("Analysis Result")

                # 分隔線
                st.divider()
                
                # 顯示 AI 回傳內容
                st.markdown(result)


        # API 使用額度不足
        except RateLimitError:
            st.error("API quota exceeded. Please check your OpenAI billing and usage.")

        # API KEY 錯誤
        except AuthenticationError:
            st.error("Invalid API key. Please check your .env file.")

        # OpenAI API 發生其他錯誤
        except APIError as e:
            st.error(f"OpenAI API error: {e}")

        # 其他未知錯誤
        except Exception as e:
            st.error(f"Unexpected error: {e}")