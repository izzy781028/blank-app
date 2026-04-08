import streamlit as st

# ==================== 1. 網頁基本設定 ====================
st.set_page_config(layout="wide", page_title="AE 提案圖生成器")

# ==================== 2. 簡易密碼鎖設定 ====================
# 🔒 設定你們團隊的通關密碼 (可以在引號內修改)
TEAM_PASSWORD = "52654260" 

# 檢查使用者是否已經登入過
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# 如果還沒登入，顯示輸入密碼的畫面
if not st.session_state.authenticated:
    st.title("🔒 內部測試工具：請輸入通關密碼")
    st.write("這是一個內部使用的 AI 提案圖生成器，請輸入密碼以進入。")
    
    pwd_input = st.text_input("輸入密碼後按 Enter", type="password")
    
    if pwd_input == TEAM_PASSWORD:
        st.session_state.authenticated = True
        st.rerun() # 密碼正確，重新載入畫面
    elif pwd_input != "":
        st.error("❌ 密碼錯誤，請重新輸入！")
        
    st.stop() # 停止執行下方的程式碼，直到密碼正確為止

# ==================== 3. 字典定義區 (中翻英對應表) ====================
# (如果你看到這裡，代表密碼輸入正確了，開始載入主程式！)

dict_style = {"寫實商業攝影": "realistic commercial photography, highly detailed, photorealistic", "高級精品感": "high-end luxury aesthetic, sleek, editorial fashion photography", "科技未來感": "cyberpunk, sci-fi futuristic, glowing neon aesthetics", "溫暖生活感": "warm lifestyle photography, cozy atmosphere, candid", "年輕潮流感": "youthful trendy vibe, streetwear aesthetics, dynamic", "日系清透": "Japanese clear aesthetic, soft airy vibe, muted pastel colors", "歐美廣告劇照": "cinematic commercial still, dramatic movie aesthetic, 35mm film", "插畫風": "digital illustration, vector art style, flat design", "3D 視覺風": "3D render, Octane render, Unreal Engine 5, Pixar style"}
dict_shot = {"極特寫": "extreme close-up shot, macro photography", "特寫": "close-up shot", "半身": "medium shot, waist up", "膝上景": "cowboy shot, knee up shot", "全身景": "full body shot", "遠景": "wide shot, long shot"}
dict_angle = {"平視": "eye-level shot", "仰視": "low angle shot", "俯視": "high angle shot", "傾斜荷蘭角": "Dutch angle, tilted frame"}
dict_relation = {"直視鏡頭 (Looking at Camera)": "looking directly at viewer", "過肩鏡頭": "over the shoulder shot, OTS", "第一人稱視角": "first-person view, POV", "旁觀者/側面視角": "profile shot, side view", "背後跟隨視角": "shot from behind, back view"}
dict_light = {"白天自然光": "bright natural sunlight", "黃昏日落暖光 (Magic hour)": "golden hour lighting", "夜晚": "night time, ambient night lighting", "棚拍柔光": "soft studio lighting, softbox", "高反差戲劇光": "dramatic high contrast lighting, chiaroscuro", "冷色科技光": "cool color palette, blue and teal lighting"}


# ==================== 4. UI 介面設計 ====================

st.title("🚀 業務提案概念圖生成器")
st.write("精準控制畫面分鏡，一鍵生成高品質提案圖。對應 Nano Banana 2 引擎。")

# 【第一區：核心內容】(3 欄：主角、動作、場景)
st.subheader("1. 畫面核心內容 (Who, Doing What, Where)")
col_text1, col_text2, col_text3 = st.columns(3)

with col_text1:
    user_keyword = st.text_input("📦 畫面主角 (Who) *必填", "一位穿白襯衫的年輕女性")

with col_text2:
    user_action = st.text_input("🏃‍♂️ 主角動作 (Doing What)", "手裡拿著咖啡，燦爛微笑", 
                                help="非必填。若主角是產品，可填寫狀態(如: 漂浮在半空中)，或保持空白。")

with col_text3:
    user_background = st.text_input("🖼️ 背景場景 (Where) *必填", "陽光明媚的現代咖啡廳")

st.divider() # 分隔線

# 【第二區：專業參數設定】(下拉式選單)
st.subheader("2. 攝影與風格控制")
col1, col2, col3 = st.columns(3)

with col1:
    style_choice = st.selectbox("✨ 視覺風格", list(dict_style.keys()))
    light_choice = st.selectbox("💡 光線與色調", list(dict_light.keys()))

with col2:
    shot_choice = st.selectbox("🔲 鏡頭大小", list(dict_shot.keys()))
    angle_choice = st.selectbox("📐 鏡頭角度", list(dict_angle.keys()))

with col3:
    relation_choice = st.selectbox("👁️ 鏡頭互動關係", list(dict_relation.keys()))
    ratio_choice = st.selectbox("📏 提案畫面比例", ["橫式簡報滿版 (16:9)", "IG限動 (9:16)", "方形 (1:1)"])

st.divider() # 分隔線

# ==================== 5. 產圖邏輯區 ====================

# 按下按鈕後執行的動作
if st.button("🪄 組合咒語並生成圖片", type="primary", use_container_width=True):
    
    # 防呆檢查：確保主角和背景有填寫
    if user_keyword.strip() == "" or user_background.strip() == "":
        st.error("⚠️ 請至少填寫「畫面主角」與「背景場景」！")
    else:
        # 1. 處理動作欄位：判斷是否有填寫動作
        if user_action.strip() != "":
            subject_and_action = f"{user_keyword} {user_action}" 
        else:
            subject_and_action = f"{user_keyword}"

        # 2. 依照最佳權重順序組合最終 Prompt
        # 組合公式：[風格], [鏡頭大小], [鏡頭角度], [主角+動作], [鏡頭關係], in [背景場景], [光線設定]
        final_prompt = (
            f"{dict_style[style_choice]}, "
            f"{dict_shot[shot_choice]}, "
            f"{dict_angle[angle_choice]}, "
            f"{subject_and_action}, "
            f"{dict_relation[relation_choice]}, "
            f"in {user_background}, "
            f"{dict_light[light_choice]}"
        )
        
        # 3. 在畫面上顯示成功的訊息與組合出來的 Prompt
        st.success("✅ 成功生成提示詞 (Prompt)！準備送出至 Nano Banana 2")
        st.code(final_prompt, language="text")
        
        # 4. 畫面比例轉換邏輯 (為 API 準備)
        width, height = 1920, 1080 # 預設 16:9
        if "9:16" in ratio_choice:
            width, height = 1080, 1920
        elif "1:1" in ratio_choice:
            width, height = 1024, 1024
            
        st.info(f"⚙️ 預計傳送給 API 的尺寸參數：寬度 {width}px, 高度 {height}px")
        
        # 💡 未來串接 API 的預留位：
        # 這裡未來可以寫 requests.post(...) 把 final_prompt 跟尺寸送到 Nano Banana 2 API